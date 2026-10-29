from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from vtube_device_auth import VTUBEDeviceAuthStore
from vtube_phone_bridge import PhoneBridge, PhoneDeviceRegistry


@dataclass
class AndroidSession:
    device_id: str
    host: str
    session_key: str
    status: str = "active"
    capabilities: List[str] = field(default_factory=lambda: ["camera", "microphone", "screen"])

    def as_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "host": self.host,
            "session_key": self.session_key,
            "status": self.status,
            "capabilities": self.capabilities,
        }


class MobileBridgeManager:
    """Bridge manager for Android companion devices connected to VTUBE OS."""

    def __init__(self):
        self.registry = PhoneDeviceRegistry()
        self.device_auth = VTUBEDeviceAuthStore()
        self.sessions: Dict[str, AndroidSession] = {}

    def pair_phone(self, host: str, token: str, device_id: Optional[str] = None, name: str = "android-phone") -> PhoneBridge:
        bridge = PhoneBridge(host, token, device_id=device_id, name=name)
        bridge.device.paired = True
        bridge.device.connected = True
        self.registry.register(bridge, name=name)
        return bridge

    def request_pairing(self, device_id: str, device_name: str, capabilities: Optional[List[str]] = None, fingerprint: str = "") -> Dict[str, Any]:
        return self.device_auth.request_pairing(device_id, device_name, capabilities, fingerprint)

    def confirm_pairing(self, pair_id: str, challenge: str, device_id: str, fingerprint: str) -> Dict[str, Any]:
        result = self.device_auth.confirm_pairing(pair_id, challenge, device_id, fingerprint)
        if result.get("status") == "paired":
            self.sessions[device_id] = AndroidSession(
                device_id=device_id,
                host="desktop-localhost",
                session_key=result["session_key"],
                capabilities=self.device_auth.paired[device_id].capabilities,
            )
        return result

    def verify_session(self, device_id: str, session_key: str) -> bool:
        return self.device_auth.verify_session(device_id, session_key)

    def list_phones(self) -> List[str]:
        return [device.id for device in self.registry.list()]

    def snapshot(self) -> List[Dict[str, Any]]:
        return [device.as_dict() for device in self.registry.list()]


if __name__ == "__main__":
    manager = MobileBridgeManager()
    pairing = manager.request_pairing("phone-primary", "Pixel 9", ["camera", "microphone", "screen"], "fp-demo")
    print(pairing)
    print(manager.confirm_pairing(pairing["pair_id"], pairing["challenge"], "phone-primary", "fp-demo"))
