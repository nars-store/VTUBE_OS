"""Real VTuber runtime layer with Live2D/VRM-ready asset loading.

This module supplies the abstraction for the final avatar runtime used by VTUBE OS.
The actual rendering backend may be Live2D/VRM-specific and should plug into this
interface.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from vtube_avatar_loader import AvatarAssetLoader
from vtube_expression_mapper import FaceMetrics


@dataclass
class AvatarRuntimeState:
    active_avatar: Optional[str] = None
    model_type: str = "vrm"
    expression_map: Dict[str, float] = field(default_factory=dict)
    rig_state: Dict[str, float] = field(default_factory=dict)
    source: str = "camera"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "active_avatar": self.active_avatar,
            "model_type": self.model_type,
            "expression_map": self.expression_map,
            "rig_state": self.rig_state,
            "source": self.source,
        }


class AvatarRuntime:
    """Asset-aware VTuber runtime for real avatar models."""

    def __init__(self, manifest_path: str = "assets/avatars/manifest.json"):
        self.loader = AvatarAssetLoader(manifest_path)
        self.state = AvatarRuntimeState()

    def load_avatar(self, name: str) -> Dict[str, Any]:
        asset = self.loader.get(name)
        self.state.active_avatar = asset.name
        self.state.model_type = asset.model_type
        self.state.expression_map = asset.expression_map
        self.state.rig_state = asset.settings.copy()
        return asset.as_dict()

    def update_from_tracking(self, metrics: FaceMetrics) -> Dict[str, float]:
        expression_map = {
            "smile": max(0.0, min(1.0, metrics.smile)),
            "blink": max(0.0, min(1.0, metrics.blink)),
            "mouth_open": max(0.0, min(1.0, metrics.mouth_open)),
            "head_yaw": metrics.head_yaw,
            "head_pitch": metrics.head_pitch,
            "head_roll": metrics.head_roll,
        }
        self.state.expression_map = expression_map
        self.state.rig_state.update({
            "head_yaw": metrics.head_yaw,
            "head_pitch": metrics.head_pitch,
            "head_roll": metrics.head_roll,
            "source": metrics.source,
        })
        return expression_map

    def snapshot(self) -> Dict[str, Any]:
        return self.state.as_dict()


if __name__ == "__main__":
    runtime = AvatarRuntime()
    print(runtime.loader.list_names())
    print(runtime.snapshot())
