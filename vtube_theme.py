from __future__ import annotations

from typing import Dict


class ThemeManager:
    """Dark/light theme palette for the VTUBE OS shell."""

    def __init__(self, theme_name: str = "dark"):
        self.theme_name = theme_name
        self.themes: Dict[str, Dict[str, str]] = {
            "dark": {
                "bg": "#0b0d14",
                "panel": "#141827",
                "panel2": "#1b2032",
                "panel3": "#101827",
                "text": "#f2f4ff",
                "muted": "#9ba4bd",
                "accent": "#9b7bff",
                "cyan": "#64e6f2",
                "green": "#67e6ac",
                "amber": "#ffca78",
                "red": "#ff7c94",
            },
            "light": {
                "bg": "#eef3ff",
                "panel": "#ffffff",
                "panel2": "#e8ecf8",
                "panel3": "#dfe7ff",
                "text": "#1c2333",
                "muted": "#556381",
                "accent": "#6d5efc",
                "cyan": "#1a7d8e",
                "green": "#2c9d6c",
                "amber": "#d28d1a",
                "red": "#d75b6b",
            },
        }

    def set_theme(self, theme_name: str) -> Dict[str, str]:
        if theme_name not in self.themes:
            raise ValueError(f"Unsupported theme: {theme_name}")
        self.theme_name = theme_name
        return self.themes[theme_name]

    def current_palette(self) -> Dict[str, str]:
        return self.themes[self.theme_name]
