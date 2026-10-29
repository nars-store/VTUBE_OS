from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any, Dict, List, Optional

PENDING: Dict[str, Dict[str, Any]] = {}
PAIRED: Dict[str, Dict[str, Any]] = {}


def create_nonce() -> str:
    return secrets.token_hex(16)


def derive_session_key(device_id: str, host_id: str, nonce: str, secret: str) -> str:
    payload = f"{device_id}:{host_id}:{nonce}:{secret}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def request_pairing(
    device_id: str,
    device_name: str,
    capabilities: Optional[List[str]] = None,
    fingerprint: str = "",
    host_id: str = "desktop-vtube",
) -> Dict[str, Any]:
    pair_id = secrets.token_hex(12)
    nonce = create_nonce()
    challenge = secrets.token_hex(8)

    PENDING[pair_id] = {
        "pair_id": pair_id,
        "device_id": device_id,
        "device_name": device_name,
        "capabilities": capabilities or ["camera", "microphone", "screen"],
        "fingerprint": fingerprint,
        "nonce": nonce,
        "challenge": challenge,
        "host_id": host_id,
        "created_at": time.time(),
        "status": "pending",
    }

    return {
        "pair_id": pair_id,
        "challenge": challenge,
        "nonce": nonce,
        "status": "pending",
    }


def confirm_pairing(pair_id: str, challenge: str, device_id: str, fingerprint: str, host_id: str = "desktop-vtube") -> Dict[str, Any]:
    pending = PENDING.get(pair_id)
    if not pending:
        return {"status": "error", "message": "pair_id_not_found"}

    if pending["device_id"] != device_id:
        return {"status": "error", "message": "device_mismatch"}
    if pending["fingerprint"] and pending["fingerprint"] != fingerprint:
        return {"status": "error", "message": "fingerprint_mismatch"}
    if pending["challenge"] != challenge:
        return {"status": "error", "message": "challenge_mismatch"}

    session_key = derive_session_key(device_id, host_id, pending["nonce"], "vtube-os-local-secret")
    PAIRED[device_id] = {
        "pair_id": pair_id,
        "device_id": device_id,
        "device_name": pending["device_name"],
        "capabilities": pending["capabilities"],
        "session_key": session_key,
        "host_id": host_id,
        "created_at": time.time(),
        "status": "paired",
    }
    PENDING.pop(pair_id, None)
    return {
        "status": "paired",
        "device_id": device_id,
        "pair_id": pair_id,
        "session_key": session_key,
    }


def verify_session(device_id: str, session_key: str) -> bool:
    pair = PAIRED.get(device_id)
    if not pair:
        return False
    return pair.get("session_key") == session_key


if __name__ == "__main__":
    req = request_pairing("phone-primary", "Pixel 9", ["camera", "microphone", "screen"], "fp-demo")
    print(req)
    print(confirm_pairing(req["pair_id"], req["challenge"], "phone-primary", "fp-demo"))
