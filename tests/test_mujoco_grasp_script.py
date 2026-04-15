from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("mujoco")

from examples import mujoco_grasp


def test_main_fails_fast_without_display_or_gl_backend(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class UnexpectedBackendInit:
        def __init__(self, *args, **kwargs) -> None:
            raise AssertionError("backend should not be constructed")

    monkeypatch.setattr(mujoco_grasp, "MuJoCoMeshcatBackend", UnexpectedBackendInit)
    monkeypatch.setattr(sys, "argv", ["mujoco_grasp.py", "--output-dir", str(tmp_path)])
    monkeypatch.delenv("MUJOCO_GL", raising=False)
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    with pytest.raises(SystemExit) as excinfo:
        mujoco_grasp.main()

    message = str(excinfo.value)
    assert "MuJoCo renderer failed to start." in message
    assert "no display server was detected and MUJOCO_GL is unset" in message
    assert "Detected MUJOCO_GL=unset, DISPLAY=unset." in message
    assert "MUJOCO_GL=osmesa" in message
    assert "MUJOCO_GL=egl" in message


def test_main_surfaces_friendly_rendering_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class FailingBackend:
        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("an OpenGL platform library has not been loaded into this process")

    monkeypatch.setattr(mujoco_grasp, "MuJoCoMeshcatBackend", FailingBackend)
    monkeypatch.setattr(sys, "argv", ["mujoco_grasp.py", "--output-dir", str(tmp_path)])
    monkeypatch.setenv("MUJOCO_GL", "egl")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    with pytest.raises(SystemExit) as excinfo:
        mujoco_grasp.main()

    message = str(excinfo.value)
    assert "MuJoCo renderer failed to start." in message
    assert "Cause: an OpenGL platform library has not been loaded into this process" in message
    assert "Detected MUJOCO_GL=egl, DISPLAY=unset." in message
    assert "MUJOCO_GL=osmesa" in message
    assert "MUJOCO_GL=egl" in message


def test_main_preserves_non_rendering_backend_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class FailingBackend:
        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(mujoco_grasp, "MuJoCoMeshcatBackend", FailingBackend)
    monkeypatch.setattr(sys, "argv", ["mujoco_grasp.py", "--output-dir", str(tmp_path)])
    monkeypatch.setenv("MUJOCO_GL", "egl")

    with pytest.raises(RuntimeError, match="boom"):
        mujoco_grasp.main()
