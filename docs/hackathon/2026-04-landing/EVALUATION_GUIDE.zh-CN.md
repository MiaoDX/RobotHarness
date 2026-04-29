# 落地赛评委 / 同事自助验证指南

> 这份文档不是用来贴飞书的。是给评委或同事点开看、自己花 5-15 分钟亲手摸一遍 Roboharness、确认这个项目不是 PPT 的指南。
>
> 主提交文档在同目录 [`SUBMISSION.zh-CN.md`](./SUBMISSION.zh-CN.md)。

---

## 0. 30 秒判断这个项目值不值得花时间

不装任何环境，依次点开：

1. https://miaodx.com/roboharness/grasp/ — 看首屏 Run Decision banner + Approval Queue（这是核心 wedge 的样子）
2. https://github.com/MiaoDX/roboharness — 看 README 第一屏的"Choose Your Start"决策树
3. https://github.com/MiaoDX/roboharness/blob/main/CHANGELOG.md — 看 v0.3.0 是 2026-04-20 发的，wedge 描述跟提交文档一致

如果上面三件事都对得上，再继续往下走。如果对不上，请直接拒掉这个项目——我们也不愿意被人凭空相信。

---

## 1. 5 分钟亲手跑一遍主 demo

```bash
# 任意 Python 3.10+ 环境（推荐 venv 或 uv）
pip install roboharness[demo]

# 默认契约（预审过的 preset）路径
python examples/mujoco_grasp.py --report --contract-preset mujoco_regression_v1

# headless / CI 环境
MUJOCO_GL=egl python examples/mujoco_grasp.py --report --contract-preset mujoco_regression_v1
```

跑完之后，检查输出目录里这 6 个文件：

| 文件 | 它是什么 | 评委关注点 |
|------|---------|----------|
| `contract.json` | 契约编译结果 | 自然语言 prompt 被翻译成结构化规则 |
| `autonomous_report.json` | 此次 run 的核心指标 + 跟 baseline 的对比 | run 的真值 |
| `alarms.json` | 触发的 hard metric 失败 | metric_gate 这一类 rule 的命中点 |
| `phase_manifest.json` | 第一个失败的 phase + 该看哪些视角 + rerun hint | 失败定位 |
| `approval_report.json` | surfaced case vs suppressed case 的判定 | 审批队列输入 |
| `report.html` | 一屏证据，不是文件夹找图 | **直接打开，先看 Run Decision banner** |

如果 `report.html` 里的 Run Decision、Approval Queue、Current vs Baseline、Hard Metric Results 都正常显示——这个项目就不是 PPT 演示。

---

## 2. 想验证 contract 编译失败的 fail-closed 行为

这是 wedge 的关键安全机制——契约不能落地，run 不允许启动。

```bash
# 故意传一个无效契约
python examples/mujoco_grasp.py --report --contract-preset NONEXISTENT_PRESET
echo "Exit code: $?"  # 应当非零
ls *.json | grep contract_compile_error  # 应当存在
```

期望行为：
- 程序 exit code 非零
- 磁盘出现 `contract_compile_error.json`，里面有 `problem / cause / fix / docs_url / next_action` 五个字段
- **没有任何 agent 行为发生**——run 在编译期就被拒绝

对应的回归测试在 `tests/test_mujoco_grasp_contract_compile_error.py`，相关 commit 是 `0c4bee7`。

---

## 3. 不想本地装环境也能交叉验证的 8 个在线 demo

每次 push 到 main 自动重新生成。也就是说**这些链接里看到的内容跟当前 main 完全同步**——这是验证此项目不是历史快照的最便捷方式。

| Demo | 链接 | 看什么 |
|------|------|--------|
| MuJoCo Grasp（**主 wedge**）| https://miaodx.com/roboharness/grasp/ | Run Decision + Approval Queue + 4-stage 证据 |
| G1 WBC Reach | https://miaodx.com/roboharness/g1-reach/ | 全身 IK，Pinocchio + Pink |
| G1 Locomotion | https://miaodx.com/roboharness/g1-loco/ | GR00T RL stand→walk→stop |
| G1 Native LeRobot (GR00T) | https://miaodx.com/roboharness/g1-native-groot/ | 走 LeRobot 官方 `make_env()`，DDS-ready |
| G1 Native LeRobot (SONIC) | https://miaodx.com/roboharness/g1-native-sonic/ | SONIC planner + LeRobot 官方接口 |
| SONIC Planner | https://miaodx.com/roboharness/sonic-planner/ | `planner_sonic.onnx` 单独路径 |
| SONIC Tracking | https://miaodx.com/roboharness/sonic/ | `encoder + decoder` 真实 ONNX |
| 总入口 | https://miaodx.com/roboharness/ | 一屏看全部 |

---

## 4. 看代码里的关键设计文档

按建议顺序读：

| 文件 | 行数 | 内容 |
|------|------|------|
| [`docs/designs/unattended-refactor-harness-v1.md`](https://github.com/MiaoDX/roboharness/blob/main/docs/designs/unattended-refactor-harness-v1.md) | ~200 | **整个 wedge 的产品契约** —— Verdict 模型、Stop Policy、Contract Schema、Rule Types 全在这一份里 |
| [`showcase-repo-plan.md`](https://github.com/MiaoDX/roboharness/blob/main/showcase-repo-plan.md) | ~100（首段）| **wedge 决策的反思日志** —— 为什么之前的 plan 是错的（"清理 repo 不是真瓶颈，trust 才是"）|
| [`docs/strategic-direction-review-2026-04.md`](https://github.com/MiaoDX/roboharness/blob/main/docs/strategic-direction-review-2026-04.md) | ~150（前半）| **战略评审记录** —— 为什么坚持单 repo、为什么 SKILL.md 优先于 MCP、为什么把 interaction scaling 当一号优先级 |
| [`docs/roadmap-2026-q2.md`](https://github.com/MiaoDX/roboharness/blob/main/docs/roadmap-2026-q2.md) | ~150 | 当前路线图，Do Now / Do Later 显式区分 |
| [`AGENTS.md`](https://github.com/MiaoDX/roboharness/blob/main/AGENTS.md) | ~100 | **给 AI agent 看的项目契约** —— 这本身就是 harness engineering 的产物 |
| [`SKILL.md`](https://github.com/MiaoDX/roboharness/blob/main/SKILL.md) | ~80 | Roboharness 自己的"如何被 AI agent 调用"说明 —— 60 行以内、手写、不让 LLM 自动生成（出处见 ETH Zurich 那篇 AGENTS.md research）|

---

## 5. 想看自 0307 至今的工程演进

127 commit，但下面这 7 个 commit 是 wedge 转变的关键节点。点开看 diff，能感受到产品方向的变化轨迹：

| Commit | 日期 | 它做了什么 |
|--------|------|----------|
| `24904a8` | 04-18 | docs: approve **contract-first unattended refactor plan** —— wedge 转变的官方决策点 |
| `d0c554b` | 04-18 | feat: add **contract-first MuJoCo approval wedge** —— wedge 转变的代码落地起点 |
| `a56896e` | 04-20 | fix: make **MuJoCo contracts authoritative** —— 把契约定为唯一真值来源 |
| `a82a0ab` | 04-20 | test: add **seeded MuJoCo evaluator corpus** —— 用语料库锁住 surfaced case 的判定边界 |
| `7d94f0f` | 04-20 | feat: add **temporal evidence and lightbox** to wedge report —— 模糊 case 自动收集时间序列证据 |
| `0c4bee7` | 04-20 | test: cover **MuJoCo contract compile failure** —— 把 fail-closed 写进回归测试 |
| `c9eba44` | 04-20 | docs: add **trust-loop steering and validation guards** —— wedge 守护边界的最终落定 |

GitHub 上点对应 commit 看 diff：`https://github.com/MiaoDX/roboharness/commit/<sha>`

---

## 6. KPI 数字快查表

供评委 / 同事在飞书评分表里直接复用：

```
项目: Roboharness（roboharness）
版本: v0.3.0（2026-04-20 发布）
仓库: https://github.com/MiaoDX/roboharness

代码规模:
  - 源码 (src/):   7,877 行  /  44 .py 文件
  - 测试 (tests/): 10,440 行 /  47 .py 文件
  - 测试覆盖率阈值: 90%
  - 总 commit:    229 次
  - 自 0307:      127 次提交（一个多月）

CI:
  - GitHub Actions: lint + type + pytest（Python 3.10–3.13）
  - Cirun GPU smoke test (AWS Sydney)
  - GitHub Pages: 8 个 demo HTML 自动重生成
  - PyPI 自动发布

Demo:
  - 在线公开 HTML 报告: 8 个
  - 可运行示例 (examples/): 16 个

Wedge 核心承诺:
  - 2-3 小时无人值守 agent run → 3 分钟人工审批
  - PASS / FAIL / AMBIGUOUS / CONTRACT_INVALID 四态判定
  - regression / migration 双模式
  - metric_gate / visual_goal / anti_goal 三类规则

依赖：
  - 核心包: numpy（仅）
  - demo extras: MuJoCo, Meshcat, Gymnasium, Rerun, Pillow
  - lerobot extras: 官方 LeRobot
  - wbc extras: Pinocchio, Pink

落地赛重点新增（自 0307 后）:
  - Contract-first approval wedge
  - Seeded MuJoCo evaluator corpus（good/bad/ambiguous）
  - LeRobot Evaluation Plugin (CI gating)
  - G1 cross-framework paired-evidence proof
  - SONIC 拆分为 planner / tracking 两个独立 demo
  - LeRobot native 拆分为 GR00T / SONIC 两个独立 demo
```

---

## 7. 如果你想自己接入它

3 个集成路径，按工作量排序：

### 路径 A：Gymnasium wrapper（3 行接入）

适合任何 `render_mode="rgb_array"` 的环境（LeRobot、ManiSkill、Isaac Lab、Gymnasium 自带）：

```python
import gymnasium as gym
from roboharness.wrappers import RobotHarnessWrapper

env = gym.make("YourEnv-v1", render_mode="rgb_array")
env = RobotHarnessWrapper(env, checkpoints=[
    {"name": "early", "step": 10},
    {"name": "lift",  "step": 50},
], output_dir="./output")
```

### 路径 B：契约驱动的完整 wedge（推荐落地用）

```bash
python examples/mujoco_grasp.py --report \
    --contract-preset mujoco_regression_v1
# 或
python examples/mujoco_grasp.py --report \
    --contract-prompt "treat this as migration mode and require manual blessing"
```

### 路径 C：直接调 `Harness` 类（自定义仿真循环）

```python
from roboharness import Harness
from roboharness.backends.mujoco_meshcat import MuJoCoMeshcatBackend

backend = MuJoCoMeshcatBackend(model_path="robot.xml", cameras=["front", "side"])
harness = Harness(backend, output_dir="./output", task_name="pick_and_place")
harness.add_checkpoint("pre_grasp", cameras=["front", "side"])
harness.add_checkpoint("lift", cameras=["front", "side"])
harness.reset()
result = harness.run_to_next_checkpoint(actions)
```

---

## 8. 反馈渠道

发现问题、想提建议、想接入但有阻力——任意一项都欢迎：

- GitHub Issues: https://github.com/MiaoDX/roboharness/issues
- 团队邮箱: miaodongxu@xiaomi.com / dingsong1@xiaomi.com

如果你帮我们找出主提交文档里的硬伤——比如数字算错了、wedge 不能像我们说的那样跑——这是项目最大的福利。
