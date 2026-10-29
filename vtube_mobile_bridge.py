from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


@dataclass
class PhoneDevice:
    id: str
    name: str
    host: str
    token: str
    paired: bool = False
    connected: bool = False
    last_seen: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=lambda: ["camera", "microphone", "screen"]) 
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "token": self.token,
            "paired": self.paired,
            "connected": self.connected,
            "last_seen": self.last_seen,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }


class PhoneBridge:
    """Bridge layer for connecting VTUBE OS to an Android companion device."""

    def __init__(self, host: str, token: str, device_id: Optional[str] = None, name: str = "phone"):
        self.host = host
        self.token = token
        self.device = PhoneDevice(
            id=device_id or f"phone-{abs(hash(host))}",
            name=name,
            host=host,
            token=token,
        )

    def pair(self) -> bool:
        self.device.paired = True
        self.device.connected = True
        self.device.last_seen = time.time()
        return True

    def disconnect(self) -> None:
        self.device.connected = False
        self.device.last_seen = time.time()

    def send_command(self, command: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "command": command,
            "payload": payload or {},
            "target": self.device.host,
            "status": "queued",
            "device_id": self.device.id,
        }

    def telemetry(self) -> Dict[str, Any]:
        return {
            "device_id": self.device.id,
            "host": self.device.host,
            "connected": self.device.connected,
            "paired": self.device.paired,
            "last_seen": self.device.last_seen,
            "capabilities": self.device.capabilities,
        }


class PhoneDeviceRegistry:
    """Registry for paired Android devices."""

    def __init__(self):
        self.devices: Dict[str, PhoneDevice] = {}

    def register(self, bridge: PhoneBridge, name: Optional[str] = None) -> PhoneDevice:
        device = bridge.device
        if name is not None:
            device.name = name
        self.devices[device.id] = device
        return device

    def get(self, device_id: str) -> PhoneDevice:
        if device_id not in self.devices:
            raise KeyError(f"Phone device not found: {device_id}")
        return self.devices[device_id]

    def list(self) -> List[PhoneDevice]:
        return list(self.devices.values())


if __name__ == "__main__":
    bridge = PhoneBridge("192.168.1.42", "phone-token-123", "phone-1", "Pixel 9")
    bridge.pair()
    print(bridge.telemetry())
    print(bridge.send_command("start_camera", {"source": "front"}))
