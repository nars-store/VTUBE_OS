from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from vtube_face_tracking import FaceMetrics


@dataclass
class MotionState:
    head_yaw: float = 0.0
    head_pitch: float = 0.0
    head_roll: float = 0.0
    left_eye_open: float = 0.0
    right_eye_open: float = 0.0
    mouth_open: float = 0.0
    blink: float = 0.0
    smoothing: float = 0.7

    def apply(self, metrics: FaceMetrics) -> "MotionState":
        self.head_yaw = (self.head_yaw * (1.0 - self.smoothing)) + (metrics.head_yaw * self.smoothing)
        self.head_pitch = (self.head_pitch * (1.0 - self.smoothing)) + (metrics.head_pitch * self.smoothing)
        self.head_roll = (self.head_roll * (1.0 - self.smoothing)) + (metrics.head_roll * self.smoothing)
        self.left_eye_open = (self.left_eye_open * (1.0 - self.smoothing)) + (metrics.left_eye_open * self.smoothing)
        self.right_eye_open = (self.right_eye_open * (1.0 - self.smoothing)) + (metrics.right_eye_open * self.smoothing)
        self.mouth_open = (self.mouth_open * (1.0 - self.smoothing)) + (metrics.mouth_open * self.smoothing)
        self.blink = (self.blink * (1.0 - self.smoothing)) + (metrics.blink * self.smoothing)
        return self

    def as_dict(self) -> Dict[str, float]:
        return {
            "head_yaw": self.head_yaw,
            "head_pitch": self.head_pitch,
            "head_roll": self.head_roll,
            "left_eye_open": self.left_eye_open,
            "right_eye_open": self.right_eye_open,
            "mouth_open": self.mouth_open,
            "blink": self.blink,
        }


class MotionTracker:
    """Simple smoothing tracker for head pose, eye blink, and mouth motion."""

    def __init__(self, smoothing: float = 0.72):
        self.state = MotionState(smoothing=smoothing)

    def update(self, metrics: FaceMetrics) -> MotionState:
        return self.state.apply(metrics)


if __name__ == "__main__":
    tracker = MotionTracker()
    sample = FaceMetrics(head_yaw=0.2, head_pitch=-0.1, head_roll=0.05, left_eye_open=0.9, right_eye_open=0.9, mouth_open=0.4, blink=0.1)
    print(tracker.update(sample).as_dict())
