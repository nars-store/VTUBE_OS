from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from vtube_auth_manager import AuthManager
from vtube_audio_device import AudioDevice, AudioDeviceManager
from vtube_audio_mixer import AudioMixer, MixerTrack
from vtube_audio_monitor import AudioMonitor
from vtube_avatar_model import AvatarModel, AvatarModelRegistry
from vtube_avatar_runtime import AvatarRuntime
from vtube_device_manager import DeviceManager
from vtube_donation_connector import DonationConnector
from vtube_encryption import SimpleCipher
from vtube_expression_mapper import ExpressionMapper
from vtube_face_tracking import FaceMetrics, FaceTracker
from vtube_live_compositor import LiveCompositor
from vtube_motion_tracker import MotionTracker
from vtube_noise_reduction import NoiseReductionEngine
from vtube_overlay_platform import OverlayPlatformManager
from vtube_permission_manager import PermissionManager
from vtube_phone_bridge import PhoneBridge, PhoneDeviceRegistry
from vtube_platform_registry import PlatformRegistry
from vtube_scene import Scene
from vtube_scene_source import SceneSource
from vtube_stream_platform import StreamPlatformManager
from vtube_stream_source import SourceCatalog


@dataclass
class VTUBERuntimeConfig:
    default_scene_name: str = "vtube-main-scene"
    default_avatar_name: str = "Luna"
    default_platform: str = "youtube"
    cipher_secret: str = "vtube-os-secret"
    default_resolution: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})


class VTUBERuntime:
    """Main orchestration layer for VTUBE OS modules across groups A-H."""

    def __init__(self, config: Optional[VTUBERuntimeConfig] = None):
        self.config = config or VTUBERuntimeConfig()

        self.phone_registry = PhoneDeviceRegistry()
        self.source_catalog = SourceCatalog()
        self.device_manager = DeviceManager()
        self.avatar_registry = AvatarModelRegistry()
        self.face_tracker = FaceTracker(tracker_name="vtube-runtime")
        self.avatar_runtime = AvatarRuntime(self.avatar_registry)
        self.audio_devices = AudioDeviceManager()
        self.audio_mixer = AudioMixer()
        self.noise_engine = NoiseReductionEngine()
        self.audio_monitor = AudioMonitor()
        self.scene = Scene(self.config.default_scene_name, width=self.config.default_resolution["width"], height=self.config.default_resolution["height"])
        self.live_compositor = LiveCompositor(self.scene)
        self.platform_registry = PlatformRegistry()
        self.stream_manager = StreamPlatformManager()
        self.donation_connector = DonationConnector()
        self.overlay_manager = OverlayPlatformManager()
        self.auth_manager = AuthManager()
        self.permission_manager = PermissionManager()
        self.cipher = SimpleCipher(self.config.cipher_secret)

    def register_phone(self, host: str, token: str, name: Optional[str] = None) -> PhoneBridge:
        bridge = PhoneBridge(host, token)
        self.phone_registry.register(bridge, name=name)
        self.device_manager.register(name or bridge.device.host, "phone", True, {"host": host})
        return bridge

    def register_avatar(self, name: str, model_type: str = "live2d", model_path: str = "", avatar_name: str = "") -> AvatarModel:
        model = AvatarModel(name=name, model_type=model_type, model_path=model_path, avatar_name=avatar_name or name)
        self.avatar_registry.register(model)
        self.avatar_runtime.load_model(name)
        return model

    def register_scene_source(self, source_id: str, kind: str, name: str, source_url: str = "", x: int = 0, y: int = 0, width: int = 640, height: int = 360, opacity: float = 1.0, z_index: int = 0) -> SceneSource:
        source = SceneSource(source_id, kind, name, source_url=source_url, x=x, y=y, width=width, height=height, opacity=opacity, z_index=z_index)
        self.scene.add_source(source, x=x, y=y, width=width, height=height, opacity=opacity)
        return source

    def register_audio_device(self, name: str, kind: str, sample_rate: int = 48000, channels: int = 2) -> AudioDevice:
        device = AudioDevice(name=name, kind=kind, sample_rate=sample_rate, channels=channels)
        self.audio_devices.register(device)
        return device

    def register_stream_platform(self, name: str, kind: str, endpoint: str, stream_key: str, channel_name: str = "") -> Dict[str, Any]:
        from vtube_platform_registry import PlatformConfig

        config = PlatformConfig(name=name, kind=kind, endpoint=endpoint, stream_key=stream_key, channel_name=channel_name)
        self.platform_registry.register(config)
        self.stream_manager.register(name, stream_key, endpoint, bitrate_kbps=2500, fps=30)
        return config.as_dict()

    def bind_audio_track(self, name: str, volume: float = 1.0, source_type: str = "microphone") -> MixerTrack:
        track = MixerTrack(name=name, volume=volume, source_type=source_type)
        self.audio_mixer.add_track(track)
        return track

    def process_face(self, frame_data: Optional[Dict[str, Any]] = None, source: str = "camera") -> Dict[str, float]:
        metrics = self.face_tracker.process_frame(frame_data=frame_data, source=source)
        return self.avatar_runtime.update_from_tracking(metrics)

    def process_audio(self, input_db: float, track_name: str = "mic") -> float:
        processed = self.noise_engine.process(input_db)
        self.audio_monitor.update(track_name, peak_db=processed, rms_db=processed, clipping=(processed >= -1.0))
        self.audio_mixer.set_volume(track_name, 1.0)
        return processed

    def render_scene_preview(self) -> Dict[str, Any]:
        return self.live_compositor.render_preview()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "scene": self.scene.snapshot(),
            "platform_registry": [p.as_dict() for p in self.platform_registry.list()],
            "stream_sessions": [s.as_dict() for s in self.stream_manager.list()],
            "donations": self.donation_connector.snapshot(),
            "overlays": self.overlay_manager.snapshot(),
            "audio_levels": self.audio_monitor.snapshot(),
            "avatar_state": self.avatar_runtime.snapshot(),
            "devices": self.device_manager.list(),
        }


def main() -> None:
    runtime = VTUBERuntime()

    runtime.register_phone("192.168.1.42", "ABC123", "phone-1")
    runtime.register_avatar("Luna", model_type="live2d", model_path="models/Luna.model3.json", avatar_name="Luna")
    runtime.register_scene_source("camera", "webcam", "Camera 1", x=0, y=0, width=1280, height=720, z_index=1)
    runtime.register_scene_source("avatar", "avatar", "Luna Avatar", x=1100, y=110, width=420, height=620, z_index=10)
    runtime.register_audio_device("Laptop Mic", "input")
    runtime.bind_audio_track("Laptop Mic", volume=0.9, source_type="microphone")
    runtime.register_stream_platform("youtube", "youtube", "rtmp://a.rtmp.youtube.com/live2", "demo-stream-key", channel_name="vtube-demo")

    face = {"confidence": 0.9, "head_yaw": 0.18, "head_pitch": -0.10, "head_roll": 0.03, "left_eye_open": 0.92, "right_eye_open": 0.93, "mouth_open": 0.42, "smile": 0.71, "blink": 0.1, "eyebrow_raise": 0.15}
    runtime.process_face(face, source="phone-camera")
    runtime.process_audio(-18.0, "Laptop Mic")
    print(runtime.snapshot())


if __name__ == "__main__":
    main()
