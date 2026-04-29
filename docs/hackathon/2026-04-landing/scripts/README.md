# AI Commit Classifier

一个简单的脚本，用于把仓库 commit 历史按 **AI 参与程度** 分类，给落地赛主提交文档里的"开发方式"数字提供可复现性。

## 为什么需要它

`git log --pretty=format:"%an"` 只看 author 名字会低估 AI 参与度——很多本地用 Claude Code / Codex 跑出来的 commit，author 显示成本人，但 commit body 里其实有：

- `Co-Authored-By: Claude <noreply@anthropic.com>`
- `Co-authored-by: Codex <codex@users.noreply.github.com>`
- `🤖 Generated with Claude Code`
- `https://claude.ai/code/session_xxx`

所以正确的分类需要**同时看 author 和 commit body trailer**。

## 使用

```bash
# 1. 导出 commit 数据（默认 main 分支）
git log --pretty=format:"===%H===%n%an%n%B%n---" > /tmp/commits.txt

# 2. 跑分类器
python3 docs/hackathon/2026-04-landing/scripts/classify_commits.py /tmp/commits.txt

# 想跑特定区间（例如自 0307 至今）
git log origin/hackathon/0307..origin/main \
    --pretty=format:"===%H===%n%an%n%B%n---" > /tmp/since_0307.txt
python3 docs/hackathon/2026-04-landing/scripts/classify_commits.py /tmp/since_0307.txt
```

## 分类口径

| 类别 | 判定规则 |
|------|---------|
| `ai_solo` | author == `Claude` 或 `Codex` |
| `ai_coauthored` | author 是人，但 body 含 `Co-Authored-By: Claude` / `Co-authored-by: Codex` / `Generated with Claude Code` / `claude.ai/code` URL |
| `bot` | author == `github-actions[bot]` |
| `human_only` | 以上都不是 |

**AI 参与度 = ai_solo + ai_coauthored**（落地赛文档使用的口径）。

## 当前主分支（main）实测结果（2026-04-29）

| 区间 | 总 commit | AI solo | AI co-authored | Bot | Human only | **AI 参与合计** |
|------|----------|---------|----------------|-----|------------|----------------|
| 0307 时（branch `hackathon/0307`） | 107 | 96（89.7%）| 0 | 1 | 10 | **89.7%** |
| 当前 main | 229 | 169（73.8%）| 41（17.9%）| 1 | 18 | **91.7%** |
| 自 0307 至今 | 127 | 77（60.6%）| 41（32.3%）| 0 | 9 | **92.9%** |

## 解读

数字本身在 0307 → 当前期间从 89.7% 上升到 92.9%。但**更值得看的是模式变化**：

- 0307 时几乎全部是"Claude 直接 author" = agent 一把梭
- 现在 ~32% 是"MiaoDX author + Codex 协作 trailer" = **人在 loop 里 bless agent 产出**

这跟项目当前 wedge（contract-first approval gate）叙事一致：agent 负责干活，人负责契约边界和最终 bless，不是 agent 全自动也不是人手写。
