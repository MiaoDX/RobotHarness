# roboharness — Visual debugging for robot simulation

## When to use
Use roboharness when an agent needs to **debug, inspect, or validate robot behavior** in simulation. Trigger conditions: task involves MuJoCo/Gymnasium robot sim, agent must verify grasp success, check poses, compare before/after states, or capture multi-camera snapshots at key moments.

## Install
```bash
pip install roboharness[demo]   # core + all demo dependencies
```

## Gymnasium wrapper (drop-in, zero-change)

```python
import gymnasium as gym
from roboharness.wrappers import RobotHarnessWrapper

env = gym.make("FetchPickAndPlace-v3", render_mode="rgb_array")
env = RobotHarnessWrapper(
    env,
    checkpoints=[{"name": "grasp", "step": 50}, {"name": "lift", "step": 100}],
    cameras=["default"],
    output_dir="./harness_output",
)
obs, info = env.reset()
for _ in range(150):
    obs, reward, term, trunc, info = env.step(env.action_space.sample())
    if "checkpoint" in info:  # auto-captured at configured steps
        print(info["checkpoint"]["name"], info["checkpoint"]["capture_dir"])
```

## Raw MuJoCo / SimulatorBackend

```python
from roboharness import Harness
from roboharness.backends.mujoco_meshcat import MuJoCoMeshcatBackend

backend = MuJoCoMeshcatBackend(model_path="robot.xml", cameras=["front", "wrist"])
harness = Harness(backend, output_dir="./harness_output", task_name="pick")

harness.add_checkpoint("pre_grasp", trigger_step=50)
harness.add_checkpoint("lift", trigger_step=100)
harness.reset()
for action in action_sequence:
    result = harness.step(action)  # returns CaptureResult at checkpoint steps

harness.restore_checkpoint("pre_grasp")  # rewind sim state to retry
```

## Output interpretation

Checkpoints save to `harness_output/<task>/trial_001/<checkpoint>/`:

| File | Contents |
|------|----------|
| `<camera>_rgb.png` | RGB snapshot — visually verify robot pose, object positions |
| `<camera>_depth.npy` | Raw float32 depth in metres; `_depth_viz.png` for visual inspection |
| `state.json` | Joint positions (`qpos`), velocities (`qvel`), controls (`ctrl`), sim time |
| `metadata.json` | Checkpoint name, step number, timestamp, camera list, file paths |

**Decision loop:** capture checkpoint images -> inspect visually or programmatically -> if wrong, `restore_checkpoint()` and retry with adjusted actions.

## MCP server (optional)

When roboharness runs as a tool service alongside other MCP tools, four tools are exposed:

| Tool | Purpose |
|------|---------|
| `capture_checkpoint` | Pause simulation, capture multi-view screenshots + state (optional base64 images) |
| `evaluate_constraints` | Run constraint evaluator on a report, return verdict |
| `compare_baselines` | Compare current success rate against evaluation history |
| `evaluate_batch_trials` | Evaluate all trials in a directory, return aggregate pass/fail with success rate |

```bash
pip install mcp                        # additional dependency
```

```python
from roboharness import Harness
from roboharness.mcp.server import create_server

harness = Harness(backend, output_dir="./output")
server = create_server(harness)
server.run()                           # blocks, listens on stdio
```

### Tool parameters

**`capture_checkpoint`** — `checkpoint_name` (string, optional), `cameras` (list of strings, default `["front"]`), `include_images` (boolean, default false — when true, each view includes an `rgb_base64` field with a base64-encoded PNG screenshot).

**`evaluate_constraints`** — `report` (object with `summary_metrics` / `snapshot_metrics`), `assertions` (list of `{metric, operator, threshold}` dicts; operators: `lt`, `le`, `eq`, `gt`, `ge`, `in_range`).

**`compare_baselines`** — `task` (string), `current_rate` (float 0–1), `window` (int, default 5), `threshold` (float, default 0.1).

**`evaluate_batch_trials`** — `results_dir` (string, path to directory with `autonomous_report.json` files), `assertions` (optional list of assertion dicts — uses grasp defaults when omitted), `min_success_rate` (optional float 0–1 — when set, result includes `ci_passed` boolean).

Business logic lives in `roboharness.mcp.tools.HarnessTools` and can be called directly without the MCP SDK.
