# Roboharness：面向 AI Coding Agent 的机器人仿真可视化验证框架

> 让 Claude Code、Codex 等 AI Coding Agent **看见机器人在做什么**，**判断任务有没有真的成功**，并在真实的仿真反馈里持续迭代。

---

## 0. 一句话介绍

Roboharness 是一个为机器人仿真场景设计的 **agent-first visual harness**：
它不是只记录日志，也不是只做截图，而是把抓取、行走、全身控制等机器人任务拆成语义化阶段，在关键 checkpoint 自动采集多视角图像、状态 JSON、HTML 报告和可恢复快照，让 AI Coding Agent 能基于真实可视结果完成“写代码 → 跑仿真 → 判断成败 → 修改代码 → 再验证”的闭环。

---

## 1. 为什么做这个项目

### 1.1 真实痛点

在机器人研发里，最痛苦的不是“代码写不出来”，而是：

- 机器人任务的成败，很多时候**无法从日志中直接判断**。
- 抓取是否成功、姿态是否稳定、轨迹是否偏、接触是否合理，往往必须靠**看图、看视频、看阶段状态**。
- 一旦进入 AI Coding Agent 时代，这个问题会更严重：
  - agent 会写代码、会改控制器、会搭流程；
  - 但如果只给它日志，它其实**看不见机器人行为本身**；
  - 于是自动迭代很容易退化成“改一版、跑一下、继续猜”。

换句话说，机器人场景真正缺的不是另一个提示词，而是一个让 agent 真正“能看、能判、能回放”的工作环境。

### 1.2 我们的判断

我们相信：

> 对机器人任务来说，**What the agent can't see doesn't exist.**

因此，Roboharness 的核心不是替 agent 写控制代码，而是给 agent 一个足够好的反馈闭环：

- 在哪里停下来观察
- 该看哪些视角
- 如何把状态以结构化方式保存下来
- 如何把失败案例重新拉回到中间阶段继续调
- 如何把结果沉淀成可以复用的报告和评估依据

---

## 2. 项目是什么

Roboharness 是一个 Python 工程化框架，面向机器人仿真中的 AI agent 开发与验证。

### 2.1 它做的事情

1. **语义化任务分阶段**
   - 例如抓取任务不是笼统地“跑完一遍”，而是拆成：
   - `plan → pre_grasp → approach → grasp → lift → place → home`

2. **关键阶段自动抓取多视角结果**
   - 在 checkpoint 处自动保存：
   - RGB 图像
   - 状态 JSON
   - 元数据
   - 可恢复仿真快照

3. **生成 agent 可消费的结果包**
   - PNG + JSON + HTML 报告
   - 既适合人看，也适合 Claude Code、Codex 等 agent 再处理

4. **支持恢复与继续迭代**
   - agent 失败后可以从 checkpoint 恢复
   - 不必每次从头重跑完整任务

5. **支持后续评估与趋势分析**
   - 报告聚合
   - 约束评估
   - 成功率趋势比较

### 2.2 它不做什么

Roboharness 不负责替代你的控制算法，也不强绑某一个机器人平台。

它做的是一层 **harness / validation layer**：

- 控制逻辑由你自己或 AI agent 编写
- 仿真后端可以替换
- Roboharness 负责 `pause → capture → restore → report → evaluate`

这使它天然适合作为机器人研发里的“观察层”和“验证层”。

---

## 3. 为什么它值得参加这个黑客松

### 3.1 它不是 PPT，而是已经跑起来的工程

当前仓库已经具备：

- MuJoCo 抓取示例
- G1 humanoid WBC reach 示例
- LeRobot 原生环境接入
- SONIC locomotion 路线
- HTML 报告生成
- CLI 评估与趋势分析
- CI 自动化验证

仓库首页已经把 demo、动画、架构图、在线 visual reports 和运行命令放出来了，具备比较强的“可展示性”和“可验证性”。

### 3.2 它不是通用 demo，而是一个可复用的基础设施层

很多项目能做出一个机器人演示，但很难把它沉淀成：

- 可复用 API
- 可扩展 backend
- 可 checkpoint 恢复
- 可自动报告
- 可接入 agent 工作流

Roboharness 的价值恰恰在这里：

> 它不是在做“单次秀肌肉”，而是在做机器人 Agent 开发的公共地基。

### 3.3 它同时具备“创意性”和“落地性”

**创意性**在于：

- 它把“harness engineering”从网页/软件工程，迁移到了机器人仿真场景。
- 它不依赖单独 VLM，而是直接把 Claude Code / Codex 这样的多模态 coding agent 变成机器人任务的观察者与评估者。

**落地性**在于：

- 它直接服务于机器人算法开发、仿真回归测试、PR 验证、失败定位。
- 它非常适合内部机器人团队、仿真平台团队、测试团队作为研发效能基础设施使用。

---

## 4. 当前能力与代表性场景

### 4.1 支持不同机器人与平台的测试

Roboharness 不是只服务于单一 demo，而是在尽量形成一层可复用的机器人验证基础设施。当前已经覆盖或明确支持的对象包括：

- **不同机器人形态**：2 指夹爪抓取任务、Unitree G1 humanoid、G1 native LeRobot 场景
- **不同仿真/接入平台**：MuJoCo、LeRobot 原生 `make_env()`、Gymnasium wrapper、Isaac Lab compatibility 路线
- **不同可视化/验证后端**：Meshcat 3D、HTML report、结构化 PNG + JSON 输出、Rerun logging 路线
- **不同任务类型**：grasp、whole-body reach、locomotion、motion tracking

这意味着它不是一个只对单个机器人写死的展示脚本，而是一个正在形成中的统一 harness 层。

### 4.2 MuJoCo Grasp

这是当前最适合展示的代表场景。

价值在于：

- 抓取任务的阶段性非常明显
- 多视角画面能直观看到成功/失败
- 非常适合说明“为什么 agent 不能只看日志”
- HTML report 和 checkpoint 结构很完整，最适合作为评委第一眼 demo

推荐展示路径：

- front view GIF
- top-down GIF
- pre_grasp / grasp / lift 三张静态图
- HTML checkpoint 报告

### 4.3 G1 Humanoid WBC Reach

说明 Roboharness 不是只会抓方块，而是可以进入更复杂的人形机器人全身控制场景。

价值在于：

- 展示多阶段姿态控制
- 展示 agent 对复杂机器人行为的观察与验证能力
- 说明项目可向更复杂控制问题扩展

### 4.4 G1 Locomotion 与 Native LeRobot

这两条线非常关键，因为它们说明项目不是停留在 toy task，而是在往更真实、更标准化、更接近生态接入的路径发展：

- **G1 Locomotion**：展示 stand → walk → stop 的 locomotion 验证能力
- **Native LeRobot**：说明项目可以接入 LeRobot 官方 `make_env()` 工厂，而不是只运行自定义 world

它们共同说明：Roboharness 不只是“会截图”，而是在朝统一机器人验证层演进。

### 4.5 SONIC 路线

SONIC 相关工作说明项目并不满足于单个 demo，而是在持续探索：

- locomotion
- motion tracking
- 更复杂控制路径
- 更长期的能力演进

这会让评委感受到项目不是一次性 hack，而是一条明确的产品/技术路线。

### 4.6 现有 HTML Demo / Live Reports

这部分建议你在飞书文档里单独放一页，因为它非常吸引人。

当前仓库已经有一整套公开可访问的 HTML demo / visual reports：

- 总入口：`https://miaodx.com/roboharness/`
- MuJoCo Grasp：`https://miaodx.com/roboharness/grasp/`
- G1 WBC Reach：`https://miaodx.com/roboharness/g1-reach/`
- G1 Locomotion：`https://miaodx.com/roboharness/g1-loco/`
- G1 Native LeRobot：`https://miaodx.com/roboharness/g1-native/`
- SONIC Motion Tracking：`https://miaodx.com/roboharness/sonic/`

这些页面不是静态手工摆拍，而是由 GitHub Pages 工作流自动构建：每次推送到 `main`，CI 会跑示例、生成 HTML report、整理 checkpoint 资源，并把结果部署成可直接浏览的 demo 站点。

这件事对评委的感知价值非常高，因为它把“项目能跑”变成了“项目能被直接看到、直接点开、直接验证”。

---

## 5. 这个项目最独特的地方：它本身就是一次 Agentic Development 实验

这一点建议在答辩时重点强调，因为这不是普通意义上的“AI 辅助编程”，而是一种极端而完整的 agentic engineering 实践。

### 5.1 没有一行手写代码

这个项目最值得讲的一点是：

> **没有一行手写代码。**

我们对这个仓库采用了一个极端约束：

- 人类不直接手写功能代码
- 人类负责定义目标、拆 issue、给出验收口径、做最终取舍
- 代码实现交给 agent 在云端完成

这让项目本身就成为一个很强的示范：不是“做了一个 AI 相关项目”，而是“用 AI agent 真正把项目做出来”。

### 5.2 Claude 负责项目规划与 steering

在这套开发方式里，Claude 承担的是高层规划与 steering 的角色：

- 帮助定义项目方向和阶段目标
- 帮助把想法整理成 issue / ticket
- 帮助进行方案比较、路线收敛和任务拆解
- 帮助在开发过程中持续 steer：当前应该先做什么、如何裁剪范围、哪里该补文档、哪里该补验证

所以在项目叙事上，可以非常明确地说：

> Claude 不是一个写几段代码的助手，而是在承担项目规划和技术 steering 的工作。

### 5.3 Claude Code 与 Codex 在云端执行编码

实际编码执行层面，主要由 Claude Code 与 Codex 在云端完成：

- 新功能实现
- 文档生成与改写
- CI 修复
- 示例补充
- 代码重构
- PR 产出与后续修正

这意味着项目的实现过程不是本地 IDE 里的人肉 coding，而是一个真正的 cloud agent workflow。

### 5.4 GitHub 云端 CI + Cirun / AWS GPU CI

验证层面，我们也尽量采用云端基础设施，而不是只靠本地机器：

- **GitHub 云端 CI**：负责 lint、类型检查、pytest、多 Python 版本测试、MuJoCo 示例验证、GitHub Pages 部署
- **Cirun + AWS GPU CI 路线**：面向需要 GPU 的更重型仿真/评测场景，把 GPU runner 放到云端按需拉起

这个组合的意义在于：

- 开发在云端 agent 上完成
- 验证在云端 CI 上完成
- 结果通过 HTML demo / visual report 被直接发布出来

整个链路天然适合黑客松，也天然适合后续规模化演进。

### 5.5 从当前 git 历史看，Claude 完成了大部分提交

基于当前仓库本地 `git log` 统计：

- 总提交数：`102`
- 署名为 Claude 的提交数：`92`
- 占比约：`90.2%`

这基本可以支撑一句非常有力的话：

> 这个仓库的绝大多数 PR / 实现工作，都是由 Claude 体系 agent 在云端完成的。

### 5.6 这是一个典型的 issues-driven 开发仓库

从当前仓库历史和文档能看到很强的 issue 驱动特征：

- 需求、阶段目标和技术路线被持续挂到 GitHub Issues 上
- Claude 参与规划和 steer
- Claude Code / Codex 根据 issue 落地代码与 PR
- 功能提交和文档更新直接围绕 issue 编号推进

这与“issue-driven development”最理想的形态非常接近。

### 5.7 它的开发闭环很适合 hackathon 主题

这个项目的实际开发闭环可以概括为：

1. 人类提出问题与方向
2. Claude 帮助规划、拆解、steer
3. 形成 issue / ticket
4. Claude Code 与 Codex 云端接手实现
5. PR 进入仓库
6. GitHub 云端 CI 做 lint / test / example / pages 验证
7. GPU 场景由 Cirun + AWS GPU CI 路线承接
8. HTML demo / visual report 作为 proof-of-work 输出
9. 再回到下一个 issue

这是一种非常完整、非常 hackathon-friendly 的 agentic workflow：

- 有目标
- 有 agent
- 有执行
- 有验证
- 有留痕
- 有可展示结果
- 有持续演进

---

## 6. 为什么说它是“有真实落地意义”的

### 6.1 直接面向真实研发环节

Roboharness 的场景不是虚构的。

它对应的是机器人研发里非常真实的一条链路：

- 控制器开发
- 仿真调试
- 回归验证
- 行为问题定位
- 失败样本复盘
- PR 验证与持续集成

这些工作现在很多还高度依赖人工肉眼检查与手工记录。
Roboharness 把它工程化、结构化、agent-friendly 化了。

### 6.2 它的目标用户很明确

目标用户不是泛化到所有人，而是聚焦在：

- 机器人算法工程师
- 仿真平台工程师
- 机器人测试工程师
- 使用 Claude Code / Codex / Cursor 的 AI 编程团队

这意味着它不是“大而空”的平台叙事，而是一个边界清晰、价值明确、可以逐步做深的工具型产品。

### 6.3 适合作为内部基础设施

如果落到公司内部，它可以成为：

- 机器人仿真任务的验证层
- agent 自动迭代的观测层
- PR 的行为回归层
- 失败案例的复盘层
- demo / benchmark / evaluation 的统一结果层

这类工具未必面向所有员工，但对于目标团队来说是高价值基础设施。

---

## 7. 为什么这个 repo 的故事对评委有吸引力

### 7.1 它同时满足“能讲”和“能证”

很多项目只能讲故事，不能证据化；
很多工具只能跑代码，但不容易展示。

Roboharness 两者兼备：

- 有非常清晰的故事：让 AI 看见机器人
- 有直观的视觉证据：GIF、PNG、HTML report
- 有工程证据：CI、测试、结构化代码、公开 repo
- 有路线证据：issue-driven roadmap
- 有开发范式证据：Claude Code 云端做大部分 PR

### 7.2 它代表的是一个趋势，而不是一个孤立需求

随着 Claude Code、Codex、Cursor 这类 agent 越来越强，
“给 agent 提供好的工作环境”会比“给 agent 写更长的 prompt”更重要。

Roboharness 正好踩在这个趋势上：

- 在软件工程里，这叫 harness engineering
- 在机器人仿真里，这件事才刚刚开始

所以它很有“方向感”。

### 7.3 它很适合黑客松语境下的亮点表达

你可以非常自然地把它包装成：

- 一个机器人研发基础设施项目
- 一个 agent-first 开发方法论样板
- 一个 issues-driven、cloud Claude-powered 的真实工程案例

这个组合非常容易打动评委。

---

## 8. GitHub 文档与 issue 线索整理

为了准备这次材料，我专门对仓库现有内容做了梳理，当前最值得讲的几条线索是：

### 8.1 README 已经具备很强展示性

README 里已经包含：

- 项目定位一句话
- 多个 demo 场景
- GIF 和静态图
- 架构图
- live visual reports 链接
- quick start

这意味着你不是从零开始补包装，而是在把一个已经成型的项目故事进一步打磨。

### 8.2 仓库内已有“方法论文档”

当前 repo 里已有多份非常有价值的辅助材料：

- `ARCHITECTURE.md`
- `docs/context.zh-CN.md`
- `docs/context.en.md`
- `docs/harness-engineering-insights.md`
- `docs/strategic-direction-review-2026-04.md`

这些文档的价值在于：

- 它们证明项目并不是“边写边碰运气”
- 而是有比较明确的技术判断、方法论总结和中长期方向

### 8.3 GitHub Issues 明确体现了路线演进

从现有 issue 与 issue 关联提交可以看到，这个项目不是一次性写完，而是在持续演进。比较适合在飞书文档里直接引用的代表 issue 包括：

- `#83` Add native LeRobot env creation support（https://github.com/MiaoDX/roboharness/issues/83）
- `#86` SONIC locomotion Phase 1 — planner-only control pipeline（https://github.com/MiaoDX/roboharness/issues/86）
- `#92` SONIC locomotion Phase 2 — encoder+decoder tracking pipeline（https://github.com/MiaoDX/roboharness/issues/92）

再结合本地提交历史，还能看到这些更早期的 issue 驱动痕迹：

- `#81` Unitree / real-robot communication 路线
- `#34` G1 WBC reach 与多视角页面能力
- `#4` Isaac Lab compatibility
- `#2` MuJoCo grasp 端到端示例

这使得项目的“成长性”非常可讲：不是先做一个大而全的闭门项目，而是围绕 issue 持续演进、不断把能力补齐。

---

## 9. 建议在飞书文档里重点强调的句子

如果你要把这份内容转成飞书文档，建议优先保留以下几句金句：

### 9.1 标题句

> Roboharness：面向 AI Coding Agent 的机器人仿真可视化验证框架

### 9.2 核心价值句

> 它让 AI agent 不再只看日志，而是真正看见机器人在做什么。

### 9.3 方法论句

> 我们不是在替 agent 写控制代码，而是在给 agent 建一个可观察、可判断、可回放、可验证的工作环境。

### 9.4 开发方式句

> 这个仓库本身就是一次 agentic development 实验：人类以 GitHub Issues 驱动方向，Claude Code 云端完成绝大多数 PR，最终由 CI 和 visual report 共同验收。

### 9.5 落地句

> 它不是另一个机器人 demo，而是一层可以进入真实研发流程的验证基础设施。

---

## 10. 建议的 3 分钟答辩结构

### 第一段：问题（30 秒）

“机器人任务是否成功，很多时候看日志根本看不出来。抓没抓住、走没走稳、轨迹偏没偏，都必须看画面。AI Coding Agent 更是如此——如果只给它日志，它其实看不见机器人。”

### 第二段：方案（45 秒）

“Roboharness 做的事情，就是把机器人任务拆成语义 checkpoint，在关键阶段自动抓取多视角图像、状态和报告，让 Claude Code、Codex 等 agent 可以基于真实视觉结果持续迭代控制代码。”

### 第三段：证明它是真的（45 秒）

“这个项目已经有 MuJoCo grasp、G1 reach、LeRobot native、SONIC 等多个场景；有 CI、有 live reports、有 issue-driven 路线；不是 PPT，而是已经在跑的工程。”

### 第四段：最特别的一点（30 秒）

“更特别的是，这个仓库本身就是按 agentic workflow 开发的：GitHub Issues 驱动方向，Claude Code 云端做了大部分 PR，CI 和 visual reports 做结果验收。”

### 第五段：落地价值（30 秒）

“所以 Roboharness 的意义不只是做一个 demo，而是在给机器人研发团队提供一层 agent-first 的验证基础设施。”

---

## 11. 团队信息

- 缪东旭 / `miaodongxu` / `miaodongxu@xiaomi.com`
- 丁松 / `dingsong1` / `dingsong1@xiaomi.com`

---

## 12. 推荐的最终报名口径

### 推荐赛道

- 创意赛
- 应用落地赛

### 推荐标签

- 机器人仿真
- AI Agent
- 可视化验证
- 自动评测
- MuJoCo
- 研发效能

### 推荐结尾口径

> Roboharness 的核心价值，不是替代工程师，也不是替代控制算法，而是为 AI Coding Agent 提供机器人研发所缺失的那层“可见、可判、可回放、可验证”的工作环境。它既是一个机器人验证框架，也是一个用 Claude Code 云端和 GitHub Issues 驱动出来的真实 agentic engineering 样板。
