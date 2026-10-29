from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PairingRecord:
    pair_id: str
    device_id: str
    device_name: str
    fingerprint: str
    capabilities: List[str]
    nonce: str
    challenge: str
    created_at: float
    status: str = "pending"
    session_key: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "fingerprint": self.fingerprint,
            "capabilities": self.capabilities,
            "nonce": self.nonce,
            "challenge": self.challenge,
            "created_at": self.created_at,
            "status": self.status,
            "session_key": self.session_key,
        }


class VTUBEDeviceAuthStore:
    """Stores pending and paired Android-device sessions for desktop VTUBE OS."""

    def __init__(self, local_secret: str = "vtube-os-local-secret"):
        self.local_secret = local_secret
        self.pending: Dict[str, PairingRecord] = {}
        self.paired: Dict[str, PairingRecord] = {}

    def _create_nonce(self) -> str:
        return secrets.token_hex(16)

    def _create_pair_id(self) -> str:
        return secrets.token_hex(12)

    def _derive_session_key(self, device_id: str, nonce: str) -> str:
        payload = f"{device_id}:{nonce}:{self.local_secret}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def request_pairing(
        self,
        device_id: str,
        device_name: str,
        capabilities: Optional[List[str]] = None,
        fingerprint: str = "",
    ) -> Dict[str, Any]:
        pair_id = self._create_pair_id()
        nonce = self._create_nonce()
        challenge = secrets.token_hex(8)
        record = PairingRecord(
            pair_id=pair_id,
            device_id=device_id,
            device_name=device_name,
            fingerprint=fingerprint,
            capabilities=capabilities or ["camera", "microphone", "screen"],
            nonce=nonce,
            challenge=challenge,
            created_at=time.time(),
        )
        self.pending[pair_id] = record
        return {
            "pair_id": pair_id,
            "challenge": challenge,
            "nonce": nonce,
            "status": "pending",
        }

    def confirm_pairing(self, pair_id: str, challenge: str, device_id: str, fingerprint: str) -> Dict[str, Any]:
        record = self.pending.get(pair_id)
        if record is None:
            return {"status": "error", "message": "pair_id_not_found"}
        if record.device_id != device_id:
            return {"status": "error", "message": "device_mismatch"}
        if record.fingerprint and record.fingerprint != fingerprint:
            return {"status": "error", "message": "fingerprint_mismatch"}
        if record.challenge != challenge:
            return {"status": "error", "message": "challenge_mismatch"}

        session_key = self._derive_session_key(device_id, record.nonce)
        record.status = "paired"
        record.session_key = session_key
        self.paired[device_id] = record
        self.pending.pop(pair_id, None)
        return {
            "status": "paired",
            "device_id": device_id,
            "pair_id": pair_id,
            "session_key": session_key,
        }

    def verify_session(self, device_id: str, session_key: str) -> bool:
        record = self.paired.get(device_id)
        if record is None:
            return False
        return hmac.compare_digest(record.session_key, session_key)

    def is_paired(self, device_id: str) -> bool:
        return device_id in self.paired

    def revoke_session(self, device_id: str) -> None:
        self.paired.pop(device_id, None)


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
        digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
        self.password_hashes[username] = f"{salt}:{digest}"
        session = UserSession(user_id=username, username=username, roles=roles or ["user"])
        self.sessions[username] = session
        return session

    def verify_password(self, username: str, password: str) -> bool:
        stored = self.password_hashes.get(username)
        if stored is None:
            return False
        salt, digest = stored.split(":", 1)
        expected = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
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
    auth_store = VTUBEDeviceAuthStore()
    result = auth_store.request_pairing("phone-1", "Pixel 9", ["camera", "microphone", "screen"], "fp-123")
    print(result)
    print(auth_store.confirm_pairing(result["pair_id"], result["challenge"], "phone-1", "fp-123"))
