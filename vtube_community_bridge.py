from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OverlayWidget:
    name: str
    kind: str  # donation, chat, ticker, goal, alert, webcam, brand
    visible: bool = True
    x: int = 0
    y: int = 0
    width: int = 320
    height: int = 180
    opacity: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "visible": self.visible,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "opacity": self.opacity,
            "metadata": self.metadata,
        }


class OverlayPlatformManager:
    """Manages overlays across-platform for donations, chat, labels, and live branding."""

    def __init__(self):
        self.widgets: Dict[str, OverlayWidget] = {}

    def add_widget(self, widget: OverlayWidget) -> OverlayWidget:
        self.widgets[widget.name] = widget
        return widget

    def remove_widget(self, name: str) -> None:
        self.widgets.pop(name, None)

    def list(self) -> List[OverlayWidget]:
        return list(self.widgets.values())

    def snapshot(self) -> List[Dict[str, Any]]:
        return [widget.as_dict() for widget in self.list()]


if __name__ == "__main__":
    manager = OverlayPlatformManager()
    manager.add_widget(OverlayWidget("donation-alert", "donation", x=100, y=80, width=360, height=140))
    manager.add_widget(OverlayWidget("brand-banner", "brand", x=20, y=20, width=300, height=80))
    print(manager.snapshot())
