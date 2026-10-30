"""Avatar model registry for VTuber assets and runtime state.

This module intentionally supports both classic model metadata and the face-driven
rig used by VTUBE OS for Live2D/VRM-type motion tracking.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from vtube_expression_mapper import FaceMetrics


SUPPORTED_AVATAR_TYPES = ("live2d", "vrm", "generic")

DEFAULT_PRESETS = {
    "Luna": {"head_scale": 1.0, "eye_scale": 1.0, "mouth_scale": 1.0, "style": "idol"},
    "Nova": {"head_scale": 1.02, "eye_scale": 1.05, "mouth_scale": 1.1, "style": "streamer"},
    "Kiro": {"head_scale": 0.98, "eye_scale": 0.95, "mouth_scale": 1.15, "style": "cyber"},
    "Aoi": {"head_scale": 1.05, "eye_scale": 1.08, "mouth_scale": 1.0, "style": "idol"},
    "Mika": {"head_scale": 1.0, "eye_scale": 1.1, "mouth_scale": 1.2, "style": "magic"},
    "Yuzu": {"head_scale": 1.05, "eye_scale": 0.98, "mouth_scale": 1.08, "style": "host"},
}


@dataclass
class AvatarModel:
    """Descriptor for a VTuber avatar model."""

    name: str
    model_type: str = "vrm"
    model_path: str = ""
    avatar_name: str = ""
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    expression_map: Dict[str, float] = field(default_factory=dict)
    rig_state: Dict[str, float] = field(default_factory=dict)

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
                "rig_state": model.rig_state,
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
                    model_type=payload.get("model_type", "vrm"),
                    model_path=payload.get("model_path", ""),
                    avatar_name=payload.get("avatar_name", name),
                    enabled=payload.get("enabled", True),
                    settings=payload.get("settings", {}),
                    expression_map=payload.get("expression_map", {}),
                    rig_state=payload.get("rig_state", {}),
                )
            )


@dataclass
class AvatarRigState:
    """Normalized VTuber motion state derived from face metrics."""

    head_yaw: float = 0.0
    head_pitch: float = 0.0
    head_roll: float = 0.0
    left_eye_open: float = 1.0
    right_eye_open: float = 1.0
    mouth_open: float = 0.0
    smile: float = 0.0
    eyebrow_raise: float = 0.0
    blink: float = 0.0
    confidence: float = 0.0
    emotion: str = "neutral"
    source: str = "camera"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "head_yaw": self.head_yaw,
            "head_pitch": self.head_pitch,
            "head_roll": self.head_roll,
            "left_eye_open": self.left_eye_open,
            "right_eye_open": self.right_eye_open,
            "mouth_open": self.mouth_open,
            "smile": self.smile,
            "eyebrow_raise": self.eyebrow_raise,
            "blink": self.blink,
            "confidence": self.confidence,
            "emotion": self.emotion,
            "source": self.source,
        }


class FaceDrivenAvatarRig:
    """Maps webcam/phone face metrics to a live VTuber rig state."""

    def __init__(self, preset_name: str = "Luna", smoothing: float = 0.7):
        self.preset_name = preset_name if preset_name in DEFAULT_PRESETS else "Luna"
        self.smoothing = smoothing
        self.state = AvatarRigState(source="camera")
        self.last_metrics: Optional[FaceMetrics] = None

    def update(self, metrics: FaceMetrics) -> AvatarRigState:
        if self.last_metrics is None:
            self.last_metrics = metrics

        target = AvatarRigState(
            head_yaw=self._mix(metrics.head_yaw, self.last_metrics.head_yaw, 0.6),
            head_pitch=self._mix(metrics.head_pitch, self.last_metrics.head_pitch, 0.6),
            head_roll=self._mix(metrics.head_roll, self.last_metrics.head_roll, 0.6),
            left_eye_open=max(0.0, min(1.0, metrics.left_eye_open)),
            right_eye_open=max(0.0, min(1.0, metrics.right_eye_open)),
            mouth_open=max(0.0, min(1.0, metrics.mouth_open)),
            smile=max(0.0, min(1.0, metrics.smile)),
            eyebrow_raise=max(0.0, min(1.0, metrics.eyebrow_raise)),
            blink=max(0.0, min(1.0, metrics.blink)),
            confidence=max(0.0, min(1.0, metrics.confidence)),
            source=metrics.source,
        )

        if target.mouth_open > 0.65:
            target.emotion = "talking"
        elif target.smile > 0.7:
            target.emotion = "happy"
        elif target.eyebrow_raise > 0.5:
            target.emotion = "surprised"
        elif target.blink > 0.6:
            target.emotion = "blink"
        else:
            target.emotion = "neutral"

        self.state.head_yaw = self._smooth(self.state.head_yaw, target.head_yaw)
        self.state.head_pitch = self._smooth(self.state.head_pitch, target.head_pitch)
        self.state.head_roll = self._smooth(self.state.head_roll, target.head_roll)
        self.state.left_eye_open = self._smooth(self.state.left_eye_open, target.left_eye_open)
        self.state.right_eye_open = self._smooth(self.state.right_eye_open, target.right_eye_open)
        self.state.mouth_open = self._smooth(self.state.mouth_open, target.mouth_open)
        self.state.smile = self._smooth(self.state.smile, target.smile)
        self.state.eyebrow_raise = self._smooth(self.state.eyebrow_raise, target.eyebrow_raise)
        self.state.blink = self._smooth(self.state.blink, target.blink)
        self.state.confidence = self._smooth(self.state.confidence, target.confidence)
        self.state.emotion = target.emotion
        self.state.source = metrics.source

        self.last_metrics = metrics
        return self.state

    def _mix(self, current: float, previous: float, weight: float) -> float:
        return previous * (1.0 - weight) + current * weight

    def _smooth(self, previous: float, target: float) -> float:
        return previous * (1.0 - self.smoothing) + target * self.smoothing

    def as_dict(self) -> Dict[str, Any]:
        return self.state.as_dict()


def list_templates() -> List[str]:
    return list(DEFAULT_PRESETS.keys())


def new_character(template: str = "Luna", name: Optional[str] = None) -> Dict[str, Any]:
    template_name = template if template in DEFAULT_PRESETS else "Luna"
    return {
        "name": name or template_name,
        "template": template_name,
        "model_type": "vrm",
        "preset": DEFAULT_PRESETS[template_name],
        "tracking": {"enabled": True},
    }


if __name__ == "__main__":
    registry = AvatarModelRegistry()
    registry.register(AvatarModel(name="Luna", model_type="vrm", model_path="assets/avatars/Luna/Luna.vrm", avatar_name="Luna"))
    print(registry.list_names())
