from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class LayoutItem:
    source_id: str
    x: int = 0
    y: int = 0
    width: int = 640
    height: int = 360
    opacity: float = 1.0
    visible: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "opacity": self.opacity,
            "visible": self.visible,
        }


class SceneLayout:
    """Canvas layout manager for live scenes."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.items: Dict[str, LayoutItem] = {}

    def set_source(self, source_id: str, x: int, y: int, width: int, height: int, opacity: float = 1.0, visible: bool = True) -> LayoutItem:
        item = LayoutItem(source_id=source_id, x=x, y=y, width=width, height=height, opacity=opacity, visible=visible)
        self.items[source_id] = item
        return item

    def remove(self, source_id: str) -> None:
        self.items.pop(source_id, None)

    def snapshot(self) -> List[Dict[str, Any]]:
        return [item.as_dict() for item in self.items.values()]

    def fit(self, source_id: str, mode: str = "cover") -> LayoutItem:
        item = self.items.get(source_id)
        if item is None:
            raise KeyError(f"Source {source_id} is not in layout")
        if mode == "cover":
            item.width = self.width
            item.height = self.height
        elif mode == "fit":
            item.width = self.width // 2
            item.height = self.height // 2
        return item


if __name__ == "__main__":
    layout = SceneLayout()
    layout.set_source("cam", 0, 0, 1280, 720)
    layout.set_source("avatar", 1100, 150, 480, 720, opacity=0.98)
    print(layout.snapshot())
