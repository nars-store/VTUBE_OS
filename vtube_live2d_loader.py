"""Avatar asset loader for Live2D and VRM models.

This module is the real asset bridge for the VTuber pipeline. It reads the avatar
manifest and resolves model files such as `.model3.json` (Live2D) and `.vrm`
(VRM) for use in the live scene runtime.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_MANIFEST = "assets/avatars/manifest.json"


@dataclass
class AvatarAsset:
    name: str
    model_type: str
    path: str
    avatar_name: str = ""
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    expression_map: Dict[str, float] = field(default_factory=dict)
    description: str = ""

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
            "avatar_name": self.avatar_name or self.name,
            "enabled": self.enabled,
            "settings": self.settings,
            "expression_map": self.expression_map,
            "description": self.description,
        }


class AvatarAssetLoader:
    """Loads avatar metadata from the repo manifest and resolves actual assets."""

    def __init__(self, manifest_path: str | Path = DEFAULT_MANIFEST):
        self.manifest_path = Path(manifest_path)
        self.assets: Dict[str, AvatarAsset] = {}
        self.load_manifest()

    def load_manifest(self) -> None:
        if not self.manifest_path.exists():
            self.assets = {}
            return

        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        for key, value in payload.get("avatars", {}).items():
            asset = AvatarAsset(
                name=value.get("name", key),
                model_type=value.get("model_type", "vrm"),
                path=value.get("path", ""),
                avatar_name=value.get("avatar_name", value.get("name", key)),
                enabled=bool(value.get("enabled", True)),
                settings=value.get("settings", {}),
                expression_map=value.get("expression_map", {}),
                description=value.get("description", ""),
            )
            self.assets[asset.name] = asset

    def list(self) -> List[AvatarAsset]:
        return list(self.assets.values())

    def list_names(self) -> List[str]:
        return sorted(self.assets.keys())

    def get(self, name: str) -> AvatarAsset:
        if name not in self.assets:
            raise KeyError(f"Avatar asset not found: {name}")
        return self.assets[name]

    def resolve(self, name: str) -> AvatarAsset:
        asset = self.get(name)
        return asset

    def snapshot(self) -> List[Dict[str, Any]]:
        return [asset.as_dict() for asset in self.list()]


def load_avatar_manifest(manifest_path: str | Path = DEFAULT_MANIFEST) -> AvatarAssetLoader:
    return AvatarAssetLoader(manifest_path)


if __name__ == "__main__":
    loader = load_avatar_manifest()
    print(loader.snapshot())
