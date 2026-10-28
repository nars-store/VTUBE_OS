from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DesktopWindow:
    app_name: str
    title: str
    state: str = "normal"
    x: int = 0
    y: int = 0
    width: int = 640
    height: int = 420
    persistent: bool = False


class WorkspaceManager:
    """Desktop workspaces and app windows."""

    def __init__(self):
        self.workspaces: Dict[str, List[DesktopWindow]] = {"Home": []}
        self.active_workspace = "Home"

    def switch(self, workspace_name: str) -> None:
        if workspace_name not in self.workspaces:
            self.workspaces[workspace_name] = []
        self.active_workspace = workspace_name

    def open_window(self, app_name: str, title: str, width: int = 640, height: int = 420) -> DesktopWindow:
        win = DesktopWindow(app_name=app_name, title=title, width=width, height=height)
        self.workspaces.setdefault(self.active_workspace, []).append(win)
        return win

    def list_windows(self, workspace_name: Optional[str] = None) -> List[DesktopWindow]:
        name = workspace_name or self.active_workspace
        return list(self.workspaces.get(name, []))
