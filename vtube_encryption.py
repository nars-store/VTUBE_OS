from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Permission:
    name: str
    description: str = ""
    allowed_roles: List[str] = field(default_factory=lambda: ["user", "admin"])


class PermissionManager:
    """Checks if a role can access a protected VTUBE OS capability."""

    def __init__(self):
        self.permissions: Dict[str, Permission] = {
            "desktop": Permission("desktop", "Access desktop shell", ["user", "admin"]),
            "camera": Permission("camera", "Use camera input", ["user", "admin"]),
            "audio": Permission("audio", "Use mic and mixer", ["user", "admin"]),
            "stream": Permission("stream", "Start live stream", ["user", "admin"]),
            "settings": Permission("settings", "Configure settings", ["admin"]),
            "pairing": Permission("pairing", "Pair phone device", ["user", "admin"]),
        }

    def can_access(self, role: str, permission_name: str) -> bool:
        permission = self.permissions.get(permission_name)
        if permission is None:
            return False
        return role in permission.allowed_roles

    def add_permission(self, permission: Permission) -> None:
        self.permissions[permission.name] = permission


if __name__ == "__main__":
    manager = PermissionManager()
    print(manager.can_access("admin", "settings"))
    print(manager.can_access("user", "camera"))
