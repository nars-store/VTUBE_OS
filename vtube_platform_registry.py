from __future__ import annotations

from vtube_runtime import VTUBERuntime, VTUBERuntimeConfig


class VTUBEApp:
    """Application bootstrap layer for VTUBE OS runtime."""

    def __init__(self, config: VTUBERuntimeConfig | None = None):
        self.runtime = VTUBERuntime(config or VTUBERuntimeConfig())

    def boot(self) -> VTUBERuntime:
        self.runtime.register_phone("192.168.1.42", "ABC123", "phone-primary")
        self.runtime.register_avatar("Luna", model_type="live2d", model_path="models/Luna.model3.json", avatar_name="Luna")
        self.runtime.register_scene_source("camera", "webcam", "Camera 1", x=0, y=0, width=1280, height=720, z_index=1)
        self.runtime.register_scene_source("avatar", "avatar", "Luna Avatar", x=1100, y=110, width=420, height=620, z_index=10)
        self.runtime.register_audio_device("Laptop Mic", "input")
        self.runtime.bind_audio_track("Laptop Mic", volume=0.9, source_type="microphone")
        self.runtime.register_stream_platform("youtube", "youtube", "rtmp://a.rtmp.youtube.com/live2", "demo-stream-key", channel_name="vtube-demo")
        return self.runtime


if __name__ == "__main__":
    app = VTUBEApp()
    runtime = app.boot()
    face = {
        "confidence": 0.9,
        "head_yaw": 0.18,
        "head_pitch": -0.10,
        "head_roll": 0.03,
        "left_eye_open": 0.92,
        "right_eye_open": 0.93,
        "mouth_open": 0.42,
        "smile": 0.71,
        "blink": 0.1,
        "eyebrow_raise": 0.15,
    }
    runtime.process_face(face, source="phone-camera")
    runtime.process_audio(-18.0, "Laptop Mic")
    print(runtime.snapshot())
