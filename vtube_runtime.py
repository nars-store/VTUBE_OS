"""VTUBE runtime model layer for Live2D/VRM-based avatar workflows.

This module replaces the older SVG-only avatar idea with a real model-management
layer suitable for future Live2D or VRM avatar runtime integration.

The goal is to provide a clean abstraction for:
- model registry and profile management
- runtime loading and switching
- expression/pose state management
- compatibility with future real VTuber engines

This is not the full runtime implementation yet, but it is the foundation that
replaces the legacy static SVG avatar export flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


SUPPORTED_MODEL_TYPES = ("live2d", "vrm", "legacy_svg")


@dataclass
class VTubeModelSpec:
    """Descriptor for a VTuber model file and its runtime metadata."""

    name: str
    model_type: str
    model_path: str
    avatar_name: str = ""
    enabled: bool = True
    tracking: Dict[str, Any] = field(default_factory=dict)
    expression_map: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.model_type not in SUPPORTED_MODEL_TYPES:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        path = Path(self.model_path)
        if not path.exists() and self.model_type != "legacy_svg":
            raise FileNotFoundError(f"Model file does not exist: {self.model_path}")


class VTubeModelManager:
    """Registry for Live2D/VRM models used by the VTUBE OS runtime."""

    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = Path(model_dir) if model_dir else Path("models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self._models: Dict[str, VTubeModelSpec] = {}

    def register(self, model: VTubeModelSpec) -> None:
        model.validate()
        self._models[model.name] = model

    def load(self, name: str) -> VTubeModelSpec:
        if name not in self._models:
            raise KeyError(f"Model not registered: {name}")
        return self._models[name]

    def list_models(self) -> List[str]:
        return sorted(self._models.keys())

    def save_manifest(self, path: str | Path) -> None:
        manifest_path = Path(path)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            name: {
                "model_type": spec.model_type,
                "model_path": spec.model_path,
                "avatar_name": spec.avatar_name,
                "enabled": spec.enabled,
                "tracking": spec.tracking,
                "expression_map": spec.expression_map,
            }
            for name, spec in self._models.items()
        }
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_manifest(self, path: str | Path) -> None:
        manifest_path = Path(path)
        if not manifest_path.exists():
            return
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, payload in data.items():
            self.register(
                VTubeModelSpec(
                    name=name,
                    model_type=payload.get("model_type", "live2d"),
                    model_path=payload.get("model_path", ""),
                    avatar_name=payload.get("avatar_name", name),
                    enabled=payload.get("enabled", True),
                    tracking=payload.get("tracking", {}),
                    expression_map=payload.get("expression_map", {}),
                )
            )


class VTubeRuntimeAdapter:
    """Runtime abstraction that future Live2D/VRM backends can implement."""

    def __init__(self, model: VTubeModelSpec):
        self.model = model

    def set_expression(self, expression: str, value: float) -> None:
        self.model.expression_map[expression] = value

    def set_pose(self, pose: Dict[str, Any]) -> None:
        self.model.tracking.update(pose)

    def preview_state(self) -> Dict[str, Any]:
        return {
            "name": self.model.name,
            "model_type": self.model.model_type,
            "avatar_name": self.model.avatar_name,
            "tracking": self.model.tracking,
            "expression_map": self.model.expression_map,
        }


class VTubeSceneSession:
    """Represents a live scene where one or more VTuber models are active."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.models: Dict[str, VTubeRuntimeAdapter] = {}

    def add_model(self, model: VTubeModelSpec) -> None:
        self.models[model.name] = VTubeRuntimeAdapter(model)

    def get_model(self, name: str) -> VTubeRuntimeAdapter:
        if name not in self.models:
            raise KeyError(f"Model not loaded in scene: {name}")
        return self.models[name]

    def export_scene_state(self) -> Dict[str, Any]:
        return {
            "scene_name": self.name,
            "models": {name: adapter.preview_state() for name, adapter in self.models.items()},
        }


if __name__ == "__main__":
    manager = VTubeModelManager()
    manager.register(
        VTubeModelSpec(
            name="LunaLive2D",
            model_type="live2d",
            model_path="models/Luna.model3.json",
            avatar_name="Luna",
            tracking={"head_yaw": 0.0, "blink": 0.0},
            expression_map={"smile": 0.4, "surprised": 0.0},
        )
    )
    print(json.dumps(manager.list_models(), indent=2))
