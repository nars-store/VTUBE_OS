from __future__ import annotations

from typing import Dict, List, Optional

from vtube_avatar_model import AvatarModel, AvatarModelRegistry
from vtube_expression_mapper import ExpressionMapper
from vtube_face_tracking import FaceMetrics
from vtube_motion_tracker import MotionTracker


class AvatarRuntime:
    """Runtime controller for VTuber character state and tracking updates."""

    def __init__(self, registry: Optional[AvatarModelRegistry] = None):
        self.registry = registry or AvatarModelRegistry()
        self.active_model: Optional[AvatarModel] = None
        self.expression_mapper = ExpressionMapper()
        self.motion_tracker = MotionTracker()
        self.last_metrics: Optional[FaceMetrics] = None

    def load_model(self, model_name: str) -> AvatarModel:
        self.active_model = self.registry.get(model_name)
        return self.active_model

    def update_from_tracking(self, metrics: FaceMetrics) -> Dict[str, float]:
        self.last_metrics = metrics
        motion = self.motion_tracker.update(metrics)
        expression_map = self.expression_mapper.map(metrics)
        expression_map["head_yaw"] = motion.head_yaw
        expression_map["head_pitch"] = motion.head_pitch
        expression_map["head_roll"] = motion.head_roll

        if self.active_model is not None:
            self.active_model.expression_map = expression_map
            self.active_model.settings.setdefault("motion", {})
            self.active_model.settings["motion"].update(motion.as_dict())

        return expression_map

    def snapshot(self) -> Dict[str, object]:
        return {
            "active_model": self.active_model.name if self.active_model else None,
            "expression_map": self.active_model.expression_map if self.active_model else {},
            "settings": self.active_model.settings if self.active_model else {},
            "motion": self.motion_tracker.state.as_dict(),
        }


if __name__ == "__main__":
    registry = AvatarModelRegistry()
    registry.register(AvatarModel(name="Luna", model_type="live2d", avatar_name="Luna"))
    runtime = AvatarRuntime(registry)
    runtime.load_model("Luna")
    metrics = FaceMetrics(smile=0.8, mouth_open=0.6, head_yaw=0.25, head_pitch=-0.1, head_roll=0.03, blink=0.12, eyebrow_raise=0.2)
    print(runtime.update_from_tracking(metrics))
