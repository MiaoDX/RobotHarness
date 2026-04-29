# Roboharness — 落地赛提交（2026-04）

> **一句话 wedge：** 把 Claude Code / Codex 的 **2-3 小时无人值守机器人代码重构**，压缩成工程师 **3 分钟最终审批**。

> **平台报名短描述（<=300字）：**
> 不是再做一个机器人 demo，而是把“AI 改代码我不敢放手”变成“让它自己跑，最后我 3 分钟审批”。Roboharness 会自动盯仿真、抓关键画面、对比 baseline、揪出风险 case，并生成可复核证据包，让 Claude Code / Codex 真正能替团队完成机器人代码重构。

> **飞书排版约定：**
> 这版正文优先使用列表和 code block，不依赖 markdown 表格。
> 推荐插图位置：
> 1. 开头首图：`assets/trust-compression-overview.svg`
> 2. “解决的核心问题”之后：`assets/review-time-compression.svg`
> 3. “三组关键落地证据”之前：`assets/judge-evidence-map.svg`

---

## 团队信息

- 缪东旭 / `miaodongxu` / `miaodongxu@xiaomi.com`
- 丁松 / `dingsong1` / `dingsong1@xiaomi.com`

## 项目链接

- GitHub: https://github.com/MiaoDX/roboharness
- PyPI: `pip install roboharness`
- 在线 demo 总入口: https://miaodx.com/roboharness/
- 上届 hackathon 分支（对照基线）: https://github.com/MiaoDX/roboharness/tree/hackathon/0307

## 评委 30 秒扫读

```text
它是什么：
面向 AI Coding Agent 的机器人仿真 approval harness

它解决什么：
agent 能跑，但工程师不敢离开屏幕

它怎么做：
prompt → contract → run
不能落地的 prompt 直接 fail-closed，不允许 run

为什么值得继续往下看：
它已经有公开 demo、PyPI、HTML report、可复现命令、CI 和 evidence pack
```

## 项目现在到什么程度

> 同口径数据来自同一个 [`classify_commits.py`](./scripts/classify_commits.py) 脚本。

```text
源码（src/）              7,877 行
测试（tests/）            10,440 行
可运行示例                16 个
公开 HTML demo            8 个
自 0307 至今 commit       127
AI 参与度（同口径）        92.9%
CI                        CPU + GPU + Pages + Release
```

这组数字的意义不是“代码很多”，而是说明这个项目已经越过了“概念 demo”的阶段：

- 有公开可点开的 demo 和 report
- 有可执行的安装与复现路径
- 有持续迭代的工程节奏，而不是一次性拼出来的展示品
- 有测试、CI 和 evidence pack 在托底

## 评委可以先关注什么

- 重点不再是“agent 能不能看见机器人”，而是“工程师敢不敢让它自己跑完，再回来审批”。
- 项目不是一次性展示页，而是一层 approval harness。核心是可复核、可回放、可复用的验证基础设施。
- 与 0307 相比，这次材料的重心已经从 capability 故事切到 ROI 和 trust boundary，这更接近落地赛的关注点。
- 如果只想快速判断成熟度，先看在线 demo、复现命令、evidence pack 和 LeRobot plugin。

## 跟 0307 相比，我们换了什么

```text
维度         | 0307                                | 现在（落地赛 / v0.3.0）
核心 wedge   | 给 agent 装眼睛                     | 信任压缩：2-3 小时无人值守 → 3 分钟审批
核心问题     | agent 看不见仿真画面               | 工程师不敢相信 agent 跑出来的结果
运行方式     | 直接 prompt → run                  | prompt → contract → run
输出         | PNG + JSON                         | contract / alarms / approval_report / report.html
判定         | 人肉看结果                         | PASS / FAIL / AMBIGUOUS / CONTRACT_INVALID
信任边界     | 无显式机制                         | seeded evaluator corpus + fail-closed contract
```

## 解决的核心问题

机器人团队现在遇到的不是“AI 能不能写代码”，而是：

> **AI 能跑，但工程师不敢离开屏幕。**

旧流程里，agent 跑 6 小时，工程师也得盯 6 小时，因为没人能快速判断它有没有偷换行为、删测试、顺手把 baseline 改掉。

```text
旧流程：
工程师写 prompt → agent 跑仿真 → 工程师盯 8 个场景看图 → 找偷换行为 → 返工重跑

新流程：
工程师写 prompt → 编译 contract → agent 无人值守运行 → 只审 surfaced cases
```

这件事的价值不在于让 agent “更聪明”，而在于让工程师更快判断它“值不值得信任”。

## 一个具体工作场景：抓取算法重构

假设一个机器人算法工程师收到一个很典型的任务：

> 把“侧抓爆破手把”改成“顶向抓球”，同时已有的 8 个测试场景尽量保持其它行为不变。

如果没有这套 wedge，流程通常会变成：

```text
工程师写 prompt
→ agent 改代码、跑仿真
→ 工程师挨个看 8 个场景截图
→ 人肉判断 agent 有没有偷换行为
→ 发现有问题，再返工重跑
```

真正贵的不是算力，而是工程师要持续盯着看。因为如果 agent 顺手删了测试、偷换了 baseline、或者把失败包装成“看起来差不多”，最后还是得人来兜底。

有了 contract-first approval wedge，流程会变成：

```text
工程师写 prompt
→ 编译 contract（先把目标、不可改部分、anti-goal 写清楚）
→ 编译通过才允许 agent 无人值守运行
→ 跑完后只把 surfaced cases 上首屏
→ 工程师只审真正有风险的 2-3 个 case
```

这就是为什么我们把它叫做“信任压缩”：不是把 agent 换成更炫的模型，而是把原本线性增长的人肉审查时间，压缩到最后几分钟的明确审批动作。

## 核心方案：prompt → contract → run

```text
prompt
  ↓
contract 编译
  - 不 grounded → fail-closed，run 不启动
  - 每条 rule 必须声明 judge + evidence_at
  ↓
run
  ↓
PASS / FAIL / AMBIGUOUS / CONTRACT_INVALID
```

- **`regression` 模式**
  适合重构、优化、清理。旧 baseline 是权威，可见变化默认可疑。

- **`migration` 模式**
  适合明确要新行为的任务，例如侧抓改顶抓。允许 agent 提议新 baseline，但必须由人最后 bless。

- **三类 rule**
  - `metric_gate`：硬性数值/布尔门槛
  - `visual_goal`：应该出现的目标行为
  - `anti_goal`：似是而非的坏行为，命中即 FAIL

这套设计真正重要的地方在于：

- **自然语言 prompt 不再直接充当真理来源**
  先编译成 contract，再启动 run。不能落地的 prompt 直接 fail-closed。

- **变化不再默认被美化**
  在 `regression` 里，可见变化默认可疑；在 `migration` 里，允许新行为，但必须最后由人 bless。

- **证据不再只有“截图看起来不错”**
  每条 rule 都要说明用什么 judge、在哪个 phase/view 取证。最后能落到具体文件和具体证据点。

## 三组关键落地证据

### 1. MuJoCo Approval Wedge

- 在线报告: https://miaodx.com/roboharness/grasp/
- 复现命令：

```bash
pip install roboharness[demo]
python examples/mujoco_grasp.py --report --contract-preset mujoco_regression_v1
```

- 产物不是一句“跑成功了”，而是：

```text
contract.json
alarms.json
approval_report.json
phase_manifest.json
report.html
```

- 这件事的关键不是“能出图”，而是这些文件共同构成了一个**可复核的审批证据包**。评委、工程师、甚至后续接手的人，都可以回到同一批证据上重新判断。

### 2. LeRobot Evaluation Plugin

它已经不只是给人看报告，还能作为第三方训练框架的 CI 阈值卡。

```bash
pip install roboharness[lerobot]
python examples/lerobot_eval_harness.py \
    --checkpoint-path /path/to/lerobot/checkpoint \
    --repo-id lerobot/unitree-g1-mujoco \
    --n-episodes 5 \
    --assert-threshold --min-success-rate 0.8
```

`--min-success-rate` 不达标就 exit code 1，CI 直接 fail。

这说明 Roboharness 不只是一个“展示层”，已经开始变成别的机器人/训练框架可以复用的验证层。

### 3. 两个真实案例

- **qpos 索引案例**
  checkpoint 截图“看起来成功”，但物理约束断言失败，最后定位到 agent 读错了 MuJoCo `qpos` 索引。
  这说明只看图不够，视觉证据和 metric 证据必须结合。

- **seeded evaluator corpus**
  我们专门构造了 `good / bad / ambiguous` 语料，要求：
  - good 全 PASS
  - bad 全 FAIL
  - ambiguous 绝不能被偷渡成 PASS

这不是论文式设计，而是对“信任边界”本身的工程化约束。

- **contract 编译失败时 fail-closed**
  如果 prompt 不能落到 grounded contract，run 不允许启动，并把错误明确写成可读的错误信封。
  这意味着系统不会因为“差不多能理解”就让 agent 冒险往下跑。

### 4. 还有哪些公开 demo 已经在跑

- MuJoCo Approval Wedge: https://miaodx.com/roboharness/grasp/
- G1 Cross-Framework Proof: 证明 Meshcat / MuJoCo 两套视角可以给出 paired 证据
- G1 WBC Reach: https://miaodx.com/roboharness/g1-reach/
- LeRobot Native（GR00T / SONIC）: https://miaodx.com/roboharness/g1-native-groot/ 与 https://miaodx.com/roboharness/g1-native-sonic/
- SONIC Planner: https://miaodx.com/roboharness/sonic-planner/
- SONIC Motion Tracking: https://miaodx.com/roboharness/sonic/
- G1 Locomotion: https://miaodx.com/roboharness/g1-loco/

这些 demo 不是为了“铺数量”，而是说明这套 approval harness 已经跨过单点示例，开始形成一层能复用的验证基础设施。

## 为什么它不止是一个 demo

- 它不是“跑一段机器人视频然后配解说”，而是把 prompt、contract、run、verdict、evidence 组织成了一套完整流程。
- 它不是“只给人看”的截图系统，而是同时给人和 agent 用的证据层。
- 它不是“为了这次 hackathon 临时拼出来的页面”，而是已经有 PyPI、示例、测试、CI、报告站点的持续演进仓库。
- 它不是单个机器人或单个后端的脚本，而是正在形成 protocol、preset、plugin、report 的组合能力。

## 落地价值

如果按一个 5 人机器人算法小组、每周每人 2 次长重构来估算：

```text
旧流程：60h / 周 人工盯屏
新流程：0.5h / 周 人工审批
理论节省：59.5h / 周
年度量级：≈ 1.4 个 FTE
```

这里要诚实说明：

- 这组数字是基于典型工作流的 ROI 推算，不是全公司规模的已结算数据。
- 当前已经被证明的是“这套 wedge 可以跑起来、可以复核、可以插进 CI、可以让工程师只看 surfaced cases”。
- 对落地赛来说，这已经比“只有概念没有证据”高一个层级。

但我们也不想把它包装成一个“已经全面铺开”的故事。更准确的说法是：

- **ROI 模型已经足够清楚**
  评委能看懂节省发生在什么地方，以及为什么它不是简单的“模型更快了”。

- **关键机制已经有工程证据**
  fail-closed、seeded evaluator corpus、approval report、LeRobot plugin 这些都已经落地。

- **下一步是把这套 wedge 从一个成熟 wedge 扩成更多 preset 和更多场景**
  这也是我们把它报到落地赛，而不是只停留在创意赛语境里的原因。

## 适合哪些场景

- **机器人抓取/装配测试自动化**
  长重构之后跑 8-32 个标准场景，工程师只审 surfaced cases。
  当前最成熟的是 MuJoCo grasp 路线，适合用来解释这套 wedge 的核心价值。

- **Sim-to-Real 部署前回归保护**
  代码改动前后跑同一组场景，输出 paired 证据包做对比。
  sim 侧能力已经比较完整，real 侧的 evidence 通道还在继续补。

- **训练曲线之外的策略评估**
  不再只看 success rate，而是给 policy 评估补上视觉和规则证据。
  LeRobot evaluation plugin 就是这件事的直接例子。

- **第三方代码审查 / 外包验收**
  甲方写 contract，乙方交代码，最后用 surfaced cases 说话，而不是靠口头争论。
  这类场景虽然不是本次最成熟的 demo，但从产品形态上很自然延伸得过去。

## 当前边界

- 目前主要在 MuJoCo + G1 + 抓取/移动/到达类任务上验证过。
- sim-to-real 里真机 camera evidence 通道还在硬件验证。
- contract preset 数量还不多，开放式自然语言契约是 fail-closed。
- MJX 大规模并行还没接进这套 wedge。

我们保留这一段，不是为了主动扣自己分，而是想让评委看到这不是“把所有问题都说成已解决”的项目。机器人领域里，敢把边界写清楚，反而更说明团队知道自己在做什么。

## 这个项目自己也是这样做出来的

这个仓库本身也是一次 agentic engineering 实验。自 0307 之后，项目不是靠人类一行行手写堆出来，而是在“人定义目标 + agent 实现 + 人 bless 契约边界”的模式下演进。

```text
自 0307 至今 commit        127
AI 参与度（同口径）         92.9%
AI solo                    77
AI co-authored             41
Human only                  9
```

这不是花絮，而是支撑性证据：如果一个产品主张“agent 干活，人做最后审批”，而它自己也是这样被做出来的，这个 wedge 的可信度会高很多。

## 评委可以优先记住的四点

1. 0307 那次我们卖“agent 能看见”，这次我们卖“工程师敢离开屏幕”。
2. 核心 wedge 是 `prompt → contract → run`，自然语言不是系统里的真理来源。
3. 输出不是一句“跑成了”，而是一整包可复核证据。
4. 项目已经越过了概念 demo 阶段，开始具备作为团队验证基础设施的形态。

## 5 分钟自助验证路径

1. **先看在线 demo**
   https://miaodx.com/roboharness/grasp/

2. **本地跑一遍**

```bash
pip install roboharness[demo]
python examples/mujoco_grasp.py --report --contract-preset mujoco_regression_v1
```

3. **看产品契约**
   https://github.com/MiaoDX/roboharness/blob/main/docs/designs/unattended-refactor-harness-v1.md

4. **看自 0307 以来的演进**
   同目录 [`EVALUATION_GUIDE.zh-CN.md`](./EVALUATION_GUIDE.zh-CN.md)
