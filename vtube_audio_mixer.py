from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AudioDevice:
    """Represents an input or output audio device."""

    name: str
    kind: str  # input, output, stream, virtual
    sample_rate: int = 48000
    channels: int = 2
    latency_ms: int = 40
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "latency_ms": self.latency_ms,
            "enabled": self.enabled,
            "settings": self.settings,
        }


class AudioDeviceManager:
    """Registry for system, phone, USB, and virtual audio devices."""

    def __init__(self):
        self.devices: Dict[str, AudioDevice] = {}

    def register(self, device: AudioDevice) -> None:
        self.devices[device.name] = device

    def set_enabled(self, name: str, enabled: bool) -> None:
        if name in self.devices:
            self.devices[name].enabled = enabled

    def list_devices(self, kind: Optional[str] = None) -> List[AudioDevice]:
        if kind is None:
            return list(self.devices.values())
        return [device for device in self.devices.values() if device.kind == kind]

    def get(self, name: str) -> AudioDevice:
        if name not in self.devices:
            raise KeyError(f"Audio device not found: {name}")
        return self.devices[name]

    def save_snapshot(self) -> Dict[str, Dict[str, Any]]:
        return {name: device.as_dict() for name, device in self.devices.items()}


if __name__ == "__main__":
    manager = AudioDeviceManager()
    manager.register(AudioDevice("Laptop Mic", "input", sample_rate=48000, channels=1))
    manager.register(AudioDevice("Phone Mic", "input", sample_rate=16000, channels=1))
    manager.register(AudioDevice("Headphones", "output", sample_rate=48000, channels=2))
    print(manager.save_snapshot())
