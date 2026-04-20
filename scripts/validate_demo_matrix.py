from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python <3.11
    import tomli as tomllib


def main() -> int:
    matrix_path = Path("constraints/demo_matrix.toml")
    if not matrix_path.exists():
        print(f"missing: {matrix_path}")
        return 1

    data = tomllib.loads(matrix_path.read_text())
    demos = data.get("demo", [])
    if not demos:
        print("demo matrix must contain at least one [[demo]] entry")
        return 1

    seen_ids: set[str] = set()
    for index, demo in enumerate(demos, start=1):
        for required in ("id", "entry", "artifact_dir"):
            if not demo.get(required):
                print(f"demo #{index} missing required key: {required}")
                return 1
        demo_id = demo["id"]
        if demo_id in seen_ids:
            print(f"duplicate demo id: {demo_id}")
            return 1
        seen_ids.add(demo_id)

    if "sonic-planner" not in seen_ids:
        print("demo matrix must include sonic-planner")
        return 1

    print(f"demo matrix ok ({len(demos)} demos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
