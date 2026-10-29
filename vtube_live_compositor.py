from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from vtube_scene_layout import SceneLayout
from vtube_scene_source import SceneSource, SceneSourceManager


@dataclass
class Scene:
    """A live scene composed of video/audio sources and layout positions."""

    name: str
    width: int = 1920
    height: int = 1080
    active: bool = True
    sources: SceneSourceManager = field(default_factory=SceneSourceManager)
    layout: SceneLayout = field(default_factory=SceneLayout)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.layout = SceneLayout(width=self.width, height=self.height)

    def add_source(self, source: SceneSource, *, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, opacity: float = 1.0) -> SceneSource:
        added = self.sources.add(source)
        if x is not None or y is not None or width is not None or height is not None:
            self.layout.set_source(source.id, x or added.x, y or added.y, width or added.width, height or added.height, opacity=opacity, visible=added.visible)
        else:
            self.layout.set_source(source.id, added.x, added.y, added.width, added.height, opacity=opacity, visible=added.visible)
        return added

    def remove_source(self, source_id: str) -> None:
        self.sources.remove(source_id)
        self.layout.remove(source_id)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "active": self.active,
            "sources": self.sources.snapshot(),
            "layout": self.layout.snapshot(),
            "metadata": self.metadata,
        }


if __name__ == "__main__":
    scene = Scene("GamingStream")
    scene.add_source(SceneSource("cam", "webcam", "Main Camera", width=1280, height=720), x=0, y=0, width=1280, height=720)
    scene.add_source(SceneSource("avatar", "avatar", "Luna", width=420, height=620, z_index=10), x=1180, y=100, width=420, height=620)
    print(scene.snapshot())
