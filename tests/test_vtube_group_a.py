import json
import tempfile
import unittest
from pathlib import Path

from vtube_app_registry import AppDescriptor, AppRegistry
from vtube_file_manager import FileManager
from vtube_session import SessionManager
from vtube_settings import SettingsManager
from vtube_theme import ThemeManager
from vtube_workspace import WorkspaceManager


class GroupATests(unittest.TestCase):
    def test_app_registry(self):
        registry = AppRegistry()
        registry.register(AppDescriptor("Control Center", "control-center", icon="◉"))
        self.assertEqual(registry.get("Control Center").command, "control-center")

    def test_theme_manager(self):
        theme = ThemeManager("dark")
        self.assertIn("bg", theme.current_palette())
        light = theme.set_theme("light")
        self.assertEqual(light["text"], "#1c2333")

    def test_settings_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = SettingsManager(tmp)
            settings.set("theme", "light")
            loaded = SettingsManager(tmp)
            self.assertEqual(loaded.get("theme"), "light")

    def test_session_manager(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = SessionManager(tmp)
            session.login("nars")
            self.assertTrue(session.logged_in)
            self.assertEqual(session.current_user, "nars")

    def test_file_manager(self):
        with tempfile.TemporaryDirectory() as tmp:
            fm = FileManager(tmp)
            target = fm.write_text("notes/demo.txt", "hello")
            self.assertTrue(target.exists())
            self.assertEqual(fm.read_text("notes/demo.txt"), "hello")

    def test_workspace_manager(self):
        ws = WorkspaceManager()
        win = ws.open_window("Live Studio", "Preview")
        self.assertEqual(win.app_name, "Live Studio")
        self.assertEqual(len(ws.list_windows()), 1)


if __name__ == "__main__":
    unittest.main()
