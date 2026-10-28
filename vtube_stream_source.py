from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class StreamSource:
    name: str
    kind: str  # phone-camera, phone-screen, webcam, desktop, silence
    input_url: str = ""
    audio_url: str = ""
    width: int = 1280
    height: int = 720
    fps: int = 30
    audio_rate: int = 16000
    channels: int = 1

    def is_audio_source(self) -> bool:
        return bool(self.audio_url)


class SourceCatalog:
    """Simple catalog of video and audio sources for the live stream."""

    def __init__(self):
        self.sources: Dict[str, StreamSource] = {}

    def register(self, source: StreamSource) -> None:
        self.sources[source.name] = source

    def get(self, name: str) -> StreamSource:
        if name not in self.sources:
            raise KeyError(f"Source not found: {name}")
        return self.sources[name]

    def list_names(self) -> List[str]:
        return sorted(self.sources.keys())

    @staticmethod
    def phone_camera(host: str, token: str, width: int = 1280, height: int = 720, fps: int = 30) -> StreamSource:
        from vtube_phone_bridge import PhoneBridge

        bridge = PhoneBridge(host, token)
        return StreamSource(
            name="phone-camera",
            kind="phone-camera",
            input_url=bridge.device.camera_url(),
            width=width,
            height=height,
            fps=fps,
        )

    @staticmethod
    def phone_screen(host: str, token: str, width: int = 1280, height: int = 720, fps: int = 30) -> StreamSource:
        from vtube_phone_bridge import PhoneBridge

        bridge = PhoneBridge(host, token)
        return StreamSource(
            name="phone-screen",
            kind="phone-screen",
            input_url=bridge.device.screen_url(),
            width=width,
            height=height,
            fps=fps,
        )

    @staticmethod
    def phone_mic(host: str, token: str, rate: int = 16000) -> StreamSource:
        from vtube_phone_bridge import PhoneBridge

        bridge = PhoneBridge(host, token)
        return StreamSource(
            name="phone-mic",
            kind="phone-mic",
            input_url=bridge.device.audio_url(),
            audio_rate=rate,
            channels=1,
        )

    @staticmethod
    def silence() -> StreamSource:
        return StreamSource(
            name="silence",
            kind="silence",
            input_url="",
            audio_url="",
        )
