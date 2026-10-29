from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Optional


class SimpleCipher:
    """Simple symmetric helper for local VTUBE OS secrets and pairing tokens."""

    def __init__(self, secret: str):
        self.secret = secret.encode('utf-8')

    def _derive_key(self, salt: bytes) -> bytes:
        return hashlib.sha256(self.secret + salt).digest()

    def encrypt(self, plaintext: str) -> str:
        salt = b'vtube-os-v1'
        key = self._derive_key(salt)
        signature = hmac.new(key, plaintext.encode('utf-8'), hashlib.sha256).digest()
        payload = plaintext.encode('utf-8') + b'|' + signature
        return base64.b64encode(payload).decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        raw = base64.b64decode(ciphertext.encode('utf-8'))
        payload, signature = raw.rsplit(b'|', 1)
        salt = b'vtube-os-v1'
        key = self._derive_key(salt)
        expected = hmac.new(key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError('Ciphertext tidak valid atau rusak.')
        return payload.decode('utf-8')


if __name__ == "__main__":
    cipher = SimpleCipher('vtube-secret-key')
    token = cipher.encrypt('phone-token-abc123')
    print(token)
    print(cipher.decrypt(token))
