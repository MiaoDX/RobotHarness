# Release Runbook

Releases are cut by pushing to the `release` branch, which triggers
`.github/workflows/release.yml` to tag, create a GitHub Release, build, and
publish to PyPI through OIDC trusted publishing.

The workflow also supports `workflow_dispatch`, but the normal project flow is
still: merge release changes to `main`, then explicitly advance the `release`
branch as a deploy pointer.

## Critical Rules

- The `release` branch has unrelated git history and exists only as a deploy
  pointer.
- Never open a PR targeting `release`; GitHub cannot merge unrelated histories.
- Force-pushing `release` is intentional, but requires explicit user
  authorization each time.
- Keep the version in both `pyproject.toml` and `src/roboharness/__init__.py`
  synchronized.
- Do not reuse a version number after a PyPI upload failure. Bump to the next
  patch instead.

## Standard Flow

1. Bump the version in `pyproject.toml` and `src/roboharness/__init__.py` on a
   feature branch.
2. Open a PR targeting `main`, not `release`.
3. Include release notes in the PR description.
4. After CI is green and the PR is merged to `main`, ask for explicit approval
   to advance the `release` pointer.
5. Push `release` to `main`'s tip:

   ```bash
   git fetch origin main
   git push origin +origin/main:release
   ```

   Equivalent local form:

   ```bash
   git push --force origin main:release
   ```

6. Watch `.github/workflows/release.yml`.
7. Verify the tag, GitHub Release, and PyPI artifact before closing out.

## What The Workflow Does

On push to `release`, the workflow:

1. Reads the version from `pyproject.toml`.
2. Fails if the corresponding `vX.Y.Z` tag already exists.
3. Updates `pyproject.toml` and `src/roboharness/__init__.py` if needed.
4. Commits the version bump if there was a generated change.
5. Creates and pushes the tag.
6. Creates a GitHub Release with generated notes.
7. Builds and verifies the wheel.
8. Publishes to PyPI.

## PyPI Environment Protection

The publish step uses the `pypi` GitHub environment. Its deployment branch/tag
rules must allow the `release` branch, and should allow `v*` if tag-triggered
publishing is introduced later.

If the workflow fails immediately with a message like `Branch 'release' is not
allowed to deploy to pypi due to environment protection rules`, fix the
environment settings in GitHub, then re-run the failed job.

## Dependency Metadata Constraint

PyPI rejects packages that declare direct git dependencies such as
`pkg @ git+https://...`, even inside optional extras. `allow-direct-references =
true` only silences build-time checks; PyPI still refuses the upload.

Install fork or git-only dependencies in a separate workflow, Dockerfile, or doc
step instead of declaring them in `[project.optional-dependencies]`.

## End-To-End Verification

A successful GitHub Release and tag do not prove PyPI publication succeeded.
The workflow creates those before building and uploading the wheel.

Always verify all three:

1. Tag: `https://github.com/MiaoDX/roboharness/tags`
2. GitHub Release: `https://github.com/MiaoDX/roboharness/releases/tag/vX.Y.Z`
3. PyPI artifact: `https://pypi.org/project/roboharness/X.Y.Z/`

Useful JSON check:

```bash
curl -s https://pypi.org/pypi/roboharness/json | jq -r .info.version
```

If PyPI publish fails after tag/release creation, keep those historical markers
and release the fix as the next patch version.
