from __future__ import annotations

from typing import Any, Dict

from vtube_face_tracking import FaceMetrics


class ExpressionMapper:
    """Map facial metrics to avatar expression states."""

    def __init__(self):
        self.base_states = {
            "neutral": 0.0,
            "smile": 0.0,
            "surprised": 0.0,
            "blink": 0.0,
            "mouth_open": 0.0,
            "angry": 0.0,
            "eyebrow_raise": 0.0,
        }

    def map(self, metrics: FaceMetrics) -> Dict[str, float]:
        states = dict(self.base_states)
        states["smile"] = max(0.0, min(1.0, metrics.smile))
        states["mouth_open"] = max(0.0, min(1.0, metrics.mouth_open))
        states["blink"] = max(0.0, min(1.0, metrics.blink))
        states["eyebrow_raise"] = max(0.0, min(1.0, metrics.eyebrow_raise))

        if metrics.head_yaw > 0.35:
            states["surprised"] = min(1.0, 0.4 + abs(metrics.head_yaw) * 0.8)
        else:
            states["surprised"] = 0.0

        if metrics.mouth_open > 0.7:
            states["mouth_open"] = min(1.0, metrics.mouth_open)

        if metrics.left_eye_open < 0.3 or metrics.right_eye_open < 0.3:
            states["blink"] = 1.0

        return states


if __name__ == "__main__":
    mapper = ExpressionMapper()
    metrics = FaceMetrics(smile=0.8, mouth_open=0.6, blink=0.1, eyebrow_raise=0.2)
    print(mapper.map(metrics))
