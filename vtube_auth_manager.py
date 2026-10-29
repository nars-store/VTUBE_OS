from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import hmac
import secrets
import time


@dataclass
class AuthToken:
    subject: str
    issued_at: float
    expires_at: float
    scopes: List[str] = field(default_factory=list)
    token: str = ""

    def is_valid(self, now: Optional[float] = None) -> bool:
        if self.token == "":
            return False
        current = time.time() if now is None else now
        return current < self.expires_at


class SecurityPolicy:
    """Core security policy for VTUBE OS tokens, trusted devices, and auth scopes."""

    def __init__(self):
        self.allowed_scopes = {
            "desktop",
            "stream",
            "avatar",
            "audio",
            "camera",
            "network",
            "settings",
            "admin",
        }
        self.trusted_devices: Dict[str, str] = {}
        self.tokens: Dict[str, AuthToken] = {}

    def create_token(self, subject: str, scopes: List[str], ttl_seconds: int = 3600) -> AuthToken:
        for scope in scopes:
            if scope not in self.allowed_scopes:
                raise ValueError(f"Scope tidak diizinkan: {scope}")
        token_value = secrets.token_urlsafe(24)
        expires_at = time.time() + ttl_seconds
        token = AuthToken(
            subject=subject,
            issued_at=time.time(),
            expires_at=expires_at,
            scopes=scopes,
            token=token_value,
        )
        self.tokens[token_value] = token
        return token

    def verify_token(self, token: str, required_scope: Optional[str] = None) -> Optional[AuthToken]:
        record = self.tokens.get(token)
        if record is None:
            return None
        if not record.is_valid():
            self.tokens.pop(token, None)
            return None
        if required_scope is not None and required_scope not in record.scopes:
            return None
        return record

    def trust_device(self, device_id: str, fingerprint: str) -> None:
        self.trusted_devices[device_id] = fingerprint

    def is_trusted_device(self, device_id: str, fingerprint: str) -> bool:
        return self.trusted_devices.get(device_id) == fingerprint


if __name__ == "__main__":
    policy = SecurityPolicy()
    token = policy.create_token("nars", ["desktop", "stream", "camera"], ttl_seconds=7200)
    print(token.token)
    print(policy.verify_token(token.token, "stream") is not None)
