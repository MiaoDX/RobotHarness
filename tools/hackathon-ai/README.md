# Agentic Hackathon CLI

`agentic-hackathon` 是 Agentic Coding Hackathon 2026 的命令行工具，用于通过 Bearer Token 查询项目、评论、作品资料、互动数据，以及执行普通用户和评委的写入操作。

## Quick Start

推荐先执行一键安装脚本，将 CLI 安装到全局环境：

```bash
bash install.sh
```

安装完成后可以直接在任意目录使用：

```bash
agentic-hackathon --help
```

也支持标准全局安装：

```bash
npm install -g .
```

如果只是本地临时运行，也可以直接执行：

```bash
./agentic-hackathon --help
```

首次登录：

```bash
agentic-hackathon login --token <your-token> --server https://agents.evad.mioffice.cn/ad-hackathon-2026/
```

登录成功后，CLI 会返回当前用户身份：

- `普通用户`
- `大众评审`
- `评委`

查看当前身份：

```bash
agentic-hackathon auth
agentic-hackathon me
```

除 `health`、`login`、`logout` 外，其余命令都默认要求先登录。

## Configuration

支持两组环境变量，优先读取 `AGENTIC_HACKATHON_*`：

```bash
export AGENTIC_HACKATHON_SERVER=https://agents.evad.mioffice.cn/ad-hackathon-2026/
export AGENTIC_HACKATHON_TOKEN=<your-token>
```

用户配置保存在 `~/.agentic-hackathon/config.json`。
仓库中的 [config.json](/Users/zhengao/Desktop/workspace/vibe-coding/ad-hackathon-2026/hackathon-ai/config.json) 仅用于本地开发示例。

## Permission Roles

- `普通用户`：可查询数据，可创建项目、更新作品资料、发表评论。
- `大众评审`：具备普通用户能力，并可查看大众评审相关互动数据。
- `评委`：具备普通用户能力，并可访问 `judge` 相关接口、提交评委评分、提交/删除 AI 评分。

## Command Categories

### GET Commands

- `health`
- `auth`
- `token-status`
- `me`
- `registration-ai-status`
- `projects`
- `project <id>`
- `stats`
- `users`
- `departments`
- `ai-review-scores`
- `ai-review <projectId>`
- `comments-stats`
- `comments <projectId>`
- `submissions`
- `submission <projectId>`
- `interaction <projectId>`
- `interaction-stats`
- `interaction-counts`
- `reviewers`
- `judge check`
- `judge score-config`
- `judge projects`
- `judge project <projectId>`
- `judge my-scores`
- `judge ai-review <projectId>`
- `judge rankings`

### WRITE Commands

以下命令会修改服务端数据：

- `login --token <token> [--server <url>]`
- `logout`
- `project-create --tracks ... --description ... --expected-users ... --usage-scenarios ...`
- `comment <projectId> --content "..."`
- `comment-delete <projectId> <commentId>`
- `submit <projectId> [--doc <url>] [--git <repo>] [--git-access-token <token>]`
- `submission-delete <projectId>`
- `judge score <projectId> --scores '{"category":{"item":7}}'`
- `judge ai-submit <projectId> --score <1-7> --comment "..."`
- `judge ai-delete <projectId> <reviewId>`

## Examples

### 普通用户：创建项目

```bash
agentic-hackathon login --token <your-token>
agentic-hackathon auth

agentic-hackathon project-create \
  --tracks 创意赛,应用落地赛 \
  --title "Agentic CLI 提效助手" \
  --description "通过 CLI 和 Skill 串起报名、作品维护、评审查询等流程。" \
  --expected-users "研发工程师、测试工程师、TPM" \
  --usage-scenarios "项目报名、作品维护、进度跟踪" \
  --tags Agent,CLI,Skill \
  --team-members alice,bob \
  --pain-points "报名和材料维护入口分散" \
  --industry-reference "GitHub CLI, Linear CLI"
```

### 普通用户：更新作品资料

只更新文档：

```bash
agentic-hackathon submit P001 --doc https://mi.feishu.cn/wiki/xxx
```

只更新 Git 仓库：

```bash
agentic-hackathon submit P001 --git https://github.com/example/repo.git
```

同时更新文档、Git 仓库和只读访问 Token：

```bash
agentic-hackathon submit P001 \
  --doc https://mi.feishu.cn/wiki/xxx \
  --git https://github.com/example/repo.git \
  --git-access-token <readonly-token>
```

更新后核对：

```bash
agentic-hackathon submission P001
```

### 评委：提交 AI 评分

```bash
agentic-hackathon judge ai-submit P001 \
  --score 6.5 \
  --comment "项目完成度较高，工具属性明确，建议补充用户规模数据。" \
  --model claude-opus-4-6 \
  --mcp-server project-evaluator
```
