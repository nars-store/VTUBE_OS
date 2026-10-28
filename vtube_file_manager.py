from __future__ import annotations

from pathlib import Path
from typing import List


class FileManager:
    """Simple filesystem wrapper for desktop file access."""

    def __init__(self, root: str | Path = Path.home()):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate.resolve()
        return (self.root / candidate).resolve()

    def list_dir(self, path: str | Path = ".") -> List[str]:
        target = self._resolve(path)
        if not target.exists() or not target.is_dir():
            return []
        return sorted(p.name for p in target.iterdir())

    def mkdir(self, path: str | Path) -> Path:
        target = self._resolve(path)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def write_text(self, path: str | Path, content: str) -> Path:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def read_text(self, path: str | Path) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def exists(self, path: str | Path) -> bool:
        return self._resolve(path).exists()
