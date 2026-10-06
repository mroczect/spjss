"""Optional password storage via the OS keyring.

If the keyring package is not installed or no backend is available,
all operations become no-ops and the caller should fall back to
asking the user every time. No insecure fallback is provided on
purpose.
"""

from __future__ import annotations

SERVICE = "spjss"

try:
    import keyring  # type: ignore
    from keyring.errors import KeyringError  # type: ignore

    _IMPORT_OK = True
except Exception:
    keyring = None  # type: ignore
    KeyringError = Exception  # type: ignore
    _IMPORT_OK = False


def is_available() -> bool:
    if not _IMPORT_OK:
        return False
    try:
        backend = keyring.get_keyring()  # type: ignore[union-attr]
        name = type(backend).__name__.lower()
        if "fail" in name or "null" in name:
            return False
        return True
    except Exception:
        return False


def save(email: str, password: str) -> bool:
    if not (_IMPORT_OK and is_available()):
        return False
    if not email or not password:
        return False
    try:
        keyring.set_password(SERVICE, email, password)  # type: ignore
        return True
    except Exception:
        return False


def load(email: str) -> str | None:
    if not (_IMPORT_OK and is_available()):
        return None
    if not email:
        return None
    try:
        return keyring.get_password(SERVICE, email)  # type: ignore
    except Exception:
        return None


def delete(email: str) -> bool:
    if not (_IMPORT_OK and is_available()):
        return False
    if not email:
        return False
    try:
        keyring.delete_password(SERVICE, email)  # type: ignore
        return True
    except Exception:
        return False


def backend_name() -> str:
    if not _IMPORT_OK:
        return "(keyring not installed)"
    try:
        return type(keyring.get_keyring()).__name__  # type: ignore
    except Exception:
        return "(unknown)"
