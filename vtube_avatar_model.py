"""Face-driven VTuber avatar runtime.

This module replaces the old static SVG avatar prototype with a real rig-oriented
VTuber state model that can be driven by webcam or phone face tracking.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from vtube_expression_mapper import FaceMetrics


DEFAULT_PRESETS = {
    "Luna": {"head_scale": 1.0, "eye_scale": 1.0, "mouth_scale": 1.0, "style": "idol"},
    "Nova": {"head_scale": 1.02, "eye_scale": 1.05, "mouth_scale": 1.1, "style": "streamer"},
    "Kiro": {"head_scale": 0.98, "eye_scale": 0.95, "mouth_scale": 1.15, "style": "cyber"},
    "Aoi": {"head_scale": 1.05, "eye_scale": 1.08, "mouth_scale": 1.0, "style": "idol"},
    "Mika": {"head_scale": 1.0, "eye_scale": 1.1, "mouth_scale": 1.2, "style": "magic"},
    "Yuzu": {"head_scale": 1.05, "eye_scale": 0.98, "mouth_scale": 1.08, "style": "host"},
}


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

        current = self.state
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

        current.head_yaw = self._smooth(current.head_yaw, target.head_yaw)
        current.head_pitch = self._smooth(current.head_pitch, target.head_pitch)
        current.head_roll = self._smooth(current.head_roll, target.head_roll)
        current.left_eye_open = self._smooth(current.left_eye_open, target.left_eye_open)
        current.right_eye_open = self._smooth(current.right_eye_open, target.right_eye_open)
        current.mouth_open = self._smooth(current.mouth_open, target.mouth_open)
        current.smile = self._smooth(current.smile, target.smile)
        current.eyebrow_raise = self._smooth(current.eyebrow_raise, target.eyebrow_raise)
        current.blink = self._smooth(current.blink, target.blink)
        current.confidence = self._smooth(current.confidence, target.confidence)
        current.emotion = target.emotion
        current.source = metrics.source

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


def render_avatar_svg(character: Dict[str, Any]) -> str:
    raise RuntimeError(
        "SVG avatar rendering is no longer used. This project now uses a face-driven VTuber rig. "
        "Use FaceDrivenAvatarRig + FaceTracker to drive a Live2D/VRM model instead."
    )


def render_stream_overlay_svg(character: Dict[str, Any], goal: float, donation_link: str = "", qr_data_uri: str = "") -> str:
    raise RuntimeError(
        "Static stream overlay SVG is deprecated. Use the real-time VTuber runtime pipeline driven by live face tracking."
    )


if __name__ == "__main__":
    rig = FaceDrivenAvatarRig("Aoi")
    sample = FaceMetrics(
        confidence=0.92,
        head_yaw=0.22,
        head_pitch=-0.1,
        head_roll=0.03,
        left_eye_open=0.9,
        right_eye_open=0.92,
        mouth_open=0.58,
        smile=0.72,
        eyebrow_raise=0.18,
        blink=0.08,
        source="webcam",
    )
    print(rig.update(sample).as_dict())
