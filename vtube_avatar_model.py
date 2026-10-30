"""Multi-source live VTuber setup for webcam, phone camera, phone screen, and phone mic."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from vtube_scene import Scene
from vtube_scene_source import SceneSource


@dataclass
class MultiSourceConfig:
    webcam_device: str = "/dev/video0"
    webcam_name: str = "Main Webcam"
    phone_host: str = "192.168.1.42"
    phone_token: str = "ABC123"
    phone_camera_name: str = "Phone Camera"
    phone_screen_name: str = "Phone Screen"
    phone_mic_name: str = "Phone Mic"
    avatar_name: str = "Luna"
    avatar_model_path: str = "assets/avatars/Luna/Luna.vrm"
    width: int = 1920
    height: int = 1080


class MultiSourceVTuberRuntime:
    """Build a scene where webcam, phone camera, phone screen, and mic are all active."""

    def __init__(self, config: Optional[MultiSourceConfig] = None):
        self.config = config or MultiSourceConfig()
        self.scene = Scene("multisource-vtube", width=self.config.width, height=self.config.height)

    def build_scene(self) -> Scene:
        webcam = SceneSource(
            "webcam-main",
            "webcam",
            self.config.webcam_name,
            source_url=self.config.webcam_device,
            x=0,
            y=0,
            width=640,
            height=480,
            z_index=1,
        )
        phone_cam = SceneSource(
            "phone-camera-main",
            "phone-camera",
            self.config.phone_camera_name,
            source_url=f"http://{self.config.phone_host}:8765/camera.mjpeg?token={self.config.phone_token}",
            x=660,
            y=0,
            width=640,
            height=480,
            z_index=2,
        )
        phone_screen = SceneSource(
            "phone-screen-main",
            "phone-screen",
            self.config.phone_screen_name,
            source_url=f"http://{self.config.phone_host}:8765/screen.mjpeg?token={self.config.phone_token}",
            x=0,
            y=500,
            width=960,
            height=540,
            z_index=3,
        )
        avatar = SceneSource(
            "avatar-live",
            "avatar",
            self.config.avatar_name,
            source_url=self.config.avatar_model_path,
            x=1180,
            y=60,
            width=620,
            height=900,
            z_index=10,
            options={"model_type": "vrm", "tracking": True},
        )

        self.scene = Scene("multisource-vtube", width=self.config.width, height=self.config.height)
        self.scene.add_source(webcam, x=0, y=0, width=640, height=480)
        self.scene.add_source(phone_cam, x=660, y=0, width=640, height=480)
        self.scene.add_source(phone_screen, x=0, y=500, width=960, height=540)
        self.scene.add_source(avatar, x=1180, y=60, width=620, height=900)
        return self.scene

    def as_dict(self) -> Dict[str, Any]:
        return {
            "config": {
                "webcam_device": self.config.webcam_device,
                "phone_host": self.config.phone_host,
                "phone_token": self.config.phone_token,
                "avatar_name": self.config.avatar_name,
            },
            "scene": self.scene.snapshot(),
        }


if __name__ == "__main__":
    runtime = MultiSourceVTuberRuntime()
    scene = runtime.build_scene()
    print(scene.snapshot())
