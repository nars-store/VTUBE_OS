from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "vtube-os"


class SettingsManager:
    """Persist VTUBE OS desktop preferences."""

    def __init__(self, config_dir: str | Path = DEFAULT_CONFIG_DIR):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path = self.config_dir / "settings.json"
        self.settings: Dict[str, Any] = self._load_defaults()

    def _load_defaults(self) -> Dict[str, Any]:
        defaults = {
            "theme": "dark",
            "language": "id-ID",
            "wallpaper": "default",
            "workspace": "Home",
            "show_desktop_icons": True,
            "volume": 80,
            "audio_device": "default",
            "network_mode": "local",
            "auto_login": False,
        }
        if self.settings_path.exists():
            try:
                data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return defaults
            if isinstance(data, dict):
                defaults.update(data)
        return defaults

    def save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(json.dumps(self.settings, indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save()
