from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlatformConfig:
    name: str
    kind: str  # youtube, twitch, tiktok, kick, custom
    enabled: bool = True
    endpoint: str = ""
    stream_key: str = ""
    account_id: str = ""
    channel_name: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "stream_key": self.stream_key,
            "account_id": self.account_id,
            "channel_name": self.channel_name,
            "settings": self.settings,
        }


class PlatformRegistry:
    """Registry for all external streaming/community platforms used by VTUBE OS."""

    def __init__(self):
        self.platforms: Dict[str, PlatformConfig] = {}

    def register(self, config: PlatformConfig) -> PlatformConfig:
        self.platforms[config.name] = config
        return config

    def get(self, name: str) -> PlatformConfig:
        if name not in self.platforms:
            raise KeyError(f"Platform not found: {name}")
        return self.platforms[name]

    def list(self) -> List[PlatformConfig]:
        return list(self.platforms.values())

    def disable(self, name: str) -> None:
        platform = self.get(name)
        platform.enabled = False

    def enable(self, name: str) -> None:
        platform = self.get(name)
        platform.enabled = True


if __name__ == "__main__":
    registry = PlatformRegistry()
    registry.register(PlatformConfig("YouTube", "youtube", endpoint="rtmp://a.rtmp.youtube.com/live2", channel_name="vtube-demo"))
    registry.register(PlatformConfig("Twitch", "twitch", endpoint="rtmp://live.twitch.tv/app", channel_name="vtube-demo"))
    print([p.name for p in registry.list()])
