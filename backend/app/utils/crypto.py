"""Encryption utilities for sensitive data like API keys."""

import base64
import hashlib

from cryptography.fernet import Fernet


def _derive_key(secret: str) -> bytes:
    """Derive a Fernet-compatible key from an arbitrary secret string."""
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet(secret: str) -> Fernet:
    """Create a Fernet instance from a secret string."""
    return Fernet(_derive_key(secret))


def encrypt_value(value: str, secret: str) -> str:
    """Encrypt a string value. Returns the ciphertext as a string."""
    f = get_fernet(secret)
    return f.encrypt(value.encode()).decode()


def decrypt_value(ciphertext: str, secret: str) -> str:
    """Decrypt a ciphertext string back to the original value."""
    f = get_fernet(secret)
    return f.decrypt(ciphertext.encode()).decode()
