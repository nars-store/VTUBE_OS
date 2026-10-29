from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import hmac
import secrets
import time


@dataclass
class UserSession:
    user_id: str
    username: str
    roles: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    active: bool = True


class AuthManager:
    """Simple auth layer for VTUBE OS local sessions and desktop access."""

    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.password_hashes: Dict[str, str] = {}

    def register_user(self, username: str, password: str, roles: Optional[List[str]] = None) -> UserSession:
        salt = secrets.token_hex(8)
        digest = hashlib.sha256(f"{salt}:{password}".encode('utf-8')).hexdigest()
        self.password_hashes[username] = f"{salt}:{digest}"
        session = UserSession(
            user_id=username,
            username=username,
            roles=roles or ["user"],
        )
        self.sessions[username] = session
        return session

    def verify_password(self, username: str, password: str) -> bool:
        stored = self.password_hashes.get(username)
        if stored is None:
            return False
        salt, digest = stored.split(":", 1)
        expected = hashlib.sha256(f"{salt}:{password}".encode('utf-8')).hexdigest()
        return hmac.compare_digest(digest, expected)

    def login(self, username: str, password: str) -> Optional[UserSession]:
        if not self.verify_password(username, password):
            return None
        session = self.sessions.get(username)
        if session is not None:
            session.last_seen = time.time()
            session.active = True
        return session

    def logout(self, username: str) -> None:
        session = self.sessions.get(username)
        if session is not None:
            session.active = False


if __name__ == "__main__":
    auth = AuthManager()
    auth.register_user("admin", "secret123", roles=["admin", "user"])
    print(auth.login("admin", "secret123"))
