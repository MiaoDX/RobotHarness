---
name: hackathon-ai
description: Agentic Coding Hackathon 2026 CLI Skill。通过 agentic-hackathon 查询项目、评论、作品资料、互动数据，并执行普通用户或评委写入操作。
---

# Agentic Hackathon CLI Skill

## Overview

`agentic-hackathon` 是 Agentic Coding Hackathon 2026 的命令行工具。

- 单文件核心实现：`hackathon-ai-cli.js`
- 可执行入口：`agentic-hackathon`
- 零外部依赖：Node.js 18+ 即可运行
- 支持 Bearer Token 鉴权
- `login` / `auth` / `me` 会返回当前用户身份：`普通用户` / `大众评审` / `评委`

## Setup

推荐先一键安装到全局环境：

```bash
bash install.sh
```

安装完成后可以直接执行：

```bash
agentic-hackathon --help
```

也支持标准全局安装：

```bash
npm install -g .
```

首次登录：

```bash
agentic-hackathon login \
  --token <your-token> \
  --server https://agents.evad.mioffice.cn/ad-hackathon-2026/
```

查看当前身份：

```bash
agentic-hackathon auth
agentic-hackathon me
```

也支持环境变量：

```bash
export AGENTIC_HACKATHON_SERVER=https://agents.evad.mioffice.cn/ad-hackathon-2026/
export AGENTIC_HACKATHON_TOKEN=<your-token>
```

CLI 配置默认保存在 `~/.agentic-hackathon/config.json`。

除 `health`、`login`、`logout` 外，其余命令都建议先完成 `login`。

## Identity Model

- `普通用户`
  - 可查询项目、评论、作品资料、互动信息
  - 可创建项目
  - 可更新/删除自己负责的作品资料
  - 可发表评论/删除自己的评论
- `大众评审`
  - 包含普通用户能力
  - 可查看大众评审白名单相关数据
- `评委`
  - 包含普通用户能力
  - 可访问全部 `judge` 相关查询接口
  - 可提交评委评分
  - 可提交/删除 AI 评分

## Commands

### GET Commands

以下命令对应只读 GET 接口：

| CLI 命令 | 对应接口 | 身份要求 |
| --- | --- | --- |
| `health` | `GET /api/health` | 无 |
| `auth` | `GET /api/auth/verify` | 已登录 |
| `token-status` | `GET /api/auth/token` | 已登录 |
| `me` | `GET /api/projects/users/current` | 已登录 |
| `registration-ai-status` | `GET /api/project-registration-ai/status` | 已登录 |
| `projects` | `GET /api/projects` | 已登录 |
| `project <id>` | `GET /api/projects/:id` | 已登录 |
| `stats` | `GET /api/projects/stats/all` | 已登录 |
| `users` | `GET /api/projects/users/list` | 已登录 |
| `departments` | `GET /api/projects/departments/list` | 已登录 |
| `ai-review-scores` | `GET /api/projects/ai-reviews/scores` | 已登录 |
| `ai-review <projectId>` | `GET /api/projects/:id/ai-review` | 已登录 |
| `comments-stats` | `GET /api/comments/stats/all` | 已登录 |
| `comments <projectId>` | `GET /api/comments/:projectId` | 已登录 |
| `submissions` | `GET /api/submissions` | 已登录 |
| `submission <projectId>` | `GET /api/submissions/:projectId` | 已登录 |
| `interaction <projectId>` | `GET /api/interactions/projects/:projectId` | 已登录 |
| `interaction-stats` | `GET /api/interactions/stats` | 已登录 |
| `interaction-counts` | `GET /api/interactions/counts` | 已登录 |
| `reviewers` | `GET /api/interactions/reviewers` | 已登录 |
| `judge check` | `GET /api/judges/check` | 已登录 |
| `judge score-config` | `GET /api/judges/score-config` | 评委 |
| `judge projects` | `GET /api/judges/projects` | 评委 |
| `judge project <id>` | `GET /api/judges/projects/:projectId` | 评委 |
| `judge my-scores` | `GET /api/judges/scores/my` | 评委 |
| `judge ai-review <projectId>` | `GET /api/judges/ai-review/:projectId` | 评委 |
| `judge rankings` | `GET /api/judges/rankings` | 评委 |

### WRITE Commands

以下命令会修改服务端数据，请谨慎执行：

| 标记 | CLI 命令 | 对应接口 | 身份要求 |
| --- | --- | --- | --- |
| `[WRITE]` | `login --token <token>` | 本地配置写入 + `GET /api/auth/verify` | 无 |
| `[WRITE]` | `logout` | 本地配置写入 | 无 |
| `[WRITE]` | `project-create ...` | `POST /api/projects` | 普通用户/大众评审/评委 |
| `[WRITE]` | `comment <projectId> --content "..."` | `POST /api/comments/:projectId` | 已登录 |
| `[WRITE]` | `comment-delete <projectId> <commentId>` | `DELETE /api/comments/:projectId/:commentId` | 评论作者 |
| `[WRITE]` | `submit <projectId> ...` | `POST /api/submissions/:projectId` | 项目相关成员 |
| `[WRITE]` | `submission-delete <projectId>` | `DELETE /api/submissions/:projectId` | 项目相关成员 |
| `[WRITE]` | `judge score <projectId> --scores ...` | `POST /api/judges/scores/:projectId` | 评委 |
| `[WRITE]` | `judge ai-submit <projectId> --score ...` | `POST /api/judges/ai-review/:projectId` | 评委 |
| `[WRITE]` | `judge ai-delete <projectId> <reviewId>` | `DELETE /api/judges/ai-review/:projectId/:reviewId` | 评委 |

## Scenario Playbooks

### 场景 1：普通用户创建项目

适用情景：

- 你已经在 Web 端生成了 CLI Token
- 你需要通过命令行提交一个新项目报名
- 你希望把队员用户名、标签、业务价值字段一次性带齐

推荐步骤：

```bash
agentic-hackathon login --token <your-token>
agentic-hackathon auth

agentic-hackathon project-create \
  --tracks 创意赛,应用落地赛 \
  --title "Agentic CLI 报名助手" \
  --description "通过 CLI 统一完成报名、资料维护、评审查询等操作。" \
  --expected-users "研发工程师、测试工程师、TPM" \
  --usage-scenarios "项目报名、作品补充、评审进度跟踪" \
  --tags Agent,CLI,提效 \
  --team-members alice,bob \
  --pain-points "报名入口分散、资料更新不集中" \
  --industry-reference "GitHub CLI, Linear CLI"
```

Example：最小创建命令

```bash
agentic-hackathon project-create \
  --tracks 创意赛 \
  --description "让用户用自然语言完成报名和资料维护。" \
  --expected-users "研发工程师" \
  --usage-scenarios "项目报名"
```

### 场景 2：普通用户更新作品资料

适用情景：

- 项目已经创建完成
- 你要补充飞书文档、Git 仓库或只读访问 Token
- 你希望用 CLI 快速迭代材料，而不是每次打开网页

推荐步骤：

先查看当前状态：

```bash
agentic-hackathon submission P001
```

只更新飞书文档：

```bash
agentic-hackathon submit P001 --doc https://mi.feishu.cn/wiki/xxxx
```

只更新 Git 仓库：

```bash
agentic-hackathon submit P001 --git https://github.com/example/repo.git
```

更新 Git 仓库和只读 Token：

```bash
agentic-hackathon submit P001 \
  --git https://github.com/example/repo.git \
  --git-access-token <readonly-token>
```

同时更新文档和 Git：

```bash
agentic-hackathon submit P001 \
  --doc https://mi.feishu.cn/wiki/xxxx \
  --git https://github.com/example/repo.git \
  --git-access-token <readonly-token>
```

更新完成后再次核对：

```bash
agentic-hackathon submission P001
```

### 场景 3：评委提交 AI 评分

适用情景：

- 你是评委
- 你要通过 CLI 或 Agent 工作流把 AI 评分写入系统
- 系统需要通过 Token 严格校验评委权限

Example：

```bash
agentic-hackathon judge ai-submit P001 \
  --score 6.5 \
  --comment "项目完成度较高，建议补充更多用户规模数据。" \
  --model claude-opus-4-6 \
  --mcp-server project-evaluator
```

查看已提交的 AI 评分：

```bash
agentic-hackathon judge ai-review P001
```

## Tips

- 绝大多数 CLI 命令都要求先 `login`
- `auth` 和 `me` 可以快速确认当前身份是否为 `普通用户 / 大众评审 / 评委`
- `--json` 非常适合给 Agent、脚本或流水线消费
- `submit` 当前支持文档和 Git 资料更新；视频上传仍建议通过网页完成
