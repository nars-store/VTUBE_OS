from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AppDescriptor:
    name: str
    command: str
    icon: str = "◉"
    category: str = "system"
    description: str = ""
    active: bool = True


class AppRegistry:
    """Static registry for VTUBE OS desktop apps."""

    def __init__(self):
        self.apps: Dict[str, AppDescriptor] = {}

    def register(self, app: AppDescriptor) -> None:
        self.apps[app.name] = app

    def register_many(self, apps: List[AppDescriptor]) -> None:
        for app in apps:
            self.register(app)

    def get(self, name: str) -> AppDescriptor:
        if name not in self.apps:
            raise KeyError(f"App not found: {name}")
        return self.apps[name]

    def list(self, category: Optional[str] = None) -> List[AppDescriptor]:
        if category is None:
            return list(self.apps.values())
        return [app for app in self.apps.values() if app.category == category]
