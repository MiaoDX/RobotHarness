"""ONNX-based locomotion controllers for humanoid robots.

Provides RL-trained locomotion policies (Balance + Walk) that output
joint position targets from proprioceptive observations. The ONNX models
are downloaded from HuggingFace on first use and cached locally.

Currently supported controllers:
  - GR00T: Balance + Walk dual-policy from NVlabs GR00T-WholeBodyControl
  - Holosoma: PPO/FastSAC policy from Amazon (planned)

These controllers implement the ``Controller`` protocol and can be used
standalone with any MuJoCo model, without DDS or unitree_sdk2py.

Usage:
    from roboharness.controllers.locomotion import GrootLocomotionController

    ctrl = GrootLocomotionController()
    state = {"qpos": data.qpos, "qvel": data.qvel}
    action = ctrl.compute(command={"velocity": [0, 0, 0]}, state=state)
    data.ctrl[:15] = action  # lower body + waist joints

Reference implementation:
    huggingface.co/lerobot — src/lerobot/robots/unitree_g1/gr00t_locomotion.py
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# G1 joint configuration (29-DOF body)
# ---------------------------------------------------------------------------
# Joints 0-5: left leg (hip pitch/roll/yaw, knee, ankle pitch/roll)
# Joints 6-11: right leg (same)
# Joints 12-14: waist (yaw, roll, pitch)
# Joints 15-21: left arm (shoulder pitch/roll/yaw, elbow, wrist roll/pitch/yaw)
# Joints 22-28: right arm (same)

NUM_BODY_JOINTS = 29
NUM_LOWER_BODY_JOINTS = 15  # joints 0-14 (legs + waist), controlled by locomotion

# Default standing angles (radians) — slight knee bend for stability
GROOT_DEFAULT_ANGLES = np.zeros(NUM_BODY_JOINTS, dtype=np.float32)
GROOT_DEFAULT_ANGLES[0] = -0.1  # left hip pitch
GROOT_DEFAULT_ANGLES[6] = -0.1  # right hip pitch
GROOT_DEFAULT_ANGLES[3] = 0.3  # left knee
GROOT_DEFAULT_ANGLES[9] = 0.3  # right knee
GROOT_DEFAULT_ANGLES[4] = -0.2  # left ankle pitch
GROOT_DEFAULT_ANGLES[10] = -0.2  # right ankle pitch

# Scaling constants (from GR00T WBC training)
ACTION_SCALE = 0.25
ANG_VEL_SCALE = 0.25
DOF_POS_SCALE = 1.0
DOF_VEL_SCALE = 0.05
CMD_SCALE = np.array([2.0, 2.0, 0.25], dtype=np.float32)

# Observation frame: 86-dim per timestep, 6-frame history → 516-dim input
OBS_FRAME_DIM = 86
OBS_HISTORY_LEN = 6

# HuggingFace model source
GROOT_HF_REPO = "nepyope/GR00T-WholeBodyControl_g1"
GROOT_BALANCE_FILE = "GR00T-WholeBodyControl-Balance.onnx"
GROOT_WALK_FILE = "GR00T-WholeBodyControl-Walk.onnx"


def get_gravity_orientation(quaternion: np.ndarray) -> np.ndarray:
    """Compute gravity direction in body frame from quaternion [w, x, y, z]."""
    qw, qx, qy, qz = quaternion
    grav = np.zeros(3, dtype=np.float32)
    grav[0] = 2 * (-qz * qx + qw * qy)
    grav[1] = -2 * (qz * qy + qw * qx)
    grav[2] = 1 - 2 * (qw * qw + qz * qz)
    return grav


def _download_onnx(repo_id: str, filename: str) -> str:
    """Download an ONNX model from HuggingFace, returning the local path."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise ImportError(
            "huggingface_hub is required for locomotion controllers. "
            "Install with: pip install roboharness[lerobot]"
        ) from e
    path: str = hf_hub_download(repo_id=repo_id, filename=filename)
    return path


class GrootLocomotionController:
    """GR00T Balance + Walk locomotion controller via ONNX inference.

    Downloads pre-trained RL policies from HuggingFace and runs them at
    50 Hz to produce lower-body joint position targets (joints 0-14).

    The controller automatically switches between Balance (standing) and
    Walk (locomotion) policies based on command magnitude.

    Implements the ``Controller`` protocol::

        action = ctrl.compute(
            command={"velocity": [vx, vy, yaw_rate]},
            state={"qpos": qpos, "qvel": qvel},
        )

    Parameters
    ----------
    repo_id:
        HuggingFace repo with ONNX models.
    default_height:
        Desired base height in meters.
    """

    control_dt: float = 0.02  # 50 Hz

    def __init__(
        self,
        repo_id: str = GROOT_HF_REPO,
        default_height: float = 0.74,
    ):
        self._repo_id = repo_id
        self._default_height = default_height

        # Download and load ONNX models
        self._balance_session = self._load_onnx(GROOT_BALANCE_FILE)
        self._walk_session = self._load_onnx(GROOT_WALK_FILE)

        # Internal state
        self._action = np.zeros(NUM_LOWER_BODY_JOINTS, dtype=np.float32)
        self._obs_history: deque[np.ndarray] = deque(maxlen=OBS_HISTORY_LEN)
        self._cmd = np.zeros(3, dtype=np.float32)

        # Pre-fill history with zeros
        for _ in range(OBS_HISTORY_LEN):
            self._obs_history.append(np.zeros(OBS_FRAME_DIM, dtype=np.float32))

        logger.info("GR00T locomotion controller loaded (Balance + Walk)")

    def _load_onnx(self, filename: str) -> Any:
        """Load an ONNX model into an inference session."""
        try:
            import onnxruntime as ort
        except ImportError as e:
            raise ImportError(
                "onnxruntime is required for locomotion controllers. "
                "Install with: pip install onnxruntime"
            ) from e
        path = _download_onnx(self._repo_id, filename)
        return ort.InferenceSession(path, providers=["CPUExecutionProvider"])

    def compute(self, command: dict[str, Any], state: dict[str, Any]) -> np.ndarray:
        """Compute lower-body joint targets from velocity command and robot state.

        Parameters
        ----------
        command:
            ``{"velocity": [vx, vy, yaw_rate]}`` — desired base velocity.
            Omit or pass zeros for standing.
        state:
            Must contain:
            - ``"qpos"``: joint positions (at least first 36 elements for
              free joint quaternion + 29 body joints)
            - ``"qvel"``: joint velocities (at least first 35 elements for
              free joint + 29 body joints)

        Returns
        -------
        np.ndarray
            Joint position targets for joints 0-14 (lower body + waist).
        """
        # Parse command
        vel = command.get("velocity", [0.0, 0.0, 0.0])
        self._cmd[:] = vel

        # Parse state — real G1 model has free joint (7 qpos, 6 qvel) then 29+14 joints
        qpos = np.asarray(state["qpos"], dtype=np.float32)
        qvel = np.asarray(state["qvel"], dtype=np.float32)

        # Extract IMU data from free joint
        # qpos[3:7] = quaternion (w, x, y, z) for MuJoCo free joint
        base_quat = qpos[3:7] if len(qpos) > 7 else np.array([1, 0, 0, 0], dtype=np.float32)
        # qvel[3:6] = angular velocity for MuJoCo free joint
        ang_vel = qvel[3:6] if len(qvel) > 6 else np.zeros(3, dtype=np.float32)

        # Body joint positions and velocities (skip free joint)
        qj_offset = 7 if len(qpos) > 7 else 0
        dqj_offset = 6 if len(qvel) > 6 else 0
        qj = qpos[qj_offset : qj_offset + NUM_BODY_JOINTS]
        dqj = qvel[dqj_offset : dqj_offset + NUM_BODY_JOINTS]

        # Pad if needed (model may have fewer joints than expected)
        if len(qj) < NUM_BODY_JOINTS:
            qj = np.pad(qj, (0, NUM_BODY_JOINTS - len(qj)))
        if len(dqj) < NUM_BODY_JOINTS:
            dqj = np.pad(dqj, (0, NUM_BODY_JOINTS - len(dqj)))

        # Build single observation frame (86-dim)
        obs = np.zeros(OBS_FRAME_DIM, dtype=np.float32)
        obs[0:3] = self._cmd * CMD_SCALE
        obs[3] = self._default_height
        obs[4:7] = 0.0  # orientation command (zeros)
        obs[7:10] = ang_vel * ANG_VEL_SCALE
        obs[10:13] = get_gravity_orientation(base_quat)
        obs[13:42] = (qj - GROOT_DEFAULT_ANGLES) * DOF_POS_SCALE
        obs[42:71] = dqj * DOF_VEL_SCALE
        obs[71:86] = self._action  # previous action

        # Append to history
        self._obs_history.append(obs.copy())

        # Stack history: 6 frames x 86 = 516-dim (oldest first)
        obs_stacked = np.concatenate(list(self._obs_history)).reshape(1, -1).astype(np.float32)

        # Select policy: Balance for near-zero commands, Walk otherwise
        cmd_magnitude = float(np.linalg.norm(self._cmd))
        session = self._balance_session if cmd_magnitude < 0.05 else self._walk_session

        # ONNX inference
        input_name = session.get_inputs()[0].name
        output = session.run(None, {input_name: obs_stacked})
        self._action[:] = output[0].flatten()[:NUM_LOWER_BODY_JOINTS]

        # Decode action → joint position targets
        target = GROOT_DEFAULT_ANGLES[:NUM_LOWER_BODY_JOINTS] + self._action * ACTION_SCALE
        return target

    def reset(self) -> None:
        """Reset internal state (call on episode reset)."""
        self._action[:] = 0.0
        self._cmd[:] = 0.0
        self._obs_history.clear()
        for _ in range(OBS_HISTORY_LEN):
            self._obs_history.append(np.zeros(OBS_FRAME_DIM, dtype=np.float32))
