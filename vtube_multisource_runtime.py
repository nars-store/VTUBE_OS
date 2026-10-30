"""Avatar asset loader for Live2D/VRM-ready VTuber models.

This loader reads the manifest in `assets/avatars/manifest.json` and resolves the
actual model files used by the VTuber runtime.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AvatarAsset:
    name: str
    model_type: str = "vrm"
    path: str = ""
    avatar_name: str = ""
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    expression_map: Dict[str, float] = field(default_factory=dict)

    @property
    def exists(self) -> bool:
        if not self.path:
            return False
        return Path(self.path).exists()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model_type": self.model_type,
            "path": self.path,
            "avatar_name": self.avatar_name,
            "enabled": self.enabled,
            "settings": self.settings,
            "expression_map": self.expression_map,
        }


class AvatarAssetLibrary:
    """Load and resolve avatar assets from the project manifest."""

    def __init__(self, manifest_path: str | Path = "assets/avatars/manifest.json"):
        self.manifest_path = Path(manifest_path)
        self.assets: Dict[str, AvatarAsset] = {}
        self.load_manifest()

    def load_manifest(self) -> None:
        if not self.manifest_path.exists():
            self.assets = {}
            return
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        avatars = payload.get("avatars", {})
        for key, value in avatars.items():
            name = value.get("name", key)
            asset = AvatarAsset(
                name=name,
                model_type=value.get("model_type", "vrm"),
                path=value.get("path", ""),
                avatar_name=value.get("avatar_name", name),
                enabled=bool(value.get("enabled", True)),
                settings=value.get("settings", {}),
                expression_map=value.get("expression_map", {}),
            )
            self.assets[name] = asset

    def list_names(self) -> List[str]:
        return sorted(self.assets.keys())

    def get(self, name: str) -> AvatarAsset:
        if name not in self.assets:
            raise KeyError(f"Avatar asset not found: {name}")
        return self.assets[name]

    def resolve(self, name: str) -> AvatarAsset:
        asset = self.get(name)
        if not asset.exists:
            return asset
        return asset

    def snapshot(self) -> List[Dict[str, Any]]:
        return [asset.as_dict() for asset in self.assets.values()]


def load_avatar_library(manifest_path: str | Path = "assets/avatars/manifest.json") -> AvatarAssetLibrary:
    return AvatarAssetLibrary(manifest_path)


if __name__ == "__main__":
    library = load_avatar_library()
    print(library.snapshot())
