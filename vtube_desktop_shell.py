from __future__ import annotations

from typing import Dict, List

from vtube_app_registry import AppDescriptor, AppRegistry
from vtube_file_manager import FileManager
from vtube_settings import SettingsManager
from vtube_session import SessionManager
from vtube_theme import ThemeManager
from vtube_workspace import WorkspaceManager


class DesktopShell:
    """Core VTUBE OS desktop shell foundation for Group A."""

    def __init__(self):
        self.theme = ThemeManager()
        self.apps = AppRegistry()
        self.settings = SettingsManager()
        self.session = SessionManager()
        self.files = FileManager()
        self.workspace = WorkspaceManager()
        self.launch_history: List[str] = []
        self.register_default_apps()

    def register_default_apps(self) -> None:
        self.apps.register_many(
            [
                AppDescriptor("Control Center", "control-center", "◉", "core", "Main VTUBE dashboard"),
                AppDescriptor("Live Studio", "live-studio", "●", "studio", "Live scene and stream control"),
                AppDescriptor("Avatar Studio", "avatar-studio", "✦", "studio", "Model and expression workspace"),
                AppDescriptor("Audio Studio", "audio-studio", "♫", "audio", "Microphone and audio controls"),
                AppDescriptor("Donation Center", "donation-center", "♡", "social", "Donation goal and overlay"),
                AppDescriptor("Connect Hub", "connect-hub", "⌁", "network", "Phone and device connection"),
                AppDescriptor("File Manager", "file-manager", "▣", "system", "Local file browser"),
                AppDescriptor("Settings", "settings", "⚙", "system", "System preferences"),
            ]
        )

    def set_theme(self, theme_name: str) -> Dict[str, str]:
        palette = self.theme.set_theme(theme_name)
        self.settings.set("theme", theme_name)
        return palette

    def login(self, username: str) -> None:
        self.session.login(username)

    def logout(self) -> None:
        self.session.logout()

    def launch_app(self, app_name: str):
        app = self.apps.get(app_name)
        self.launch_history.append(app_name)
        return self.workspace.open_window(app.name, app.description or app.name)

    def write_note(self, relative_path: str, content: str) -> str:
        path = self.files.write_text(relative_path, content)
        return str(path)


def build_default_shell() -> DesktopShell:
    return DesktopShell()


if __name__ == "__main__":
    shell = build_default_shell()
    print("VTUBE OS shell initialized")
    print([app.name for app in shell.apps.list()])
