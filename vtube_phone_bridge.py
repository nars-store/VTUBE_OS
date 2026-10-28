from __future__ import annotations

import ipaddress
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PhoneDevice:
    host: str
    pair_token: str
    mode: str = "wifi-local"
    status: str = "offline"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        ip = ipaddress.ip_address(self.host)
        if not ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError("Host harus IP lokal privat yang valid di jaringan yang sama dengan HP.")
        token = self.pair_token.strip().upper()
        if len(token) != 6 or not token.isalnum():
            raise ValueError("Pair code harus 6 karakter alfanumerik.")

    def status_url(self) -> str:
        return self._endpoint_url("status")

    def camera_url(self) -> str:
        return self._endpoint_url("camera.mjpeg")

    def screen_url(self) -> str:
        return self._endpoint_url("screen.mjpeg")

    def audio_url(self) -> str:
        return self._endpoint_url("audio.pcm")

    def _endpoint_url(self, endpoint: str) -> str:
        query = urllib.parse.urlencode({"token": self.pair_token.strip().upper()})
        return f"http://{self.host}:8765/{endpoint}?{query}"


class PhoneBridge:
    """Manage local pairing and device status checks for VTUBE Connect on Android."""

    def __init__(self, host: str, pair_token: str, mode: str = "wifi-local"):
        self.device = PhoneDevice(host=host, pair_token=pair_token, mode=mode)
        self.device.validate()

    @staticmethod
    def validate_host(host: str) -> str:
        ip = ipaddress.ip_address(host)
        if not ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError("Host harus IPv4 privat lokal.")
        return str(ip)

    @staticmethod
    def normalize_token(token: str) -> str:
        value = token.strip().upper()
        if len(value) != 6 or not value.isalnum():
            raise ValueError("Pair code harus 6 karakter alfanumerik.")
        return value

    def status(self, timeout: int = 5) -> Dict[str, Any]:
        try:
            with urllib.request.urlopen(self.device.status_url(), timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            data = json.loads(payload)
            self.device.status = "online" if data.get("status") == "ok" else "offline"
            self.device.metadata = data
            return data
        except Exception:
            self.device.status = "offline"
            self.device.metadata = {"status": "offline", "error": "unreachable"}
            return self.device.metadata

    def is_online(self, timeout: int = 5) -> bool:
        return self.status(timeout=timeout).get("status") == "ok"

    def device_snapshot(self) -> Dict[str, Any]:
        return {
            "host": self.device.host,
            "mode": self.device.mode,
            "pair_token": self.device.pair_token,
            "status": self.device.status,
            "metadata": self.device.metadata,
            "camera_url": self.device.camera_url(),
            "screen_url": self.device.screen_url(),
            "audio_url": self.device.audio_url(),
        }


class PhoneDeviceRegistry:
    """Simple registry for active phone devices connected to VTUBE OS."""

    def __init__(self):
        self.devices: Dict[str, PhoneBridge] = {}

    def register(self, bridge: PhoneBridge, name: Optional[str] = None) -> str:
        key = name or bridge.device.host
        self.devices[key] = bridge
        return key

    def unregister(self, name: str) -> None:
        self.devices.pop(name, None)

    def list_status(self) -> List[Dict[str, Any]]:
        return [bridge.device_snapshot() for bridge in self.devices.values()]

    def get(self, name: str) -> PhoneBridge:
        return self.devices[name]


if __name__ == "__main__":
    bridge = PhoneBridge("192.168.1.42", "ABC123")
    print(bridge.device_snapshot())
