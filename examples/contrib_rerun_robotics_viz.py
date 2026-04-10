#!/usr/bin/env python3
"""Rerun + Roboharness: Multi-view Robot Simulation Visualization.

A community example showing how to visualize multi-view robot simulation
captures with Rerun, using roboharness as the capture harness.

This example demonstrates:
  - Logging multi-camera RGB and depth images to Rerun
  - Using Rerun timelines (simulation step + wall-clock time)
  - Annotating captures with simulation state (joint positions, contacts)
  - Applying a Blueprint for a standardized robotics debug layout
  - Exporting a portable ``.rrd`` file for offline viewing

The Roboharness library provides checkpoint-based visual capture for robot
simulations. Combined with Rerun's visualization, this creates a powerful
debugging workflow for AI coding agents working on manipulation tasks.

Run:
    pip install roboharness[demo]
    MUJOCO_GL=osmesa python examples/contrib_rerun_robotics_viz.py

View the recording:
    rerun harness_rerun_output/grasp_debug/trial_001/capture.rrd

Upstream target: Rerun examples gallery
  https://github.com/rerun-io/rerun/tree/main/examples/python
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rerun + Roboharness: Multi-view Robot Simulation Visualization"
    )
    parser.add_argument("--output-dir", default="./harness_rerun_output", help="Output directory")
    parser.add_argument("--width", type=int, default=640, help="Render width")
    parser.add_argument("--height", type=int, default=480, help="Render height")
    args = parser.parse_args()

    # --- Check dependencies ---
    try:
        import rerun as rr  # noqa: F401
    except ImportError:
        print("ERROR: rerun-sdk is required. Install with: pip install rerun-sdk>=0.18")
        sys.exit(1)

    try:
        import mujoco  # noqa: F401
    except ImportError:
        print("ERROR: mujoco is required. Install with: pip install mujoco>=3.0")
        sys.exit(1)

    from roboharness.backends.mujoco_meshcat import MuJoCoMeshcatBackend
    from roboharness.core.harness import Harness
    from roboharness.core.protocol import GRASP_PROTOCOL

    output_dir = Path(args.output_dir)

    print("=" * 60)
    print("  Rerun + Roboharness: Multi-view Robot Visualization")
    print("=" * 60)

    # 1. Load a MuJoCo model with multiple cameras
    print("\n[1/5] Loading MuJoCo model with 3 cameras ...")
    backend = MuJoCoMeshcatBackend(
        xml_string=GRASP_MJCF,
        cameras=["front", "side", "top"],
        render_width=args.width,
        render_height=args.height,
    )

    # 2. Create harness with Rerun logging enabled
    print("[2/5] Setting up harness with Rerun capture logging ...")
    harness = Harness(
        backend,
        output_dir=str(output_dir),
        task_name="grasp_debug",
        enable_rerun=True,
        rerun_app_id="roboharness_rerun_example",
    )
    harness.load_protocol(
        GRASP_PROTOCOL,
        phases=["pre_grasp", "approach", "grasp", "lift"],
    )
    print(f"      Protocol: {harness.active_protocol.name}")
    print(f"      Checkpoints: {harness.list_checkpoints()}")

    # 3. Build scripted grasp sequence
    phases = _build_grasp_phases()

    # 4. Run simulation — each checkpoint logs to .rrd automatically
    print("[3/5] Running grasp simulation (logging to Rerun) ...")
    harness.reset()

    for phase_name, actions in phases.items():
        result = harness.run_to_next_checkpoint(actions)
        if result is None:
            print(f"      WARNING: No checkpoint for phase '{phase_name}'")
            continue

        n_views = len(result.views)
        print(
            f"      Checkpoint '{phase_name}': {n_views} views"
            f" | step={result.step} | sim_time={result.sim_time:.3f}s"
        )

    # 5. Log additional annotations to the recording
    print("[4/5] Adding state annotations to Rerun recording ...")
    _log_state_summary(harness, phases)

    # 6. Summary
    rrd_path = output_dir / "grasp_debug" / "trial_001" / "capture.rrd"
    print("\n[5/5] Done!")
    if rrd_path.exists():
        size_mb = rrd_path.stat().st_size / (1024 * 1024)
        print(f"      Rerun recording: {rrd_path} ({size_mb:.1f} MB)")
    else:
        print(f"      Expected recording at: {rrd_path}")

    print("\n  View the recording:")
    print(f"    rerun {rrd_path}")
    print()
    print("  What you'll see in the Rerun Viewer:")
    print("    - camera/front/rgb, camera/side/rgb, camera/top/rgb — multi-view captures")
    print("    - camera/*/depth — depth maps at each checkpoint")
    print("    - harness/checkpoint — checkpoint names on the timeline")
    print("    - harness/state — full simulation state JSON at each checkpoint")
    print("\n" + "=" * 60)


def _log_state_summary(harness: object, phases: dict[str, list[np.ndarray]]) -> None:
    """Log a summary of what happened at each phase (for Rerun annotation)."""
    import rerun as rr

    summaries = {
        "pre_grasp": "Gripper open, hovering above the cube",
        "approach": "Gripper lowered onto the cube, fingers still open",
        "grasp": "Fingers closed around the cube",
        "lift": "Cube lifted off the table surface",
    }

    cumulative_step = 0
    for phase_name, actions in phases.items():
        cumulative_step += len(actions)
        if hasattr(rr, "set_time_sequence"):
            rr.set_time_sequence("sim_step", cumulative_step)
        else:
            rr.set_time("sim_step", sequence=cumulative_step)

        description = summaries.get(phase_name, phase_name)
        rr.log("harness/phase_summary", rr.TextDocument(f"**{phase_name}**: {description}"))


# ---------------------------------------------------------------------------
# Grasp action helpers
# ---------------------------------------------------------------------------


def _make_action_sequence(
    target_z: float, finger_left: float, finger_right: float, n_steps: int
) -> list[np.ndarray]:
    action = np.array([target_z, finger_left, finger_right])
    return [action for _ in range(n_steps)]


def _build_grasp_phases() -> dict[str, list[np.ndarray]]:
    left_open, left_closed = 0.015, -0.02
    right_open, right_closed = -0.015, 0.02

    return {
        "pre_grasp": _make_action_sequence(0.05, left_open, right_open, 500),
        "approach": _make_action_sequence(-0.24, left_open, right_open, 500),
        "grasp": _make_action_sequence(-0.24, left_closed, right_closed, 800),
        "lift": _make_action_sequence(-0.10, left_closed, right_closed, 800),
    }


# ---------------------------------------------------------------------------
# Inline MJCF model: table + cube + 2-finger gripper + 3 cameras
# ---------------------------------------------------------------------------
GRASP_MJCF = """\
<mujoco model="simple_grasp">
  <option gravity="0 0 -9.81" timestep="0.002"/>

  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.6 0.8 1.0" rgb2="0.2 0.3 0.5"
             width="256" height="256"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.9 0.9 0.9" rgb2="0.7 0.7 0.7"
             width="256" height="256"/>
    <material name="grid_mat" texture="grid" texrepeat="4 4" reflectance="0.1"/>
    <material name="table_mat" rgba="0.6 0.4 0.2 1"/>
    <material name="cube_mat" rgba="0.9 0.2 0.2 1"/>
    <material name="gripper_mat" rgba="0.3 0.3 0.7 1"/>
  </asset>

  <worldbody>
    <geom type="plane" size="1 1 0.01" material="grid_mat"/>
    <light pos="0 0 2" dir="0 0 -1" diffuse="0.8 0.8 0.8"/>
    <light pos="0.5 0.5 1.5" dir="-0.3 -0.3 -1" diffuse="0.4 0.4 0.4"/>

    <camera name="front" pos="0.75 0 0.55" xyaxes="0 1 0 -0.4 0 0.75"/>
    <camera name="side" pos="0 0.75 0.55" xyaxes="-1 0 0 0 -0.4 0.75"/>
    <camera name="top" pos="0 0 1.2" xyaxes="1 0 0 0 1 0"/>

    <body name="table" pos="0 0 0.2">
      <geom type="box" size="0.3 0.3 0.02" material="table_mat"/>
      <geom type="cylinder" size="0.015 0.1" pos=" 0.25  0.25 -0.12"/>
      <geom type="cylinder" size="0.015 0.1" pos="-0.25  0.25 -0.12"/>
      <geom type="cylinder" size="0.015 0.1" pos=" 0.25 -0.25 -0.12"/>
      <geom type="cylinder" size="0.015 0.1" pos="-0.25 -0.25 -0.12"/>
    </body>

    <body name="cube" pos="0 0 0.25">
      <joint type="free"/>
      <geom type="box" size="0.025 0.025 0.025" mass="0.02" material="cube_mat"
            friction="2.0 0.1 0.001" condim="4" solref="0.01 1" solimp="0.95 0.99 0.001"/>
    </body>

    <body name="gripper_base" pos="0 0 0.55">
      <joint name="gripper_z" type="slide" axis="0 0 1" range="-0.35 0.1" damping="50"/>
      <geom type="cylinder" size="0.02 0.03" material="gripper_mat"/>

      <body name="finger_left" pos="0 0.04 -0.06">
        <joint name="finger_left" type="slide" axis="0 1 0" range="-0.02 0.015" damping="0.5"/>
        <geom type="box" size="0.012 0.012 0.04" material="gripper_mat"
              friction="2.0 0.1 0.001" condim="4"/>
      </body>

      <body name="finger_right" pos="0 -0.04 -0.06">
        <joint name="finger_right" type="slide" axis="0 1 0" range="-0.015 0.02" damping="0.5"/>
        <geom type="box" size="0.012 0.012 0.04" material="gripper_mat"
              friction="2.0 0.1 0.001" condim="4"/>
      </body>
    </body>
  </worldbody>

  <actuator>
    <position name="gripper_z_ctrl" joint="gripper_z" kp="200" ctrlrange="-0.35 0.1"/>
    <position name="finger_left_ctrl" joint="finger_left" kp="100" ctrlrange="-0.02 0.015"/>
    <position name="finger_right_ctrl" joint="finger_right" kp="100" ctrlrange="-0.015 0.02"/>
  </actuator>
</mujoco>
"""

if __name__ == "__main__":
    main()
