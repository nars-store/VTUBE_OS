from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "tools" / "mvp1_phone_capture.py"
    spec = importlib.util.spec_from_file_location("mvp1_phone_capture", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


module = load_module()


def test_phone_url_build():
    assert module.phone_url("192.168.0.10", "ABC123", "camera.mjpeg") == (
        "http://192.168.0.10:8765/camera.mjpeg?token=ABC123"
    )


def test_invalid_token_rejected():
    try:
        module.phone_url("192.168.0.10", "BAD", "camera.mjpeg")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid token")


def test_extract_jpeg_from_mjpeg_sample():
    sample = b"header\xff\xd8test\xff\xd9tail"
    assert module.extract_jpeg_from_mjpeg(sample) == b"\xff\xd8test\xff\xd9"


# This file intentionally stays small: MVP1 is a runtime helper for local phone validation.
