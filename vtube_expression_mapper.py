from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class FaceMetrics:
    """Normalized face tracking metrics from webcam or phone camera."""

    confidence: float = 0.0
    head_yaw: float = 0.0
    head_pitch: float = 0.0
    head_roll: float = 0.0
    left_eye_open: float = 0.0
    right_eye_open: float = 0.0
    mouth_open: float = 0.0
    smile: float = 0.0
    eyebrow_raise: float = 0.0
    blink: float = 0.0
    timestamp: float = 0.0
    source: str = "unknown"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "head_yaw": self.head_yaw,
            "head_pitch": self.head_pitch,
            "head_roll": self.head_roll,
            "left_eye_open": self.left_eye_open,
            "right_eye_open": self.right_eye_open,
            "mouth_open": self.mouth_open,
            "smile": self.smile,
            "eyebrow_raise": self.eyebrow_raise,
            "blink": self.blink,
            "timestamp": self.timestamp,
            "source": self.source,
        }


class FaceTracker:
    """Face tracking foundation, compatible with future MediaPipe/OpenCV integration."""

    def __init__(self, tracker_name: str = "generic", smoothing: float = 0.7):
        self.tracker_name = tracker_name
        self.smoothing = smoothing
        self.last_metrics: Optional[FaceMetrics] = None

    def process_frame(self, frame_data: Optional[Dict[str, Any]] = None, source: str = "camera") -> FaceMetrics:
        """Process a generic frame payload or an already-normalized dictionary.

        This is intentionally lightweight and designed as a compatibility layer for real
        face-tracking backends such as OpenCV or MediaPipe later in the project.
        """
        data = frame_data or {}
        if not data:
            metrics = FaceMetrics(confidence=0.0, source=source)
        else:
            metrics = FaceMetrics(
                confidence=float(data.get("confidence", 0.0)),
                head_yaw=float(data.get("head_yaw", 0.0)),
                head_pitch=float(data.get("head_pitch", 0.0)),
                head_roll=float(data.get("head_roll", 0.0)),
                left_eye_open=float(data.get("left_eye_open", 0.0)),
                right_eye_open=float(data.get("right_eye_open", 0.0)),
                mouth_open=float(data.get("mouth_open", 0.0)),
                smile=float(data.get("smile", 0.0)),
                eyebrow_raise=float(data.get("eyebrow_raise", 0.0)),
                blink=float(data.get("blink", 0.0)),
                source=source,
            )

        if self.last_metrics is not None:
            metrics.head_yaw = self._mix(metrics.head_yaw, self.last_metrics.head_yaw)
            metrics.head_pitch = self._mix(metrics.head_pitch, self.last_metrics.head_pitch)
            metrics.head_roll = self._mix(metrics.head_roll, self.last_metrics.head_roll)
            metrics.left_eye_open = self._mix(metrics.left_eye_open, self.last_metrics.left_eye_open)
            metrics.right_eye_open = self._mix(metrics.right_eye_open, self.last_metrics.right_eye_open)
            metrics.mouth_open = self._mix(metrics.mouth_open, self.last_metrics.mouth_open)
            metrics.smile = self._mix(metrics.smile, self.last_metrics.smile)
            metrics.blink = self._mix(metrics.blink, self.last_metrics.blink)

        self.last_metrics = metrics
        return metrics

    def _mix(self, current: float, previous: float) -> float:
        return previous * (1.0 - self.smoothing) + current * self.smoothing


if __name__ == "__main__":
    tracker = FaceTracker("camera")
    sample = {
        "confidence": 0.82,
        "head_yaw": 0.15,
        "head_pitch": -0.08,
        "head_roll": 0.02,
        "left_eye_open": 0.9,
        "right_eye_open": 0.9,
        "mouth_open": 0.25,
        "smile": 0.45,
        "blink": 0.0,
    }
    print(tracker.process_frame(sample, source="phone-camera").as_dict())
