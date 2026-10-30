"""Loader for VRM avatar files and their metadata.

VRM is the most common file format for real VTuber avatar rigs. This module reads
basic metadata and leaves actual animation/rendering to the eventual real rendering
backend.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class VRMModel:
    path: str
    name: str = ""
    model_type: str = "vrm"
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    @property
    def exists(self) -> bool:
        return Path(self.path).exists()

    def load(self) -> Dict[str, Any]:
        if not self.exists:
            return {"status": "missing", "path": self.path, "model_type": "vrm"}

        payload = json.loads(Path(self.path).read_text(encoding="utf-8"))
        self.metadata = payload.get("meta", payload)
        self.name = self.metadata.get("title", Path(self.path).stem)
        return self.metadata


class VRMModelLoader:
    """Load and validate VRM metadata from a `.vrm` file."""

    def __init__(self, model_path: str | Path):
        self.model_path = str(model_path)
        self.model = VRMModel(path=self.model_path)

    def load(self) -> Dict[str, Any]:
        return self.model.load()


if __name__ == "__main__":
    loader = VRMModelLoader("assets/avatars/Luna/Luna.vrm")
    print(loader.load())
