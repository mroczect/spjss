"""
Python ctypes binding for librjss-ffi.

The native library must be reachable from this file or via the
LIBRJSS_FFI environment variable.

    Linux    liblibrjss_ffi.so
    macOS    liblibrjss_ffi.dylib
    Windows  librjss_ffi.dll

Build the library with:

    cargo build -p librjss-ffi --release
"""

from __future__ import annotations

import ctypes
import json as _json
import os
import platform
from ctypes import (
    CDLL,
    POINTER,
    Structure,
    byref,
    c_char_p,
    c_int32,
    c_size_t,
    c_uint8,
    c_uint32,
    c_uint64,
    c_void_p,
)
from typing import Any, Optional, Sequence, Union

__version__ = "2.3.0"

__all__ = [
    "RjssClient",
    "JssError",
    "JssClientConfig",
    "version",
    "last_error",
    "from_env",
    "JSS_OK",
    "JSS_ERR_CONFIG",
    "JSS_ERR_VALIDATION",
    "JSS_ERR_NETWORK",
    "JSS_ERR_HTTP",
    "JSS_ERR_API",
    "JSS_ERR_AUTH",
    "JSS_ERR_CSRF",
    "JSS_ERR_PERMISSION",
    "JSS_ERR_SITENAME_MISMATCH",
    "JSS_ERR_NOT_AUTHENTICATED",
    "JSS_ERR_RATE_LIMITED",
    "JSS_ERR_PARSE",
    "JSS_ERR_EXPIRED",
    "JSS_ERR_CANCELLED",
    "JSS_ERR_FILE_OPERATION",
    "JSS_ERR_INTERNAL",
    "JSS_ERR_NULL_POINTER",
    "JSS_ERR_UTF8",
    "JSS_ERR_PANIC",
    "JSS_FLAG_INSECURE_SSL",
    "JSS_FLAG_NO_READONLY_GUARD",
]


# ── constants ────────────────────────────────────────────────────────

JSS_OK = 0

JSS_ERR_CONFIG = -1
JSS_ERR_VALIDATION = -2
JSS_ERR_NETWORK = -3
JSS_ERR_HTTP = -4
JSS_ERR_API = -5
JSS_ERR_AUTH = -6
JSS_ERR_CSRF = -7
JSS_ERR_PERMISSION = -8
JSS_ERR_SITENAME_MISMATCH = -9
JSS_ERR_NOT_AUTHENTICATED = -10
JSS_ERR_RATE_LIMITED = -11
JSS_ERR_PARSE = -12
JSS_ERR_EXPIRED = -13
JSS_ERR_CANCELLED = -14
JSS_ERR_FILE_OPERATION = -15
JSS_ERR_INTERNAL = -16
JSS_ERR_NULL_POINTER = -17
JSS_ERR_UTF8 = -18
JSS_ERR_PANIC = -19

JSS_FLAG_INSECURE_SSL = 1 << 0
JSS_FLAG_NO_READONLY_GUARD = 1 << 1

_ERROR_NAMES: dict[int, str] = {
    JSS_ERR_CONFIG: "CONFIG",
    JSS_ERR_VALIDATION: "VALIDATION",
    JSS_ERR_NETWORK: "NETWORK",
    JSS_ERR_HTTP: "HTTP",
    JSS_ERR_API: "API",
    JSS_ERR_AUTH: "AUTH",
    JSS_ERR_CSRF: "CSRF",
    JSS_ERR_PERMISSION: "PERMISSION",
    JSS_ERR_SITENAME_MISMATCH: "SITENAME_MISMATCH",
    JSS_ERR_NOT_AUTHENTICATED: "NOT_AUTHENTICATED",
    JSS_ERR_RATE_LIMITED: "RATE_LIMITED",
    JSS_ERR_PARSE: "PARSE",
    JSS_ERR_EXPIRED: "EXPIRED",
    JSS_ERR_CANCELLED: "CANCELLED",
    JSS_ERR_FILE_OPERATION: "FILE_OPERATION",
    JSS_ERR_INTERNAL: "INTERNAL",
    JSS_ERR_NULL_POINTER: "NULL_POINTER",
    JSS_ERR_UTF8: "UTF8",
    JSS_ERR_PANIC: "PANIC",
}


# ── struct ───────────────────────────────────────────────────────────

class JssClientConfig(Structure):
    _fields_ = [
        ("base_url", c_char_p),
        ("auth_kind", c_char_p),
        ("principal", c_char_p),
        ("secret", c_char_p),
        ("expected_sitename", c_char_p),
        ("flags", c_uint32),
        ("_reserved", c_uint32),
        ("timeout_secs", c_uint64),
        ("max_retries", c_uint32),
        ("_reserved2", c_uint32),
    ]


# ── library loading ──────────────────────────────────────────────────

def _lib_filename() -> str:
    system = platform.system()
    if system == "Windows":
        return "librjss_ffi.dll"
    if system == "Darwin":
        return "liblibrjss_ffi.dylib"
    return "liblibrjss_ffi.so"


def _target_triple() -> Optional[str]:
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Windows":
        if machine in ("amd64", "x86_64"):
            return "x86_64-pc-windows-msvc"
        if machine in ("x86", "i386", "i686"):
            return "i686-pc-windows-msvc"
    elif system == "Darwin":
        if machine == "arm64":
            return "aarch64-apple-darwin"
        if machine == "x86_64":
            return "x86_64-apple-darwin"
    elif system == "Linux":
        if machine == "x86_64":
            return "x86_64-unknown-linux-gnu"
        if machine in ("aarch64", "arm64"):
            return "aarch64-unknown-linux-gnu"
    return None


def _locate_library(explicit: Optional[str] = None) -> str:
    """Return the absolute path to the shared library, or the bare name
    if no candidate file exists (letting the OS loader search PATH)."""

    if explicit:
        if not os.path.isfile(explicit):
            raise FileNotFoundError(f"librjss-ffi not found at {explicit!r}")
        return os.path.abspath(explicit)

    name = _lib_filename()
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)

    candidates: list[str] = []

    env = os.environ.get("LIBRJSS_FFI")
    if env:
        candidates.append(env)

    # sibling of this file
    candidates.append(os.path.join(here, name))

    # per-platform subdirectory: lib/linux-x86_64/liblibrjss_ffi.so
    triple = _target_triple()
    if triple:
        candidates.append(os.path.join(here, triple, name))
        candidates.append(
            os.path.join(parent, "target", triple, "release", name)
        )

    # plain cargo target dir
    candidates.append(os.path.join(parent, "target", "release", name))

    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)

    return name


def _load(path: Optional[str] = None) -> CDLL:
    resolved = _locate_library(path)
    try:
        lib = CDLL(resolved)
    except OSError as exc:
        raise OSError(
            f"failed to load librjss-ffi from {resolved!r}: {exc}"
        ) from exc
    _declare(lib)
    return lib


def _declare(lib: CDLL) -> None:
    """Attach restype and argtypes to every exported function."""

    # version / error
    lib.jss_version.restype = c_void_p
    lib.jss_version.argtypes = []

    lib.jss_last_error.restype = c_void_p
    lib.jss_last_error.argtypes = []

    # lifecycle
    lib.jss_client_new.restype = c_void_p
    lib.jss_client_new.argtypes = [POINTER(JssClientConfig)]

    lib.jss_client_free.restype = None
    lib.jss_client_free.argtypes = [c_void_p]

    lib.jss_client_trace_id.restype = c_int32
    lib.jss_client_trace_id.argtypes = [c_void_p, POINTER(c_void_p)]

    # auth lifecycle
    lib.jss_client_is_authenticated.restype = c_int32
    lib.jss_client_is_authenticated.argtypes = [c_void_p]

    lib.jss_client_authenticate.restype = c_int32
    lib.jss_client_authenticate.argtypes = [c_void_p]

    lib.jss_client_logout.restype = c_int32
    lib.jss_client_logout.argtypes = [c_void_p]

    lib.jss_client_ensure_session.restype = c_int32
    lib.jss_client_ensure_session.argtypes = [c_void_p]

    # http verbs
    lib.jss_client_get.restype = c_int32
    lib.jss_client_get.argtypes = [c_void_p, c_char_p, POINTER(c_void_p)]

    lib.jss_client_delete.restype = c_int32
    lib.jss_client_delete.argtypes = [c_void_p, c_char_p, POINTER(c_void_p)]

    lib.jss_client_post.restype = c_int32
    lib.jss_client_post.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_put.restype = c_int32
    lib.jss_client_put.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_post_form.restype = c_int32
    lib.jss_client_post_form.argtypes = [
        c_void_p,
        c_char_p,
        POINTER(c_char_p),
        POINTER(c_char_p),
        c_size_t,
        POINTER(c_void_p),
    ]

    lib.jss_client_call_method.restype = c_int32
    lib.jss_client_call_method.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    # documents
    lib.jss_client_get_doc.restype = c_int32
    lib.jss_client_get_doc.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_create_doc.restype = c_int32
    lib.jss_client_create_doc.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_update_doc.restype = c_int32
    lib.jss_client_update_doc.argtypes = [
        c_void_p, c_char_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_delete_doc.restype = c_int32
    lib.jss_client_delete_doc.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    # files
    lib.jss_client_upload_file.restype = c_int32
    lib.jss_client_upload_file.argtypes = [
        c_void_p,
        c_char_p,
        POINTER(c_uint8),
        c_size_t,
        c_char_p,
        c_char_p,
        c_char_p,
        POINTER(c_void_p),
    ]

    lib.jss_client_download_file.restype = c_int32
    lib.jss_client_download_file.argtypes = [
        c_void_p,
        c_char_p,
        POINTER(c_void_p),
        POINTER(c_size_t),
    ]

    lib.jss_client_download_pdf_kartu_piutang.restype = c_int32
    lib.jss_client_download_pdf_kartu_piutang.argtypes = [
        c_void_p,
        c_char_p,
        c_char_p,
        c_char_p,
        c_int32,
        POINTER(c_void_p),
        POINTER(c_size_t),
    ]

    # reports and search
    lib.jss_client_run_report.restype = c_int32
    lib.jss_client_run_report.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_global_search.restype = c_int32
    lib.jss_client_global_search.argtypes = [
        c_void_p, c_char_p, c_uint32, c_char_p, POINTER(c_void_p)
    ]

    # boot info
    lib.jss_client_boot_sitename.restype = c_int32
    lib.jss_client_boot_sitename.argtypes = [c_void_p, POINTER(c_void_p)]

    lib.jss_client_boot_user_name.restype = c_int32
    lib.jss_client_boot_user_name.argtypes = [c_void_p, POINTER(c_void_p)]

    lib.jss_client_boot_user_full_name.restype = c_int32
    lib.jss_client_boot_user_full_name.argtypes = [c_void_p, POINTER(c_void_p)]

    lib.jss_client_boot_user_roles.restype = c_int32
    lib.jss_client_boot_user_roles.argtypes = [c_void_p, POINTER(c_void_p)]

    lib.jss_client_accessible_doctypes.restype = c_int32
    lib.jss_client_accessible_doctypes.argtypes = [c_void_p, POINTER(c_void_p)]

    lib.jss_client_is_developer_mode.restype = c_int32
    lib.jss_client_is_developer_mode.argtypes = [c_void_p]

    lib.jss_client_is_read_only.restype = c_int32
    lib.jss_client_is_read_only.argtypes = [c_void_p]

    # permissions
    lib.jss_client_can_read.restype = c_int32
    lib.jss_client_can_read.argtypes = [c_void_p, c_char_p]

    lib.jss_client_can_write.restype = c_int32
    lib.jss_client_can_write.argtypes = [c_void_p, c_char_p]

    lib.jss_client_can_create.restype = c_int32
    lib.jss_client_can_create.argtypes = [c_void_p, c_char_p]

    lib.jss_client_can_submit.restype = c_int32
    lib.jss_client_can_submit.argtypes = [c_void_p, c_char_p]

    lib.jss_client_can_delete.restype = c_int32
    lib.jss_client_can_delete.argtypes = [c_void_p, c_char_p]

    # memory
    lib.jss_string_free.restype = None
    lib.jss_string_free.argtypes = [c_void_p]

    lib.jss_bytes_free.restype = None
    lib.jss_bytes_free.argtypes = [c_void_p, c_size_t]


lib = _load()


# ── exception ────────────────────────────────────────────────────────

class JssError(Exception):
    """Error raised by any librjss-ffi call.

    Attributes:
        code:    int32 error code (negative JSS_ERR_*)
        message: detail string from jss_last_error()
    """

    def __init__(self, code: int, message: Optional[str] = None) -> None:
        self.code = code
        self.message = message or _ERROR_NAMES.get(code, f"error {code}")
        name = _ERROR_NAMES.get(code, str(code))
        super().__init__(f"[{name}] {self.message}")

    @property
    def name(self) -> str:
        return _ERROR_NAMES.get(self.code, f"UNKNOWN({self.code})")


# ── module-level helpers ─────────────────────────────────────────────

def version() -> str:
    """Return the native library version string."""
    raw = lib.jss_version()
    if not raw:
        return ""
    return ctypes.string_at(raw).decode("utf-8")


def last_error() -> Optional[str]:
    """Return the last error message for the current thread, or None.

    This uses the module-level library handle. When a client was created
    with an explicit lib_path, prefer RjssClient.last_error() which uses
    the same handle the client was built with.
    """
    raw = lib.jss_last_error()
    if not raw:
        return None
    return ctypes.string_at(raw).decode("utf-8")


def _read_cstring(ptr: int) -> Optional[str]:
    if not ptr:
        return None
    return ctypes.string_at(ptr).decode("utf-8")


def _encode(value: Optional[str], field: str) -> Optional[bytes]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field} must be str, got {type(value).__name__}")
    return value.encode("utf-8")


def _encode_required(value: str, field: str) -> bytes:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be str, got {type(value).__name__}")
    if not value:
        raise ValueError(f"{field} must not be empty")
    return value.encode("utf-8")


def _json_payload(value: Union[str, dict, list, None], field: str) -> bytes:
    if value is None:
        return b"{}"
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, (dict, list)):
        return _json.dumps(value).encode("utf-8")
    raise TypeError(
        f"{field} must be str, dict, list, or None, "
        f"got {type(value).__name__}"
    )


# ── client ───────────────────────────────────────────────────────────

class RjssClient:
    """Client for a Frappe / ERPNext backend, backed by librjss-ffi.

    Example (session auth):

        with RjssClient(
            "https://erp.example.com",
            email="user@example.com",
            password="hunter2",
        ) as c:
            c.authenticate()
            rows = c.get_json("/api/resource/ToDo?limit_page_length=5")

    Example (token auth):

        with RjssClient(
            "https://erp.example.com",
            api_key="abcd1234",
            api_secret="efgh5678",
        ) as c:
            c.authenticate()
            doc = c.get_doc_json("Customer", "CUST-0001")

    A single handle is not safe to use from multiple threads at the same
    time. Create one client per thread, or serialise access externally.
    """

    def __init__(
        self,
        base_url: str,
        *,
        email: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        expected_sitename: Optional[str] = None,
        timeout_secs: Optional[int] = None,
        max_retries: Optional[int] = None,
        insecure_ssl: bool = False,
        readonly_guard: bool = True,
        lib_path: Optional[str] = None,
    ) -> None:
        self._lib = _load(lib_path) if lib_path else lib
        self._h: Optional[int] = None
        self._closed = False
        self._cfg: Optional[JssClientConfig] = None

        if api_key is not None:
            if api_secret is None:
                raise ValueError("api_key requires api_secret")
            auth_kind = b"token"
            principal = _encode_required(api_key, "api_key")
            secret = _encode_required(api_secret, "api_secret")
        elif email is not None:
            if password is None:
                raise ValueError("email requires password")
            auth_kind = b"session"
            principal = _encode_required(email, "email")
            secret = _encode_required(password, "password")
        else:
            raise ValueError(
                "provide email/password or api_key/api_secret"
            )

        if timeout_secs is not None and timeout_secs < 0:
            raise ValueError("timeout_secs must be >= 0")
        if max_retries is not None and max_retries < 0:
            raise ValueError("max_retries must be >= 0")

        cfg = JssClientConfig()
        cfg.base_url = _encode_required(base_url, "base_url")
        cfg.auth_kind = auth_kind
        cfg.principal = principal
        cfg.secret = secret
        cfg.expected_sitename = _encode(expected_sitename, "expected_sitename")
        cfg.timeout_secs = timeout_secs or 0
        cfg.max_retries = max_retries or 0

        flags = 0
        if insecure_ssl:
            flags |= JSS_FLAG_INSECURE_SSL
        if not readonly_guard:
            flags |= JSS_FLAG_NO_READONLY_GUARD
        cfg.flags = flags
        cfg._reserved = 0
        cfg._reserved2 = 0

        # keep cfg alive so ctypes does not free the bytes we assigned
        self._cfg = cfg

        handle = self._lib.jss_client_new(byref(cfg))
        if not handle:
            raise JssError(
                JSS_ERR_CONFIG,
                self._last_error() or "jss_client_new failed",
            )
        self._h = handle

    # lifecycle

    def close(self) -> None:
        if self._closed:
            return
        if self._h:
            self._lib.jss_client_free(self._h)
            self._h = None
        self._closed = True

    def __enter__(self) -> "RjssClient":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def __repr__(self) -> str:
        state = "closed" if self._closed else "open"
        return f"<RjssClient {state} trace_id={self.trace_id!r}>"

    # internal

    def _handle(self) -> int:
        if self._closed or not self._h:
            raise JssError(JSS_ERR_NULL_POINTER, "client is closed")
        return self._h

    def _last_error(self) -> Optional[str]:
        raw = self._lib.jss_last_error()
        return _read_cstring(raw)

    def _check(self, rc: int) -> None:
        if rc == JSS_OK:
            return
        raise JssError(rc, self._last_error())

    def _take_string(self, ptr: c_void_p) -> str:
        try:
            value = _read_cstring(ptr.value)
            return value if value is not None else ""
        finally:
            if ptr.value:
                self._lib.jss_string_free(ptr)

    def _take_bytes(self, ptr: c_void_p, length: c_size_t) -> bytes:
        if not ptr.value:
            return b""
        n = int(length.value)
        try:
            if n == 0:
                return b""
            return ctypes.string_at(ptr.value, n)
        finally:
            self._lib.jss_bytes_free(ptr, n)

    # info

    @property
    def trace_id(self) -> str:
        if self._closed:
            return ""
        out = c_void_p()
        rc = self._lib.jss_client_trace_id(self._h, byref(out))
        self._check(rc)
        return self._take_string(out)

    def is_authenticated(self) -> bool:
        rc = self._lib.jss_client_is_authenticated(self._handle())
        if rc < 0:
            self._check(rc)
        return rc == 1

    # auth lifecycle

    def authenticate(self) -> None:
        self._check(self._lib.jss_client_authenticate(self._handle()))

    def logout(self) -> None:
        self._check(self._lib.jss_client_logout(self._handle()))

    def ensure_session(self) -> None:
        self._check(self._lib.jss_client_ensure_session(self._handle()))

    # http verbs

    def get(self, path: str) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_get(
            self._handle(), _encode_required(path, "path"), byref(out)
        )
        self._check(rc)
        return self._take_string(out)

    def delete(self, path: str) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_delete(
            self._handle(), _encode_required(path, "path"), byref(out)
        )
        self._check(rc)
        return self._take_string(out)

    def post(
        self,
        path: str,
        body: Union[str, dict, list, None] = None,
    ) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_post(
            self._handle(),
            _encode_required(path, "path"),
            _json_payload(body, "body"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def put(
        self,
        path: str,
        body: Union[str, dict, list, None] = None,
    ) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_put(
            self._handle(),
            _encode_required(path, "path"),
            _json_payload(body, "body"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def post_form(
        self,
        path: str,
        pairs: Union[Sequence[tuple[str, str]], dict[str, str]],
    ) -> str:
        if isinstance(pairs, dict):
            items = list(pairs.items())
        else:
            items = list(pairs)

        for k, v in items:
            if not isinstance(k, str) or not isinstance(v, str):
                raise TypeError("form keys and values must be str")

        n = len(items)
        keys_arr = (c_char_p * n)(*[k.encode("utf-8") for k, _ in items])
        vals_arr = (c_char_p * n)(*[v.encode("utf-8") for _, v in items])

        out = c_void_p()
        rc = self._lib.jss_client_post_form(
            self._handle(),
            _encode_required(path, "path"),
            keys_arr,
            vals_arr,
            n,
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def call_method(
        self,
        method: str,
        args: Union[dict[str, Any], str, None] = None,
    ) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_call_method(
            self._handle(),
            _encode_required(method, "method"),
            _json_payload(args, "args"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    # documents

    def get_doc(self, doctype: str, name: str) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_get_doc(
            self._handle(),
            _encode_required(doctype, "doctype"),
            _encode_required(name, "name"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def create_doc(
        self,
        doctype: str,
        data: Union[dict[str, Any], str],
    ) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_create_doc(
            self._handle(),
            _encode_required(doctype, "doctype"),
            _json_payload(data, "data"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def update_doc(
        self,
        doctype: str,
        name: str,
        data: Union[dict[str, Any], str],
    ) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_update_doc(
            self._handle(),
            _encode_required(doctype, "doctype"),
            _encode_required(name, "name"),
            _json_payload(data, "data"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def delete_doc(self, doctype: str, name: str) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_delete_doc(
            self._handle(),
            _encode_required(doctype, "doctype"),
            _encode_required(name, "name"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    # files

    def upload_file(
        self,
        file_name: str,
        content: bytes,
        doctype: str = "",
        docname: str = "",
        fieldname: str = "",
    ) -> str:
        if not isinstance(content, (bytes, bytearray)):
            raise TypeError("content must be bytes")
        buf = bytes(content)
        cbuf = ctypes.create_string_buffer(buf, len(buf))
        ptr = ctypes.cast(cbuf, POINTER(c_uint8))

        out = c_void_p()
        rc = self._lib.jss_client_upload_file(
            self._handle(),
            _encode_required(file_name, "file_name"),
            ptr,
            len(buf),
            _encode(doctype, "doctype"),
            _encode(docname, "docname"),
            _encode(fieldname, "fieldname"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def download_file(self, file_url: str) -> bytes:
        out_data = c_void_p()
        out_len = c_size_t()
        rc = self._lib.jss_client_download_file(
            self._handle(),
            _encode_required(file_url, "file_url"),
            byref(out_data),
            byref(out_len),
        )
        self._check(rc)
        return self._take_bytes(out_data, out_len)

    def download_pdf_kartu_piutang(
        self,
        doctype: str,
        name: str,
        format: str,
        no_letterhead: bool = False,
    ) -> bytes:
        out_data = c_void_p()
        out_len = c_size_t()
        rc = self._lib.jss_client_download_pdf_kartu_piutang(
            self._handle(),
            _encode_required(doctype, "doctype"),
            _encode_required(name, "name"),
            _encode_required(format, "format"),
            1 if no_letterhead else 0,
            byref(out_data),
            byref(out_len),
        )
        self._check(rc)
        return self._take_bytes(out_data, out_len)

    # reports and search

    def run_report(
        self,
        report_name: str,
        filters: Union[dict[str, Any], str, None] = None,
    ) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_run_report(
            self._handle(),
            _encode_required(report_name, "report_name"),
            _json_payload(filters, "filters"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    def global_search(
        self,
        query: str,
        limit: int = 20,
        doctype: Optional[str] = None,
    ) -> str:
        if limit < 0:
            raise ValueError("limit must be >= 0")
        out = c_void_p()
        rc = self._lib.jss_client_global_search(
            self._handle(),
            _encode_required(query, "query"),
            limit,
            _encode(doctype, "doctype"),
            byref(out),
        )
        self._check(rc)
        return self._take_string(out)

    # boot info

    def boot_sitename(self) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_boot_sitename(self._handle(), byref(out))
        self._check(rc)
        return self._take_string(out)

    def boot_user_name(self) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_boot_user_name(self._handle(), byref(out))
        self._check(rc)
        return self._take_string(out)

    def boot_user_full_name(self) -> str:
        out = c_void_p()
        rc = self._lib.jss_client_boot_user_full_name(
            self._handle(), byref(out)
        )
        self._check(rc)
        return self._take_string(out)

    def boot_user_roles(self) -> list[str]:
        out = c_void_p()
        rc = self._lib.jss_client_boot_user_roles(
            self._handle(), byref(out)
        )
        self._check(rc)
        raw = self._take_string(out)
        if not raw:
            return []
        parsed = _json.loads(raw)
        if not isinstance(parsed, list):
            return []
        return parsed

    def accessible_doctypes(self) -> list[str]:
        out = c_void_p()
        rc = self._lib.jss_client_accessible_doctypes(
            self._handle(), byref(out)
        )
        self._check(rc)
        raw = self._take_string(out)
        if not raw:
            return []
        parsed = _json.loads(raw)
        if not isinstance(parsed, list):
            return []
        return parsed

    def is_developer_mode(self) -> bool:
        rc = self._lib.jss_client_is_developer_mode(self._handle())
        if rc < 0:
            self._check(rc)
        return rc == 1

    def is_read_only(self) -> bool:
        rc = self._lib.jss_client_is_read_only(self._handle())
        if rc < 0:
            self._check(rc)
        return rc == 1

    # permissions

    def _bool_call(self, fn_name: str, doctype: str) -> bool:
        rc = getattr(self._lib, fn_name)(
            self._handle(), _encode_required(doctype, "doctype")
        )
        if rc < 0:
            self._check(rc)
        return rc == 1

    def can_read(self, doctype: str) -> bool:
        return self._bool_call("jss_client_can_read", doctype)

    def can_write(self, doctype: str) -> bool:
        return self._bool_call("jss_client_can_write", doctype)

    def can_create(self, doctype: str) -> bool:
        return self._bool_call("jss_client_can_create", doctype)

    def can_submit(self, doctype: str) -> bool:
        return self._bool_call("jss_client_can_submit", doctype)

    def can_delete(self, doctype: str) -> bool:
        return self._bool_call("jss_client_can_delete", doctype)

    # JSON convenience

    def get_json(self, path: str) -> Any:
        return _json.loads(self.get(path))

    def get_doc_json(self, doctype: str, name: str) -> Any:
        return _json.loads(self.get_doc(doctype, name))

    def call_method_json(
        self,
        method: str,
        args: Union[dict[str, Any], str, None] = None,
    ) -> Any:
        return _json.loads(self.call_method(method, args))

    def post_form_json(
        self,
        path: str,
        pairs: Union[Sequence[tuple[str, str]], dict[str, str]],
    ) -> Any:
        return _json.loads(self.post_form(path, pairs))


# ── from_env ─────────────────────────────────────────────────────────

def _env(*names: str) -> Optional[str]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("true", "1", "yes", "y", "on")


def from_env(
    *,
    insecure_ssl: Optional[bool] = None,
    readonly_guard: Optional[bool] = None,
    lib_path: Optional[str] = None,
) -> RjssClient:
    """Build a client from environment variables.

    Variables:

        JSS_BASE_URL or JSS_URL         required
        JSS_TOKEN_KEY                   token mode
        JSS_TOKEN_SECRET                token mode
        JSS_EMAIL or JSS_USR            session mode
        JSS_PASSWORD or JSS_PWD         session mode
        JSS_EXPECTED_SITENAME           optional
        JSS_TIMEOUT_SECS                default 30
        JSS_MAX_RETRIES                 default 3
        JSS_INSECURE_SSL                true/1/yes
        JSS_READONLY_GUARD              false/0/no disables

    Keyword arguments override the environment.
    """

    base_url = _env("JSS_BASE_URL", "JSS_URL")
    if not base_url:
        raise JssError(
            JSS_ERR_CONFIG,
            "JSS_BASE_URL or JSS_URL is required",
        )

    kwargs: dict[str, Any] = {
        "base_url": base_url,
        "expected_sitename": _env("JSS_EXPECTED_SITENAME"),
        "lib_path": lib_path,
    }

    timeout = _env("JSS_TIMEOUT_SECS")
    if timeout:
        try:
            kwargs["timeout_secs"] = int(timeout)
        except ValueError:
            pass

    retries = _env("JSS_MAX_RETRIES")
    if retries:
        try:
            kwargs["max_retries"] = int(retries)
        except ValueError:
            pass

    token_key = _env("JSS_TOKEN_KEY")
    if token_key:
        token_secret = _env("JSS_TOKEN_SECRET")
        if not token_secret:
            raise JssError(
                JSS_ERR_CONFIG,
                "JSS_TOKEN_KEY set but JSS_TOKEN_SECRET missing",
            )
        kwargs["api_key"] = token_key
        kwargs["api_secret"] = token_secret
    else:
        email = _env("JSS_EMAIL", "JSS_USR")
        password = _env("JSS_PASSWORD", "JSS_PWD")
        if not (email and password):
            raise JssError(
                JSS_ERR_CONFIG,
                "set JSS_EMAIL/JSS_PASSWORD or "
                "JSS_TOKEN_KEY/JSS_TOKEN_SECRET",
            )
        kwargs["email"] = email
        kwargs["password"] = password

    if insecure_ssl is None:
        insecure_ssl = _env_bool("JSS_INSECURE_SSL", False)
    kwargs["insecure_ssl"] = insecure_ssl

    if readonly_guard is None:
        raw = os.environ.get("JSS_READONLY_GUARD")
        if raw is None:
            readonly_guard = True
        else:
            readonly_guard = raw.strip().lower() not in (
                "false", "0", "no", "n", "off"
            )
    kwargs["readonly_guard"] = readonly_guard

    return RjssClient(**kwargs)


# ── self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"librjss-ffi version : {version()}")
    print(f"library loaded from : {lib._name}")
    print(f"PANIC error code    : {JSS_ERR_PANIC}")
    print(
        f"flags               : "
        f"INSECURE_SSL={JSS_FLAG_INSECURE_SSL:#x}, "
        f"NO_READONLY_GUARD={JSS_FLAG_NO_READONLY_GUARD:#x}"
    )

    if os.environ.get("JSS_BASE_URL"):
        print()
        print("connecting using environment variables")
        try:
            with from_env() as c:
                c.authenticate()
                print(f"  sitename       : {c.boot_sitename()}")
                print(
                    f"  user           : {c.boot_user_full_name()} "
                    f"<{c.boot_user_name()}>"
                )
                print(f"  roles          : {c.boot_user_roles()}")
                print(f"  developer mode : {c.is_developer_mode()}")
                print(f"  read only      : {c.is_read_only()}")
                print(f"  can_read ToDo  : {c.can_read('ToDo')}")
                print(f"  trace_id       : {c.trace_id}")
        except JssError as exc:
            print(f"  error: {exc}")
    else:
        print()
        print("set JSS_BASE_URL, JSS_EMAIL and JSS_PASSWORD to test a live server")