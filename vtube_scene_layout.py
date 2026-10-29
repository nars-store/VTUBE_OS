from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SceneSource:
    """A media source in a VTUBE live scene."""

    id: str
    kind: str  # webcam, avatar, phone-screen, gameplay, browser, text, overlay
    name: str
    source_url: str = ""
    x: int = 0
    y: int = 0
    width: int = 640
    height: int = 360
    opacity: float = 1.0
    visible: bool = True
    z_index: int = 0
    options: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "source_url": self.source_url,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "opacity": self.opacity,
            "visible": self.visible,
            "z_index": self.z_index,
            "options": self.options,
        }


class SceneSourceManager:
    """Registry for all sources inside a scene."""

    def __init__(self):
        self.sources: Dict[str, SceneSource] = {}

    def add(self, source: SceneSource) -> SceneSource:
        self.sources[source.id] = source
        return source

    def remove(self, source_id: str) -> None:
        self.sources.pop(source_id, None)

    def list(self) -> List[SceneSource]:
        return sorted(self.sources.values(), key=lambda item: (item.z_index, item.id))

    def get(self, source_id: str) -> SceneSource:
        if source_id not in self.sources:
            raise KeyError(f"Source not found: {source_id}")
        return self.sources[source_id]

    def update(self, source_id: str, **kwargs: Any) -> SceneSource:
        source = self.get(source_id)
        for key, value in kwargs.items():
            if hasattr(source, key):
                setattr(source, key, value)
        return source

    def snapshot(self) -> List[Dict[str, Any]]:
        return [source.as_dict() for source in self.list()]


if __name__ == "__main__":
    manager = SceneSourceManager()
    manager.add(SceneSource("cam", "webcam", "Camera 1", x=0, y=0, width=1280, height=720))
    manager.add(SceneSource("avatar", "avatar", "Luna", x=880, y=120, width=320, height=520, z_index=10))
    print(manager.snapshot())
