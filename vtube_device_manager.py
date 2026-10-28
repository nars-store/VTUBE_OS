from __future__ import annotations

from typing import List, Optional


class DeviceManager:
    """Track known local devices (webcam, phone, microphone, desktop capture)."""

    def __init__(self):
        self.devices = []

    def register(self, name: str, kind: str, online: bool = True, extra: Optional[dict] = None) -> dict:
        record = {
            "name": name,
            "kind": kind,
            "online": online,
            "extra": extra or {},
        }
        self.devices.append(record)
        return record

    def list(self) -> List[dict]:
        return list(self.devices)

    def get(self, name: str) -> dict:
        for device in self.devices:
            if device["name"] == name:
                return device
        raise KeyError(f"Device not found: {name}")

    def clear(self) -> None:
        self.devices.clear()


if __name__ == "__main__":
    manager = DeviceManager()
    manager.register("Phone Camera", "phone-camera")
    manager.register("Phone Microphone", "phone-mic")
    print(manager.list())
