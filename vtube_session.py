from __future__ import annotations

import json
from pathlib import Path


class SessionManager:
    """Tracks active user session and selected workspace."""

    def __init__(self, config_dir: str | Path = Path.home() / ".config" / "vtube-os"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.session_path = self.config_dir / "session.json"
        self.current_user = "guest"
        self.active_workspace = "Home"
        self.logged_in = False
        self._load()

    def _load(self) -> None:
        if not self.session_path.exists():
            return
        try:
            data = json.loads(self.session_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict):
            self.current_user = data.get("current_user", self.current_user)
            self.active_workspace = data.get("active_workspace", self.active_workspace)
            self.logged_in = bool(data.get("logged_in", False))

    def save(self) -> None:
        payload = {
            "current_user": self.current_user,
            "active_workspace": self.active_workspace,
            "logged_in": self.logged_in,
        }
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.session_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def login(self, username: str) -> None:
        self.current_user = username
        self.logged_in = True
        self.save()

    def logout(self) -> None:
        self.current_user = "guest"
        self.active_workspace = "Home"
        self.logged_in = False
        self.save()

    def select_workspace(self, workspace_name: str) -> None:
        self.active_workspace = workspace_name
        self.save()
