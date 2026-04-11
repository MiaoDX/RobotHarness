# LeRobot Community Response: Prepared Technical Content

_Context: Issue [miaodx/roboharness#148](https://github.com/MiaoDX/roboharness/issues/148) — contribute technical solutions to two LeRobot community threads._

**Status note (April 2026):** Both target issues are now closed:
- [lerobot#538](https://github.com/huggingface/lerobot/issues/538) — closed "not planned" (Oct 2025); original reporter self-solved with `xvfb-run`
- [lerobot#2375](https://github.com/huggingface/lerobot/issues/2375) — closed via PR #2899 (varied `init_state_id` on reset)

The prepared responses below remain accurate and can be used in:
- LeRobot Discussions tab (preferred — doesn't re-open closed issues)
- New issues if related problems resurface
- HuggingFace forum posts or Discord

---

## Response A — lerobot#538: Headless Evaluation

> Thread topic: headless MuJoCo rendering without `xvfb-run`, plus saving evaluation screenshots.

---

Hi — I ran into the same headless rendering issue while building [roboharness](https://github.com/MiaoDX/roboharness), a visual testing harness for AI coding agents in robot simulation. The key insight is that MuJoCo's native `mujoco.Renderer` works **off-screen without xvfb** as long as you set the right GL backend:

```bash
# For headless servers (no GPU): osmesa software renderer
MUJOCO_GL=osmesa python eval.py

# For servers with NVIDIA GPU: EGL hardware renderer (faster)
MUJOCO_GL=egl python eval.py
```

For saving screenshots at evaluation checkpoints, here's the core pattern:

```python
import mujoco
import numpy as np
from pathlib import Path
from PIL import Image

def capture_frame(model, data, camera_name: str, width=640, height=480) -> np.ndarray:
    """Capture a single frame headlessly — no display required."""
    renderer = mujoco.Renderer(model, height=height, width=width)
    renderer.update_scene(data, camera=camera_name)
    rgb = renderer.render()  # (H, W, 3) uint8
    renderer.close()
    return rgb

# In your eval loop:
for episode in range(n_episodes):
    obs, _ = env.reset()
    episode_dir = Path(f"eval_output/episode_{episode:04d}")
    episode_dir.mkdir(parents=True, exist_ok=True)

    for step in range(max_steps):
        action = policy(obs)
        obs, reward, done, truncated, info = env.step(action)

        # Save screenshot every N steps (or at key events)
        if step % 10 == 0:
            frame = capture_frame(env.model, env.data, camera_name="front_camera")
            Image.fromarray(frame).save(episode_dir / f"step_{step:04d}.png")

        if done or truncated:
            break
```

If you want structured JSON alongside the screenshots (useful for AI agent debugging), roboharness does this out of the box:

```python
from roboharness import Harness
from roboharness.backends.mujoco_visualizer import MuJoCoNativeVisualizer

visualizer = MuJoCoNativeVisualizer(model, data, cameras=["front_camera", "wrist_camera"])
harness = Harness(visualizer)

for episode in range(n_episodes):
    obs, _ = env.reset()
    for step in range(max_steps):
        action = policy(obs)
        obs, reward, done, truncated, info = env.step(action)

        if step % 10 == 0:
            # Saves: front_camera_rgb.png, wrist_camera_rgb.png, state.json, metadata.json
            result = harness.capture(checkpoint_name=f"ep{episode}_step{step}")
            result.save(Path(f"eval_output/episode_{episode:04d}/checkpoint_{step:04d}"))

        if done or truncated:
            break
```

The `metadata.json` output looks like:
```json
{
  "checkpoint": "ep0_step10",
  "step": 10,
  "sim_time": 0.1,
  "cameras": ["front_camera", "wrist_camera"],
  "files": {
    "front_camera": {"rgb": "front_camera_rgb.png"},
    "wrist_camera": {"rgb": "wrist_camera_rgb.png"}
  }
}
```

This makes it trivial to pass screenshots to Claude Code or another AI agent for behavioral analysis without a separate VLM inference step.

---

## Response B — lerobot#2375: Eval Reproducibility / Trajectory Recording

> Thread topic: LeRobot's LIBERO eval uses `episode_idx=0` (always same initial state), diverging from OpenPI's varied initial configurations. Also: trajectories aren't saved.

---

Hi — trajectory recording + varied initial states are exactly what we built roboharness for. The PR #2899 fix (`init_state_id` rotation) is a good start for the LIBERO init mismatch, but for broader eval reproducibility, saving structured checkpoint data at each step gives you a complete diagnostic trail.

Here's a minimal pattern for saving full trajectories with varied initial states:

```python
import json
import numpy as np
from pathlib import Path
from roboharness import Harness
from roboharness.wrappers import RobotHarnessWrapper

# Wrap any Gymnasium env — zero changes to env code
env = RobotHarnessWrapper(env, capture_dir=Path("trajectories"))

results = []
for episode_idx in range(n_episodes):
    # Use episode_idx to vary initial state (fixes the lerobot#2375 core issue)
    obs, info = env.reset(options={"episode_idx": episode_idx})
    episode_data = {"episode_idx": episode_idx, "steps": []}

    for step in range(max_steps):
        action = policy(obs)
        obs, reward, done, truncated, info = env.step(action)

        # Record structured step data alongside screenshots
        episode_data["steps"].append({
            "step": step,
            "reward": float(reward),
            "done": bool(done),
        })

        if done or truncated:
            break

    episode_data["total_reward"] = sum(s["reward"] for s in episode_data["steps"])
    results.append(episode_data)

# Save aggregate results
with open("eval_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

The key advantage is that each episode's trajectory is stored as:
```
trajectories/
├── episode_0000/
│   ├── checkpoint_0000/
│   │   ├── front_camera_rgb.png   ← what the agent saw
│   │   ├── state.json             ← full sim state (qpos, qvel, ctrl)
│   │   └── metadata.json         ← step, sim_time, reward
│   └── checkpoint_0010/
│       └── ...
└── episode_0001/
    └── ...
```

When a policy fails on episode N but succeeds on episode M, you can literally show both `front_camera_rgb.png` sequences to Claude Code and ask "what's different?" — no separate VLM infrastructure needed.

---

## Suggested venues (April 2026)

Since both original issues are closed, consider:

1. **LeRobot Discussions** — https://github.com/huggingface/lerobot/discussions — open a new thread in "Show and Tell" or "Q&A"
2. **HuggingFace Discord** `#lerobot` channel — more discoverable than GitHub for quick tips
3. **lerobot#538 was closed stale** — a follow-up discussion post linking to roboharness would be more visible than a comment on the closed issue
