from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from vtube_scene import Scene
from vtube_scene_source import SceneSource


@dataclass
class RenderLayer:
    source_id: str
    order: int = 0
    opacity: float = 1.0
    visible: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "order": self.order,
            "opacity": self.opacity,
            "visible": self.visible,
        }


class LiveCompositor:
    """A simple compositor for live scene rendering and output preparation."""

    def __init__(self, scene: Optional[Scene] = None):
        self.scene = scene or Scene("default")
        self.layers: List[RenderLayer] = []

    def refresh_layers(self) -> None:
        self.layers = []
        for source in self.scene.sources.list():
            self.layers.append(
                RenderLayer(
                    source_id=source.id,
                    order=source.z_index,
                    opacity=source.opacity,
                    visible=source.visible,
                )
            )
        self.layers.sort(key=lambda item: item.order)

    def compose(self) -> List[Dict[str, Any]]:
        self.refresh_layers()
        return [layer.as_dict() for layer in self.layers]

    def render_preview(self) -> Dict[str, Any]:
        return {
            "scene": self.scene.name,
            "canvas": {"width": self.scene.width, "height": self.scene.height},
            "layers": self.compose(),
            "sources": self.scene.snapshot()["sources"],
        }


if __name__ == "__main__":
    scene = Scene("LiveDemo")
    scene.add_source(SceneSource("game", "gameplay", "Gameplay", width=1920, height=1080, z_index=1), x=0, y=0, width=1920, height=1080)
    scene.add_source(SceneSource("avatar", "avatar", "Luna", width=420, height=620, z_index=25), x=1300, y=90, width=420, height=620)
    compositor = LiveCompositor(scene)
    print(compositor.render_preview())
