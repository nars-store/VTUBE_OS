from __future__ import annotations

from typing import Optional

from vtube_auth_manager import AuthManager
from vtube_permission_manager import PermissionManager


class SecurityPolicy:
    """Compatibility wrapper for VTUBE security policy access."""

    def __init__(self):
        self.auth_manager = AuthManager()
        self.permission_manager = PermissionManager()

    def can(self, username: str, role: str, permission: str) -> bool:
        session = self.auth_manager.sessions.get(username)
        if session is None:
            return False
        if role not in session.roles and "admin" not in session.roles:
            return False
        return self.permission_manager.can_access(role, permission)


if __name__ == "__main__":
    policy = SecurityPolicy()
    print(policy.can("admin", "admin", "stream"))
