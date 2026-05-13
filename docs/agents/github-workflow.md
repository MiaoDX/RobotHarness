# GitHub And PR Workflow

## Tooling By Environment

In Claude web/cloud environments, use GitHub MCP tools for issues, PRs,
comments, and check runs when available. The `gh` CLI is usually not authorized
there.

In local CLI/IDE environments, `gh` may be used when already authenticated.

If an MCP tool call fails because the service is temporarily unavailable, wait
briefly and retry before switching approaches.

## PR Review Fixes

When reviewing a PR as an agent or on behalf of one, push fixes directly to the
PR's source branch instead of creating a second branch or separate PR.

Standard loop:

1. Fetch and check out the PR source branch.
2. Make the fix.
3. Run the relevant validation.
4. Commit with a scoped message.
5. Push to the same branch.

This keeps review in one PR and avoids duplicate review threads.

## Branch And Commit Hygiene

- Branch from `main` for normal feature work.
- Use scoped messages such as `feat: ...`, `fix: ...`, `ci: ...`, `docs: ...`,
  or `refactor: ...`.
- Include the required co-author trailer for Codex-created commits:

  ```text
  Co-authored-by: Codex <codex@users.noreply.github.com>
  ```

- Include the corresponding co-author trailer when another AI coding agent
  creates the commit.
