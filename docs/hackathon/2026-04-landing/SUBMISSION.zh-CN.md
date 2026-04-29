# Roboharness — 落地赛提交（2026-04）

> **文档定位：飞书可直接粘贴。** 所有图片/GIF 走 GitHub raw 链接，飞书会自动渲染。

> **一句话 wedge：** 把 Claude Code / Codex 的 **2-3 小时无人值守机器人代码重构**，压缩成工程师 **3 分钟最终审批**。

---

## 团队信息

- 缪东旭 / `miaodongxu` / `miaodongxu@xiaomi.com`
- 丁松 / `dingsong1` / `dingsong1@xiaomi.com`

## 项目链接

- GitHub: https://github.com/MiaoDX/roboharness
- PyPI: `pip install roboharness`
- 在线 demo 总入口: https://miaodx.com/roboharness/
- 上届 hackathon 分支（对照基线）: https://github.com/MiaoDX/roboharness/tree/hackathon/0307

---

## 跟上次 hackathon（0307）相比，我们到底做了什么

上次我们卖的是 **capability 故事**——"让 AI agent 不再只看日志、真正看见机器人在做什么"。

跑了一个月之后，我们发现一个更扎心的问题：

> **"agent 能看见"不等于"工程师敢离开屏幕"。**
>
> 如果工程师不能信任 agent 的产出，agent 跑 6 小时 = 工程师盯 6 小时屏幕。 capability 增加了，时间没省下来。

所以 v0.3.0（4 月 20 日发布）我们把核心 wedge 整体换了：从 **"给 agent 装眼睛"** 切到了 **"信任压缩"**。这次落地赛的提交，主体讲的是这个新 wedge。

### 核心变化对照表

| 维度 | 0307 hackathon | 现在（落地赛 / v0.3.0） |
|------|---------------|----------------------|
| **核心 wedge** | 给 agent 装眼睛（visual testing harness） | 信任压缩：2-3 小时无人值守 → 3 分钟人工审批 |
| **核心问题** | agent 看不见仿真画面 | 工程师不敢相信 agent 6 小时跑出来的东西 |
| **输出** | PNG 截图 + JSON 状态包 | contract.json + alarms.json + approval_report.json + phase_manifest.json + report.html 证据包 |
| **运行模式** | 单一截图模式 | regression / migration 双模式，**contract-first 编译** |
| **判定** | 工程师/agent 自己看 | **PASS / FAIL / AMBIGUOUS / CONTRACT_INVALID** 四态 |
| **首屏** | 全部 checkpoint 缩略图 | **只显示 surfaced cases（变化的、模糊的）** |
| **失败上限** | 无 | 同一 failure signature 重复 2 次必停，最多 12 次重跑 |
| **评测语料** | 无 | seeded MuJoCo evaluator corpus（good/bad/ambiguous）锁信任边界 |

### 项目一览（数字快查）

> 同口径对比 — 用同一个 [`classify_commits.py`](./scripts/classify_commits.py) 重新跑了两个时间点的数据。0307 那份文档里的 50/48/96% 是手数，本表统一用 commit body trailer + author 自动分类，可现场复现。

| 指标 | 0307 hackathon | 现在 | 增长 |
|------|---------------|------|------|
| 源码（src/）| ~4,000 行 | **7,877 行** | +97% |
| 测试（tests/）| ~3,500 行 | **10,440 行** | +198% |
| 可运行示例 | 8 | **16** | 2× |
| 在线 HTML demo 报告 | 5 | **8** | +3 个 |
| 总 commit | 107（同口径重数）| **229** | 2.1× |
| 自 0307 至今的 commit | — | **127** | 一个多月 |
| 测试覆盖率阈值 | — | 90% |  |
| CI 工作流 | 4 | 4（CPU lint/type/test + Cirun GPU smoke + Pages + Release）|  |
| **AI 参与度（commit 级）** | **89.7%** | **91.7%**（自 0307 起 **92.9%**）| 不降反升 |

---

## 为什么这次叫"落地"，不再叫"demo"

落地赛我们认为评委关心的不是技术新颖性，而是**这个东西部署后是否真能省下工程师的时间**。

下面是把新 wedge 落到一个真实场景里的展开。

### 场景：抓取算法重构（典型一周一次的工作）

某机器人算法工程师收到指令："把侧抓爆破手把改成顶向抓球，已有 8 个测试场景里的其它逻辑保持不变。"

**0307 wedge 下的工作流：**

```
工程师写 prompt → 给 Claude Code → 工程师边盯仿真窗口边看 →
agent 改完 → 工程师挨个看 8 个场景的截图 → 人肉对比新旧行为 →
发现 agent 偷换了 2 个测试场景 → 找出来 → 让 agent 重做 → 再看一遍
```

工程师人时 ≈ 6 小时（因为不敢离开），agent 自主跑时间被人盯进度浪费掉。

**新 wedge 下的工作流：**

```
工程师写 prompt → roboharness 编译成 JSON contract（MIGRATION 模式 +
8 个场景标 immutable + 顶向抓球 visual_goal + "侧抓 + 抓爆破手把"
anti_goal）→ 编译失败/有歧义则停下问 → 编译通过才允许 agent 启动 →
agent 跑 2-3 小时无人值守 → 8 个场景里 5 个 PASS（不上首屏）、
2 个 AMBIGUOUS（自动收集更多视角和 phase 强证据）、1 个 anti_goal
被命中 FAIL → 工程师只看这 3 个 case 的 report.html
```

工程师人时 ≈ 3 分钟，agent 真自主跑了 2-3 小时。**这个 ROI 缺口就是"落地"二字的全部意义。**

### 评委可计算的收益

假设一个 5 人机器人算法小组，每周每人有 2 次"长重构"任务：

| 指标 | 旧流程（人盯）| 新流程（信任压缩）| 节省 |
|------|------|------|------|
| 单次工程师人时 | ~6h | ~3 min | -99% |
| 每周组人时（2 次 × 5 人）| 60h | 0.5h | **-59.5h** |
| 一年（按 40 周）| 2400h | 20h | **-2380h ≈ 1.4 个 FTE** |

数字会随团队规模和重构频率变化，但**收益曲线只跟"AMBIGUOUS / FAIL case 数"线性相关，不再跟 agent 总产出线性相关**——这是这次 wedge 设计的核心承诺。

---

## 核心方案：Contract-First Approval Wedge

### 1. 自然语言不是真理来源

工程师写"把侧抓改成顶抓"。直接传给 agent 会出问题——agent 可以偷换概念、删测试、改 baseline、把失败合理化（[Anthropic 原话](https://www.anthropic.com/engineering/harness-design-long-running-apps)：agent will "confidently praise their own work despite obvious mediocrity"）。

所以 **prompt → run** 之间多插了一步 **prompt → contract → run**：

```
工程师 prompt
     │
     ▼
[contract 编译器]──► 选已审过的 preset（mujoco_regression_v1 等）
     │           或 prompt-assisted preset 选择
     │           开放式自然语言契约：fail-closed（拒绝启动）
     ▼
contract.json
     │
     ▼
[run 启动校验]──► 每条 rule 必须有 judge + evidence_at；缺一就停
     │
     ▼
agent 跑（无人值守 2-3 小时）
     │
     ▼
PASS / FAIL / AMBIGUOUS / CONTRACT_INVALID
```

如果 prompt 不能落到 grounded contract，run 不允许启动；用户拿到的是 `problem / cause / fix / docs_url / next_action` 五字段的错误信封，不是模糊的"试试看"。

### 2. 双模式：regression vs migration

| 模式 | 何时用 | baseline 权威性 | agent 能否提议新 baseline |
|------|--------|--------------|----------------------|
| **regression** | 重构/优化，行为应保持一致 | 旧 baseline 权威，可见变化默认可疑 | 否（任何变化都进 surfaced 队列）|
| **migration** | 明确要新行为（如侧抓改顶抓）| 仅老场景集合 immutable | 可以，**但需要人最后一次性 bless** |

没有这两种模式的区分，agent 可以把"我让你重构"洗成"我顺便把行为也改了"。

### 3. 三种 rule，足够覆盖 v1 场景

- **`metric_gate`** — 硬性数值/布尔门槛。例：lift 阶段 cube z > 桌面 + 5mm；alarm 计数 ≤ 0
- **`visual_goal`** — 应当看到的目标行为。例：最终顶视图必须看到掌心向下握球
- **`anti_goal`** — 似是而非的坏行为，命中即 FAIL。例：手指碰瓶子而非球；最后一帧靠瞬时抖动伪装目标姿态

每条 rule 必须申明：
- `judge` ∈ {metric, visual, hybrid}
- `evidence_at` = phase + view（+ 可选 motion window）

### 4. 首屏 = 只看变了的

旧 report 是把所有 checkpoint 缩略图铺一屏。新 report 首屏是 **Run Decision banner + 只显示 surfaced case 的 approval queue**。8 个场景里 5 个未变化的根本不上首屏（保留在折叠区），工程师不需要扫不需要看的东西。

```
┌────────────────────────────────────────────┐
│ Run Decision: REVIEW REQUIRED              │
│ 8 cases / 3 surfaced / 5 unchanged         │
├────────────────────────────────────────────┤
│ ⚠ scene_03  AMBIGUOUS  (visual_goal#2)    │
│ ✗ scene_07  FAIL       (anti_goal#1)      │
│ ⚠ scene_04  MIGRATION  (proposed baseline) │
└────────────────────────────────────────────┘
```

---

## 现有 Demo（GitHub 直链可看）

### Demo 1：MuJoCo Approval Wedge（首推，落地赛主 demo）

抓取任务的 4 阶段证据：`pre_grasp → contact → grasp → lift`

| pre_grasp | contact | grasp | lift |
|:-:|:-:|:-:|:-:|
| ![pre](https://github.com/MiaoDX/roboharness/raw/main/assets/example_mujoco_grasp/pre_grasp_front.png) | ![contact](https://github.com/MiaoDX/roboharness/raw/main/assets/example_mujoco_grasp/contact_front.png) | ![grasp](https://github.com/MiaoDX/roboharness/raw/main/assets/example_mujoco_grasp/grasp_front.png) | ![lift](https://github.com/MiaoDX/roboharness/raw/main/assets/example_mujoco_grasp/lift_front.png) |

- 在线报告: https://miaodx.com/roboharness/grasp/
- 重现命令:
  ```bash
  pip install roboharness[demo]
  python examples/mujoco_grasp.py --report
  # 或 preset 模式（落地赛主推路径）：
  python examples/mujoco_grasp.py --report --contract-preset mujoco_regression_v1
  ```
- 你会拿到：`contract.json` / `autonomous_report.json` / `alarms.json` / `phase_manifest.json` / `approval_report.json` / `report.html`

### Demo 2：G1 Cross-Framework Proof（0307 之后新增）

证明 agent 改的不只是其中一个仿真框架的行为——**Meshcat 视角和 MuJoCo 视角并排出 paired 证据**。

![G1 cross-framework](https://github.com/MiaoDX/roboharness/raw/main/assets/g1/X36_Y28_Z13/g1_meshcat_mujoco_comparison.gif)

- 重现命令: `python examples/g1_cross_framework_report.py`

### Demo 3：G1 WBC Reach（保留）

全身 IK，Pinocchio + Pink，双臂同时到达 3D target，下肢保持平衡。

| stand | reach_left | reach_both | retract |
|:-:|:-:|:-:|:-:|
| ![stand](https://github.com/MiaoDX/roboharness/raw/main/assets/example_g1_wbc_reach/stand_front.png) | ![reach_left](https://github.com/MiaoDX/roboharness/raw/main/assets/example_g1_wbc_reach/reach_left_front.png) | ![reach_both](https://github.com/MiaoDX/roboharness/raw/main/assets/example_g1_wbc_reach/reach_both_front.png) | ![retract](https://github.com/MiaoDX/roboharness/raw/main/assets/example_g1_wbc_reach/retract_front.png) |

- 在线报告: https://miaodx.com/roboharness/g1-reach/

### Demo 4-5：LeRobot Native（拆分为 GR00T / SONIC 两个独立 demo）

0307 时是合并展示，现在按 controller 拆成两份独立报告，便于工程师按 controller 选择验证目标：

- GR00T balance + walk: https://miaodx.com/roboharness/g1-native-groot/
- SONIC planner: https://miaodx.com/roboharness/g1-native-sonic/

走的是 LeRobot 官方 `make_env("lerobot/unitree-g1-mujoco")` 工厂函数，DDS-ready，硬件到位时直接 sim-to-real。

### Demo 6：SONIC Planner Standalone（新增）

`planner_sonic.onnx` 单独路径：速度命令进、全身姿态轨迹出。

- 在线报告: https://miaodx.com/roboharness/sonic-planner/

### Demo 7：SONIC Motion Tracking

`encoder + decoder` 真实 ONNX 路径，回放 MoCap clip。

- 在线报告: https://miaodx.com/roboharness/sonic/

### Demo 8：LeRobot Evaluation Plugin（新增，落地赛重要）

把 roboharness 作为 LeRobot 官方 policy 评估的 **CI 阈值卡**：

```bash
pip install roboharness[lerobot]
python examples/lerobot_eval_harness.py \
    --checkpoint-path /path/to/lerobot/checkpoint \
    --repo-id lerobot/unitree-g1-mujoco \
    --n-episodes 5 \
    --assert-threshold --min-success-rate 0.8
```

`--min-success-rate` 不达标 → exit code 1，CI fail。这是**第一个把 roboharness 接入第三方训练框架做 PR 准入门槛的 demo**，对应业务落地中"我能不能给 agent 写的 policy 直接装一个 CI 门"的核心问题。

### Demo 9：G1 Locomotion（保留）

GR00T RL `stand → walk → stop`。在线报告: https://miaodx.com/roboharness/g1-loco/

---

## 真实案例

### 案例 1：qpos 索引（0307 那个，依然有效）

**背景：** MuJoCo 抓取代码 checkpoint 截图看起来一切正常（夹爪确实夹住了方块）。但 CI 加上 `--assert-success` 物理约束验证后断言立刻失败：cube z 高度 ≈ 0。

**根因：** Agent 假设 `qpos` 数组里 slide joint 排在前面，用 `qpos[5]` 读取 cube z。但 MuJoCo 实际把 free joint 排前面，正确索引是 `qpos[2]`。

**这说明什么：** 视觉说"OK"、约束说"不对"——**两者结合才是完整反馈**。这是 metric_gate 这个 rule type 存在的全部理由。

> 相关提交: `102a593 fix: correct qpos index for cube z-position in grasp assertion`

### 案例 2：seeded evaluator corpus（v0.3.0 新增，落地赛新案例）

为了让 surfaced-case 的判断本身有信任边界，我们做了一个**有意构造的评测语料库**：

- `good/` — 行为正确的真 PASS 样本
- `bad/` — 应该被抓到的真 FAIL 样本（含 anti_goal 命中）
- `ambiguous/` — 不可自己 self-pass 的边界样本

每次发布前，wedge 必须在这个语料上跑一遍：good 全 PASS、bad 全 FAIL、ambiguous 不能被偷渡成 PASS。**没有这个语料，'信任压缩' 就是空话——你怎么证明 surfaced case 的标准本身没漂？**

这件事是落地导向的工程动作，不是论文风的设计。它直接对应"我怎么向同事证明这个 wedge 可以信任"。

> 相关提交: `a82a0ab test: add seeded MuJoCo evaluator corpus`

### 案例 3：contract 编译失败时的 fail-closed（v0.3.0 新增）

如果 prompt 不能落到 grounded contract，run **不允许启动**，并在磁盘留下 `contract_compile_error.json`。我们专门为这件事写了脚本级回归测试——因为 fail-closed 必须是契约的一部分，不能依赖 agent 自觉。

> 相关提交: `0c4bee7 test: cover MuJoCo contract compile failure`

---

## 业务可落地场景

为了避开 PPT 概念，下面四个场景都是当前已经能跑或者改少量代码就能落的：

### 场景 A：机器人公司内部抓取/装配测试自动化

测试工程师不再每次都看视频。每周长重构后跑 8-32 个 standard scene 集合，工程师只看 surfaced case。
- **当前已支持**：MuJoCo grasp + LeRobot G1 + 任何 `render_mode="rgb_array"` 的 Gymnasium env
- **接入工作量**：3 行 Gymnasium wrapper + 1 个 contract preset

### 场景 B：Sim-to-Real 部署前的回归保护

每次代码改动前后跑同一组场景，证据包做 paired 对比。real 上的同样 contract 可以复用同一套 rule，只是换 `evidence_at` 的视角源。
- **当前进度**：sim 端完整、real 端 DDS hook 已做（demo 4-5 的 native LeRobot 路径已经 DDS-ready）
- **缺口**：real camera feed 的 evidence 通道还在硬件验证

### 场景 C：训练曲线之外的策略评估

LeRobot/HuggingFace 上很多公开 checkpoint 只有 success rate 数字，没有视觉证据。我们的 LeRobot eval plugin 把这件事插到 CI 里。
- **直接对应 LeRobot 官方未解决 issue #538、#2375**
- **下一步**：往 LeRobot 上游提一个 eval entry PR

### 场景 D：第三方机器人代码审查 / 外包验收

合同方提交代码 → 一键编译 contract（甲方写）→ 短报告输出。**甲方拿 surfaced case 给乙方做反驳**，比口头扯皮高效得多。
- **直接价值**：把口头"代码不达标"翻译成"contract 第 5 条 anti_goal#3 命中，证据见 phase_manifest 第 12 帧"

---

## 适用边界（诚实说）

我们坚持把这一段写出来，因为评委是混合背景，看得多了，**只讲优点的方案大概率不在这个领域的核心**。

1. **当前主要在 MuJoCo + G1 + 抓取/移动/到达类任务上验证过。** 长时间力反馈、精细装配（插孔、拧螺丝）类任务还没在 v0.3.0 wedge 里跑过。
2. **Sim-to-real 那一段还需要硬件验证。** DDS 通道已经做了（issue #81、#83），但真机 camera feed 的 evidence 通道还在做。
3. **contract preset 数量有限。** 目前只有 `mujoco_regression_v1` 和 `mujoco_migration_guarded_v1` 两个被审过的 preset；开放式自然语言契约是 fail-closed（这是产品决策，不是 bug）。
4. **AMBIGUOUS 自动收集证据有上限：12 次 rerun。** 复杂场景可能撞到上限然后停下问人。
5. **MJX 大规模并行还没接进 wedge。** 当前是一次重构跑一遍，不是 1000 个 case 同时跑。

---

## 开发方式（保留 0307 故事，但作为支撑）

这个仓库本身依然是一次 agentic engineering 实验。**自 0307 至今 127 个 commit，用同一个 [classifier 脚本](./scripts/classify_commits.py) 跑出来的真实分类是：**

| 类别 | commits | 占比 | 含义 |
|------|---------|------|------|
| AI solo（Claude 直接 author）| 77 | 60.6% | agent 一把梭 |
| AI co-authored（人 author + Codex/Claude trailer）| 41 | 32.3% | **人在 loop 里 bless agent 产出** |
| Human only（无 AI 痕迹）| 9 | 7.1% | 真人手敲 |
| **AI 参与合计** | **118** | **92.9%** | |

跟 0307 时同口径（89.7%）相比 **不降反升**——但更值得讲的不是这 3 个百分点：

- **0307 时几乎全部是 AI solo（96/107）—— agent 一把梭模式**
- **现在 32.3% 是 AI co-authored —— MiaoDX author + Codex trailer，人在 loop 里 bless**

这个变化跟项目当前的 wedge 完全对得上：从"agent 全自动"演化成"agent 干活、契约和 bless 由人把关"。这恰恰是产品契约（contract-first approval gate）在团队工作流里的镜像，**不是巧合**——一个产品自己用什么方式做出来，跟它向用户主张什么样的工作流，应该是一致的。

### 工作流细节

- Claude Opus chat 做 roadmap / refactor steering（高层规划）
- 拆 GitHub issue（issue-driven，方向决策由人做）
- claude.ai/code/scheduled 自动给 issue 打优先级 label + 开 auto PR
- 本地用 Codex 做需要紧密迭代的工作（commit 体现为 MiaoDX author + Codex trailer）
- CI 跑 UT/CPU/GPU + 自动重生成 8 个 demo 的 HTML 报告

> Claude / Codex 不是"写几段代码的助手"，是**承担规划 → 实现 → 验证全链路**，但在产品契约边界上由人把关。

这次落地赛我们认为这个故事**不应该是主推**——主推是 wedge ROI。但它是支撑落地说服力的事实细节：**如果一个产品自己都是这么做出来的，它对应的 wedge 大概率是真的。**

---

## 评委最应该记住的 4 句话（落地版）

1. **0307 那次我们卖"agent 能看见"，这次我们卖"工程师敢离开"。** 后者才有人时收益。
2. **核心 wedge 是契约：prompt → contract → run。** 自然语言不是真理来源，contract 不能落地的 run 直接拒绝启动。
3. **首屏只看变了的。** 8 个场景里 5 个未变化的不上首屏，工程师只审 surfaced case，审查时间从跟产出线性变到跟 ambiguity 线性。
4. **它已经在跑。** 8 个公开在线 demo、127 个 commit、10,440 行测试、CPU + GPU CI 双线、seeded evaluator corpus 锁信任边界。不是 PPT。

---

## 3 分钟答辩稿（落地版）

### `[0:00–0:25]` 痛点重新定义

大家好，我们是 Roboharness 团队。

机器人算法重构是周高频任务。AI agent 已经能写代码，工程师已经习惯让它跑——但有个问题没人解决：**工程师不敢离开屏幕。** 不是因为 agent 写不出代码，是因为没法快速判断它写的对不对。结果是 agent 跑 6 小时 = 工程师盯 6 小时屏幕。capability 增加了，时间没省。

### `[0:25–1:00]` 我们的解法

Roboharness v0.3.0 把这件事重新定义为**信任压缩**：把 2-3 小时无人值守 agent 跑，压缩成工程师 3 分钟最终审批。

做法是 prompt → contract → run 三段：自然语言 prompt 先编译成 JSON contract，每条规则必须申明用 metric 还是 visual 来判、在哪个 phase + view 取证据。编译不通过 run 不许启动。跑完后**只把变了的、模糊的 case 上首屏**，没变的 5 个场景工程师不需要看。

### `[1:00–1:35]` 真实场景

举一个例子：抓取重构任务。旧流程，agent 跑完，工程师挨个看 8 个场景，发现 agent 偷换了 2 个测试场景——人时 6 小时。

新流程，contract 在编译期就把 8 个场景标 immutable，"侧抓+爆破手把"标 anti_goal。Agent 跑完，5 个 PASS 不上首屏，2 个 AMBIGUOUS 自动多收证据，1 个 anti_goal 命中 FAIL——工程师只看这 3 个 case，3 分钟。

5 人组每周 2 次长重构，年节省 ≈ 1.4 个 FTE 的人时。

### `[1:35–2:10]` 它真的在跑

不是 PPT。8 个公开在线 demo，每次 push 到 main 自动重新生成 HTML 报告，链接当场可点。覆盖 MuJoCo grasp、G1 全身 IK、LeRobot native、SONIC locomotion、LeRobot eval CI plugin。10,440 行测试、CPU + GPU 双线 CI，seeded evaluator corpus 锁住"什么算变化"的判断本身。

### `[2:10–2:40]` 跟上次比的进步

距离上次 hackathon 一个多月，127 个 commit，**其中 92.9% 由 Claude 或 Codex 直接产出或在 commit 里有 AI co-author trailer**——同口径下比 0307 时（89.7%）还高。**核心不是堆功能，是把 wedge 整体换了。**0307 时我们卖的是"给 agent 装眼睛"，那是 capability 故事。这次我们卖的是"工程师敢离开屏幕"，这是 ROI 故事。后者更难做，但落地价值高一个数量级。

我们也认真写了适用边界：MJX 大规模并行还没接、装配类精细任务还没验过、preset 数量有限——**敢说 limitation 的项目，主张才靠谱。**

### `[2:40–3:00]` 收尾

Roboharness 的目标不是替工程师写代码，也不是替工程师做决策——是让工程师**敢于让 agent 跑、敢于离开屏幕、敢于用 3 分钟代替 3 小时**。

如果这个 wedge 在你们公司的机器人组成立，每年就有几个 FTE 的人时回到工程师手里去做更重要的事。

谢谢。

---

## 附：评委 5 分钟自助验证路径

如果想立刻验证这个项目不是 PPT：

1. **不装环境就看：** 点开 https://miaodx.com/roboharness/grasp/ ，首屏的 Run Decision banner、Approval Queue、surfaced case 都是真的，不是截图。
2. **5 分钟跑一遍：** `pip install roboharness[demo] && python examples/mujoco_grasp.py --report --contract-preset mujoco_regression_v1` ，本地 `report.html` 就长成你刚看到的样子。
3. **看代码里的契约定义：** [`docs/designs/unattended-refactor-harness-v1.md`](https://github.com/MiaoDX/roboharness/blob/main/docs/designs/unattended-refactor-harness-v1.md) — 整个 wedge 的产品契约、verdict 模型、stop policy 都在这 200 行里。
4. **看自 0307 的工程演进：** 详细路径见同目录 [`EVALUATION_GUIDE.zh-CN.md`](./EVALUATION_GUIDE.zh-CN.md)。
