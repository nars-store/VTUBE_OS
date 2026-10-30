"""VRM renderer adapter for VTUBE OS.

This is a bridge layer for a real VRM runtime. The code keeps metadata loading and
runtime state validation separate from the actual 3D engine that may run in the
browser or a desktop runtime.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class VRMRenderAsset:
    path: str
    model_name: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def exists(self) -> bool:
        return Path(self.path).exists()

    def load(self) -> Dict[str, Any]:
        if not self.exists:
            return {"status": "missing", "path": self.path, "model_type": "vrm"}
        payload = json.loads(Path(self.path).read_text(encoding="utf-8"))
        self.metadata = payload.get("meta", payload)
        self.model_name = self.metadata.get("title", Path(self.path).stem)
        return self.metadata


class VRMRenderer:
    """Renderer adapter. Use with Three.js + @pixiv/three-vrm or other VRM engine."""

    def __init__(self, model_path: str = "assets/avatars/Luna/Luna.vrm"):
        self.asset = VRMRenderAsset(path=model_path)

    def load(self) -> Dict[str, Any]:
        return self.asset.load()

    def preview(self) -> Dict[str, Any]:
        return {
            "model_type": "vrm",
            "path": self.asset.path,
            "model_name": self.asset.model_name,
            "status": "ready" if self.asset.exists else "missing",
        }


if __name__ == "__main__":
    renderer = VRMRenderer()
    print(renderer.preview())
