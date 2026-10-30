"""Live2D renderer adapter for VTUBE OS.

This is a bridge layer for a real Live2D runtime. The project keeps the logic as a
runtime-facing adapter so a real Live2D Web SDK or native client can plug in.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class Live2DRenderAsset:
    path: str
    model_name: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def exists(self) -> bool:
        return Path(self.path).exists()

    def load(self) -> Dict[str, Any]:
        if not self.exists:
            return {"status": "missing", "path": self.path, "model_type": "live2d"}
        payload = json.loads(Path(self.path).read_text(encoding="utf-8"))
        self.model_name = payload.get("FileReferences", {}).get("Moc", Path(self.path).stem)
        self.metadata = payload
        return payload


class Live2DRenderer:
    """Renderer adapter. Use with Live2D Cubism Web SDK / native runtime."""

    def __init__(self, model_path: str = "assets/avatars/Nova/Nova.model3.json"):
        self.asset = Live2DRenderAsset(path=model_path)

    def load(self) -> Dict[str, Any]:
        return self.asset.load()

    def preview(self) -> Dict[str, Any]:
        return {
            "model_type": "live2d",
            "path": self.asset.path,
            "model_name": self.asset.model_name,
            "status": "ready" if self.asset.exists else "missing",
        }


if __name__ == "__main__":
    renderer = Live2DRenderer()
    print(renderer.preview())
