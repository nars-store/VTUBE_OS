from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


SUPPORTED_AVATAR_TYPES = ("live2d", "vrm", "generic")


@dataclass
class AvatarModel:
    """Descriptor for a VTuber avatar model."""

    name: str
    model_type: str = "live2d"
    model_path: str = ""
    avatar_name: str = ""
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    expression_map: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        if self.model_type not in SUPPORTED_AVATAR_TYPES:
            raise ValueError(f"Unsupported avatar model type: {self.model_type}")
        if self.model_type != "generic" and self.model_path:
            path = Path(self.model_path)
            if not path.exists():
                raise FileNotFoundError(f"Avatar model file does not exist: {self.model_path}")


class AvatarModelRegistry:
    """Registry for VTuber models loaded by the runtime."""

    def __init__(self):
        self.models: Dict[str, AvatarModel] = {}

    def register(self, model: AvatarModel) -> None:
        model.validate()
        self.models[model.name] = model

    def get(self, name: str) -> AvatarModel:
        if name not in self.models:
            raise KeyError(f"Avatar model not found: {name}")
        return self.models[name]

    def list_names(self) -> List[str]:
        return sorted(self.models.keys())

    def save_manifest(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            name: {
                "model_type": model.model_type,
                "model_path": model.model_path,
                "avatar_name": model.avatar_name,
                "enabled": model.enabled,
                "settings": model.settings,
                "expression_map": model.expression_map,
            }
            for name, model in self.models.items()
        }
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_manifest(self, path: str | Path) -> None:
        target = Path(path)
        if not target.exists():
            return
        data = json.loads(target.read_text(encoding="utf-8"))
        for name, payload in data.items():
            self.register(
                AvatarModel(
                    name=name,
                    model_type=payload.get("model_type", "live2d"),
                    model_path=payload.get("model_path", ""),
                    avatar_name=payload.get("avatar_name", name),
                    enabled=payload.get("enabled", True),
                    settings=payload.get("settings", {}),
                    expression_map=payload.get("expression_map", {}),
                )
            )


if __name__ == "__main__":
    registry = AvatarModelRegistry()
    registry.register(
        AvatarModel(
            name="Luna",
            model_type="live2d",
            model_path="models/Luna.model3.json",
            avatar_name="Luna",
            settings={"base_scale": 1.0},
            expression_map={"smile": 0.4, "blink": 0.0},
        )
    )
    print(registry.list_names())
