#!/usr/bin/env python3
"""Generate the roboharness/showcase repository structure.

Creates a complete, ready-to-push directory with:
  - Root README.md with overview and instructions
  - lerobot-g1/ showcase (adapted from examples/lerobot_g1_native.py)
  - Placeholder directories for future showcases
  - CI workflow (.github/workflows/showcase-ci.yml)
  - Org profile README (.github-org/profile/README.md)

Usage:
    python scripts/init-showcase-repo.py [OUTPUT_DIR]

The default output directory is ``./showcase-output``. Run from the
roboharness repo root so the script can find ``examples/lerobot_g1_native.py``.

See: https://github.com/MiaoDX/roboharness/issues/139
"""

from __future__ import annotations

import argparse
import shutil
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
LEROBOT_EXAMPLE = REPO_ROOT / "examples" / "lerobot_g1_native.py"

SHOWCASE_DIRS = [
    "groot-n16",
    "pi0-libero",
    "lerobot-g1",
    "sonic-locomotion",
    "capx-comparison",
]

# ---------------------------------------------------------------------------
# File content generators
# ---------------------------------------------------------------------------


def _root_readme() -> str:
    rows = []
    for d in SHOWCASE_DIRS:
        desc = "LeRobot G1 native locomotion demo" if d == "lerobot-g1" else "Coming soon"
        status = "Ready" if d == "lerobot-g1" else "Planned"
        rows.append(f"| [{d}]({d}/) | {desc} | {status} |")
    showcase_table = "\n".join(rows)
    return textwrap.dedent(f"""\
        # roboharness/showcase

        Standalone demo integrations for
        [roboharness](https://github.com/MiaoDX/roboharness) --- the visual
        testing harness for AI coding agents in robot simulation.

        Each directory is a self-contained showcase that pip-installs
        `roboharness` and runs independently. No submodules, no monorepo
        coupling.

        ## Showcases

        | Directory | Description | Status |
        |-----------|-------------|--------|
        {showcase_table}

        ## Quick start

        ```bash
        cd lerobot-g1
        pip install -r requirements.txt
        bash run.sh
        ```

        ## Design principles

        - **Self-contained**: each showcase has its own `requirements.txt`,
          `run.sh`, and main script
        - **roboharness is a pip dependency**: always uses the latest PyPI release
        - **Independent CI**: one job per showcase, failures don't block others
        - **Minimal coupling**: no git submodules, no shared code between showcases

        ## Adding a new showcase

        1. Create a new directory: `my-showcase/`
        2. Add `README.md`, `requirements.txt`, `run.sh`, and your main script
        3. Add the directory to the CI matrix in `.github/workflows/showcase-ci.yml`
        4. Open a PR

        ## License

        MIT --- same as [roboharness](https://github.com/MiaoDX/roboharness).
    """)


def _ci_workflow() -> str:
    return textwrap.dedent("""\
        name: Showcase CI

        on:
          push:
            branches: [main]
          pull_request:

        jobs:
          showcase:
            strategy:
              fail-fast: false
              matrix:
                include:
                  - name: lerobot-g1
                    dir: lerobot-g1
                    # Future showcases:
                    # - name: groot-n16
                    #   dir: groot-n16
                    # - name: sonic-locomotion
                    #   dir: sonic-locomotion

            name: ${{ matrix.name }}
            runs-on: ubuntu-latest
            env:
              MUJOCO_GL: osmesa

            steps:
              - uses: actions/checkout@v4

              - uses: actions/setup-python@v5
                with:
                  python-version: "3.10"

              - name: Install system deps (OSMesa for headless MuJoCo)
                run: |
                  sudo apt-get update
                  sudo apt-get install -y libosmesa6-dev libgl1-mesa-glx

              - name: Install Python deps
                run: |
                  cd ${{ matrix.dir }}
                  pip install -r requirements.txt

              - name: Run showcase
                run: |
                  cd ${{ matrix.dir }}
                  bash run.sh
    """)


def _lerobot_readme() -> str:
    return textwrap.dedent("""\
        # LeRobot G1 Native Locomotion

        Demonstrates [roboharness](https://github.com/MiaoDX/roboharness) integration with
        LeRobot's official `make_env("lerobot/unitree-g1-mujoco")` factory.

        Runs the Unitree G1 43-DOF humanoid through stand, walk, and stop phases using
        GR00T or SONIC locomotion controllers, capturing multi-camera checkpoint screenshots
        via `RobotHarnessWrapper`.

        ## Requirements

        - Python 3.10+
        - MuJoCo with OSMesa for headless rendering (CI), or a display (local)

        ## Quick start

        ```bash
        pip install -r requirements.txt
        bash run.sh
        ```

        ## Run options

        ```bash
        # GR00T controller (default)
        MUJOCO_GL=osmesa python lerobot_g1_native.py --controller groot --report

        # SONIC controller
        MUJOCO_GL=osmesa python lerobot_g1_native.py --controller sonic --report
        ```

        ## Output

        ```
        harness_output/lerobot_g1_native_groot/trial_001/
            initial/   -- robot standing after reset
            walking/   -- controller walking forward
            final/     -- final stopped state
        ```

        Each checkpoint directory contains multi-camera PNG screenshots and a `state.json`
        with joint angles, step count, and reward.

        ## What this demonstrates

        - **Zero-change Gymnasium wrapper**: `RobotHarnessWrapper` wraps the LeRobot env
        - **Multi-camera capture**: screenshots from all MuJoCo cameras at each checkpoint
        - **Task protocol**: structured phases (initial/walking/final) with automatic triggering
        - **HTML reports**: self-contained visual report for agent consumption

        ## References

        - [roboharness](https://github.com/MiaoDX/roboharness)
        - [lerobot/unitree-g1-mujoco](https://huggingface.co/lerobot/unitree-g1-mujoco)
        - [LeRobot](https://github.com/huggingface/lerobot)
    """)


def _lerobot_requirements() -> str:
    return textwrap.dedent("""\
        roboharness[demo]
        lerobot
        torch --index-url https://download.pytorch.org/whl/cpu
        PyYAML
    """)


def _lerobot_run_sh() -> str:
    return textwrap.dedent("""\
        #!/usr/bin/env bash
        set -euo pipefail

        # Default to headless rendering if no display is available
        export MUJOCO_GL="${MUJOCO_GL:-osmesa}"

        echo "=== LeRobot G1 Native Showcase ==="
        echo "Controller: groot (default)"
        echo "MUJOCO_GL=$MUJOCO_GL"
        echo ""

        python lerobot_g1_native.py --controller groot --report --assert-success
    """)


def _placeholder_readme(name: str) -> str:
    return textwrap.dedent(f"""\
        # {name}

        *Coming soon.* This showcase is planned but not yet implemented.

        See the [main README](../README.md) for the full showcase list.

        Want to contribute? Open an issue at
        [roboharness/showcase](https://github.com/roboharness/showcase/issues).
    """)


def _org_profile_readme() -> str:
    return textwrap.dedent("""\
        ## roboharness

        **Visual testing harness for AI coding agents in robot simulation.**

        Let Claude Code and Codex *see* what the robot is doing, *judge* if it's working,
        and *iterate* autonomously.

        | Repository | Description |
        |------------|-------------|
        | [roboharness][rh] | Core: harness, wrappers, backends, evaluation |
        | [showcase][sc] | Standalone demos (GR00T, LeRobot, SONIC, Pi0) |

        [rh]: https://github.com/MiaoDX/roboharness
        [sc]: https://github.com/roboharness/showcase

        ### Links

        - [Live Visual Reports](https://miaodx.com/roboharness/)
        - [PyPI](https://pypi.org/project/roboharness/)
        - [Documentation](https://github.com/MiaoDX/roboharness/tree/main/docs)
    """)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the roboharness/showcase repository structure"
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="./showcase-output",
        help="Target directory (default: ./showcase-output)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output directory",
    )
    args = parser.parse_args()

    output = Path(args.output_dir).resolve()

    if output.exists() and not args.force:
        print(f"Error: {output} already exists. Use --force to overwrite.")
        sys.exit(1)

    if output.exists() and args.force:
        shutil.rmtree(output)

    # Check that the source example exists
    if not LEROBOT_EXAMPLE.exists():
        print(f"Error: cannot find {LEROBOT_EXAMPLE}")
        print("Run this script from the roboharness repo root.")
        sys.exit(1)

    print(f"Generating showcase repo in: {output}")

    # Create directory structure
    for d in SHOWCASE_DIRS:
        (output / d).mkdir(parents=True, exist_ok=True)
    (output / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (output / ".github-org" / "profile").mkdir(parents=True, exist_ok=True)

    # Root files
    (output / "README.md").write_text(_root_readme())
    (output / ".github" / "workflows" / "showcase-ci.yml").write_text(_ci_workflow())

    # Org profile README (for roboharness/.github repo)
    (output / ".github-org" / "profile" / "README.md").write_text(_org_profile_readme())

    # lerobot-g1 showcase (the first real showcase)
    lerobot_dir = output / "lerobot-g1"
    shutil.copy2(LEROBOT_EXAMPLE, lerobot_dir / "lerobot_g1_native.py")
    (lerobot_dir / "README.md").write_text(_lerobot_readme())
    (lerobot_dir / "requirements.txt").write_text(_lerobot_requirements())
    run_sh = lerobot_dir / "run.sh"
    run_sh.write_text(_lerobot_run_sh())
    run_sh.chmod(0o755)

    # Placeholder showcases
    for d in SHOWCASE_DIRS:
        if d == "lerobot-g1":
            continue
        (output / d / "README.md").write_text(_placeholder_readme(d))

    # Summary
    print("\nGenerated structure:")
    for p in sorted(output.rglob("*")):
        if p.is_file():
            rel = p.relative_to(output)
            print(f"  {rel}")

    print("\nDone! To use:")
    print("  1. Create the repo: gh repo create roboharness/showcase --public")
    print(f"  2. cd {output}")
    print("  3. git init && git add -A && git commit -m 'Initial showcase structure'")
    print("  4. git remote add origin git@github.com:roboharness/showcase.git")
    print("  5. git push -u origin main")
    print("\n  Org profile README is in .github-org/ -- copy to roboharness/.github repo.")


if __name__ == "__main__":
    main()
