from __future__ import annotations

from typing import Any, Dict, List, Optional

from vtube_runtime import VTUBERuntime
from vtube_mobile_bridge import MobileBridgeManager
from vtube_device_auth import VTUBEDeviceAuthStore


class VTUBEIntegratedRuntime:
    """Integrated runtime containing desktop OS, Android bridge, and session pipeline."""

    def __init__(self):
        self.runtime = VTUBERuntime()
        self.mobile_manager = MobileBridgeManager()
        self.device_auth = VTUBEDeviceAuthStore()

    def register_android_phone(self, host: str, token: str, device_id: Optional[str] = None, name: str = "android-phone") -> Dict[str, Any]:
        bridge = self.mobile_manager.pair_phone(host, token, device_id=device_id, name=name)
        self.runtime.phone_registry.register(bridge, name=name)
        return bridge.telemetry()

    def request_pairing(self, device_id: str, device_name: str, capabilities: Optional[List[str]] = None, fingerprint: str = "") -> Dict[str, Any]:
        return self.mobile_manager.request_pairing(device_id, device_name, capabilities, fingerprint)

    def confirm_pairing(self, pair_id: str, challenge: str, device_id: str, fingerprint: str) -> Dict[str, Any]:
        return self.mobile_manager.confirm_pairing(pair_id, challenge, device_id, fingerprint)

    def verify_session(self, device_id: str, session_key: str) -> bool:
        return self.mobile_manager.verify_session(device_id, session_key)

    def bootstrap(self) -> Dict[str, Any]:
        self.runtime.register_phone("192.168.1.42", "ABC123", "phone-primary")
        self.runtime.register_avatar("Luna", model_type="live2d", model_path="models/Luna.model3.json", avatar_name="Luna")
        self.runtime.register_scene_source("camera", "webcam", "Camera 1", x=0, y=0, width=1280, height=720, z_index=1)
        self.runtime.register_scene_source("avatar", "avatar", "Luna", x=1100, y=110, width=420, height=620, z_index=10)
        self.runtime.register_audio_device("Laptop Mic", "input")
        self.runtime.bind_audio_track("Laptop Mic", volume=0.9, source_type="microphone")
        self.runtime.register_stream_platform("youtube", "youtube", "rtmp://a.rtmp.youtube.com/live2", "demo-stream-key", channel_name="vtube-demo")
        return self.runtime.snapshot()


if __name__ == "__main__":
    runtime = VTUBEIntegratedRuntime()
    pairing = runtime.request_pairing("phone-primary", "Pixel 9", ["camera", "microphone", "screen"], "fp-demo")
    print(pairing)
    print(runtime.confirm_pairing(pairing["pair_id"], pairing["challenge"], "phone-primary", "fp-demo"))
