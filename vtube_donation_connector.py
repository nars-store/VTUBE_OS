from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StreamSession:
    platform: str
    status: str = "idle"  # idle, connecting, live, error
    stream_key: str = ""
    rtmp_url: str = ""
    bitrate_kbps: int = 2500
    fps: int = 30
    width: int = 1920
    height: int = 1080
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "status": self.status,
            "stream_key": self.stream_key,
            "rtmp_url": self.rtmp_url,
            "bitrate_kbps": self.bitrate_kbps,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "metadata": self.metadata,
        }


class StreamPlatformManager:
    """Manage platform destinations and stream status for VTUBE OS."""

    def __init__(self):
        self.sessions: Dict[str, StreamSession] = {}

    def register(self, platform: str, stream_key: str, rtmp_url: str, **kwargs: Any) -> StreamSession:
        session = StreamSession(platform=platform, stream_key=stream_key, rtmp_url=rtmp_url, **kwargs)
        self.sessions[platform] = session
        return session

    def get(self, platform: str) -> StreamSession:
        if platform not in self.sessions:
            raise KeyError(f"Stream session not found: {platform}")
        return self.sessions[platform]

    def set_status(self, platform: str, status: str) -> StreamSession:
        session = self.get(platform)
        session.status = status
        return session

    def list(self) -> List[StreamSession]:
        return list(self.sessions.values())


if __name__ == "__main__":
    mgr = StreamPlatformManager()
    mgr.register("youtube", "live-key-123", "rtmp://a.rtmp.youtube.com/live2", bitrate_kbps=3500, fps=30)
    print(mgr.get("youtube").as_dict())
