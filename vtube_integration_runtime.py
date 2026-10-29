from __future__ import annotations

from typing import Any, Dict, List, Optional

from vtube_phone_bridge import PhoneBridge, PhoneDeviceRegistry


class MobileBridgeManager:
    """Convenience manager for connecting VTUBE OS to Android companion devices."""

    def __init__(self):
        self.registry = PhoneDeviceRegistry()

    def pair_phone(self, host: str, token: str, device_id: Optional[str] = None, name: str = "android-phone") -> PhoneBridge:
        bridge = PhoneBridge(host, token, device_id=device_id, name=name)
        bridge.pair()
        self.registry.register(bridge, name=name)
        return bridge

    def listphones(self) -> List[str]:
        return [device.id for device in self.registry.list()]

    def snapshot(self) -> List[Dict[str, Any]]:
        return [device.as_dict() for device in self.registry.list()]


if __name__ == "__main__":
    manager = MobileBridgeManager()
    bridge = manager.pair_phone("192.168.1.42", "abc123", device_id="phone-primary", name="Pixel 9")
    print(bridge.telemetry())
    print(manager.snapshot())
