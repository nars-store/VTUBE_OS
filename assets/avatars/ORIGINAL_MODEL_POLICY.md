"""OBS / RTMP / YouTube output helper for VTUBE OS.

This file builds stream target data and FFmpeg command templates so the VTUBE OS
scene can be pushed to OBS or RTMP endpoints such as YouTube Live.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StreamTarget:
    name: str
    kind: str = "rtmp"
    endpoint: str = "rtmp://a.rtmp.youtube.com/live2"
    stream_key: str = "your-stream-key"
    fps: int = 30
    bitrate_kbps: int = 2500
    width: int = 1920
    height: int = 1080
    enabled: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "endpoint": self.endpoint,
            "stream_key": self.stream_key,
            "fps": self.fps,
            "bitrate_kbps": self.bitrate_kbps,
            "width": self.width,
            "height": self.height,
            "enabled": self.enabled,
        }


class StreamOutputManager:
    """Build RTMP/YouTube/OBS stream configuration for the live scene."""

    def __init__(self):
        self.targets: Dict[str, StreamTarget] = {}

    def add_target(self, target: StreamTarget) -> StreamTarget:
        self.targets[target.name] = target
        return target

    def build_ffmpeg_command(self, target: StreamTarget, input_sources: List[str]) -> str:
        inputs = " ".join(f"-f lavfi -i color=c=black:s={target.width}x{target.height}:d=1" for _ in input_sources)
        return (
            f"ffmpeg {inputs} "
            f"-c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p "
            f"-b:v {target.bitrate_kbps}k -r {target.fps} "
            f"-f flv \"{target.endpoint}/{target.stream_key}\""
        )

    def snapshot(self) -> List[Dict[str, Any]]:
        return [target.as_dict() for target in self.targets.values()]


if __name__ == "__main__":
    manager = StreamOutputManager()
    target = StreamTarget("youtube-live", "youtube", "rtmp://a.rtmp.youtube.com/live2", "demo-stream-key")
    manager.add_target(target)
    print(manager.snapshot())
    print(manager.build_ffmpeg_command(target, ["webcam", "phone-camera", "avatar"]))
