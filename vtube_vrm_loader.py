"""Loader for Live2D Cubism model files used in VTUBE OS.

This is the real bridge for `.model3.json` assets. The code intentionally keeps the
loader lightweight and compatible with an actual Live2D runtime integration.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Live2DModel:
    path: str
    name: str = ""
    model_type: str = "live2d"
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    @property
    def exists(self) -> bool:
        return Path(self.path).exists()

    def load(self) -> Dict[str, Any]:
        if not self.exists:
            return {"status": "missing", "path": self.path, "model_type": "live2d"}
        payload = json.loads(Path(self.path).read_text(encoding="utf-8"))
        self.metadata = payload
        self.name = payload.get("FileReferences", {}).get("Moc", self.name or Path(self.path).stem)
        return payload


class Live2DModelLoader:
    """Load and validate Live2D model metadata from a `.model3.json` file."""

    def __init__(self, model_path: str | Path):
        self.model_path = str(model_path)
        self.model = Live2DModel(path=self.model_path)

    def load(self) -> Dict[str, Any]:
        return self.model.load()


if __name__ == "__main__":
    loader = Live2DModelLoader("assets/avatars/Luna/Luna.model3.json")
    print(loader.load())
