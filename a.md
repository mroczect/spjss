```
.  # src/spjss/
├── __init__.py
├── __main__.py
├── _native
│   ├── __init__.py
│   ├── librjss.h
│   ├── librjss.py
│   ├── librjss_ffi.lib
├── app.py
├── config.py
├── data
│   ├── about.txt
│   ├── license.txt
│   ├── privacy.txt
│   ├── terms.txt
│   ├── third_party.txt
├── downloader.py
├── keyring_helper.py
├── legal.py
├── pages
│   ├── __init__.py
│   ├── base.py
│   ├── dashboard.py
│   ├── login.py
│   ├── privacy.py
│   ├── review.py
│   ├── run.py
│   ├── settings.py
│   ├── terms.py
│   ├── third_party.py
│   ├── welcome.py
├── presets.py
├── update_check.py
├── worker.py
```
## src/spjss/__init__.py

```python
from ._native import JssError, RjssClient
from ._native import version as lib_version

__version__ = "0.1.0"
__all__ = ["JssError", "RjssClient", "__version__", "lib_version"]
```
## src/spjss/_native/__init__.py

```python
from .librjss import (
    JssClientConfig,
    JssError,
    RjssClient,
    from_env,
    last_error,
    version,
)

__all__ = [
    "JssClientConfig",
    "JssError",
    "RjssClient",
    "from_env",
    "last_error",
    "version",
]
```
## src/spjss/_native/librjss_ffi.lib

```
[Binary file, content omitted]
```
## src/spjss/_native/librjss.h

```c
#ifndef LIBRJSS_FFI_H
#define LIBRJSS_FFI_H

#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#define JSS_OK 0

#define JSS_ERR_CONFIG -1

#define JSS_ERR_VALIDATION -2

#define JSS_ERR_NETWORK -3

#define JSS_ERR_HTTP -4

#define JSS_ERR_API -5

#define JSS_ERR_AUTH -6

#define JSS_ERR_CSRF -7

#define JSS_ERR_PERMISSION -8

#define JSS_ERR_SITENAME_MISMATCH -9

#define JSS_ERR_NOT_AUTHENTICATED -10

#define JSS_ERR_RATE_LIMITED -11

#define JSS_ERR_PARSE -12

#define JSS_ERR_EXPIRED -13

#define JSS_ERR_CANCELLED -14

#define JSS_ERR_FILE_OPERATION -15

#define JSS_ERR_INTERNAL -16

#define JSS_ERR_NULL_POINTER -17

#define JSS_ERR_UTF8 -18

#define JSS_ERR_PANIC -19

#define JSS_FLAG_INSECURE_SSL (1 << 0)

#define JSS_FLAG_NO_READONLY_GUARD (1 << 1)

typedef struct JssClient JssClient;

typedef struct JssClientConfig {
  const char *base_url;
  const char *auth_kind;
  const char *principal;
  const char *secret;
  const char *expected_sitename;
  uint32_t flags;
  uint32_t _reserved;
  uint64_t timeout_secs;
  uint32_t max_retries;
  uint32_t _reserved2;
} JssClientConfig;

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

const char *jss_last_error(void);

const char *jss_version(void);

struct JssClient *jss_client_new(const struct JssClientConfig *cfg);

void jss_client_free(struct JssClient *c);

int32_t jss_client_trace_id(struct JssClient *c, char **out);

int32_t jss_client_is_authenticated(struct JssClient *c);

int32_t jss_client_authenticate(struct JssClient *c);

int32_t jss_client_logout(struct JssClient *c);

int32_t jss_client_ensure_session(struct JssClient *c);

int32_t jss_client_get(struct JssClient *c, const char *path, char **out_body);

int32_t jss_client_delete(struct JssClient *c, const char *path, char **out_body);

int32_t jss_client_post(struct JssClient *c,
                        const char *path,
                        const char *body_json,
                        char **out_body);

int32_t jss_client_put(struct JssClient *c,
                       const char *path,
                       const char *body_json,
                       char **out_body);

int32_t jss_client_post_form(struct JssClient *c,
                             const char *path,
                             const char *const *keys,
                             const char *const *values,
                             uintptr_t n_pairs,
                             char **out_body);

int32_t jss_client_call_method(struct JssClient *c,
                               const char *method,
                               const char *args_json,
                               char **out_body);

int32_t jss_client_get_doc(struct JssClient *c,
                           const char *doctype,
                           const char *name,
                           char **out_body);

int32_t jss_client_create_doc(struct JssClient *c,
                              const char *doctype,
                              const char *data_json,
                              char **out_body);

int32_t jss_client_update_doc(struct JssClient *c,
                              const char *doctype,
                              const char *name,
                              const char *data_json,
                              char **out_body);

int32_t jss_client_delete_doc(struct JssClient *c,
                              const char *doctype,
                              const char *name,
                              char **out_body);

int32_t jss_client_upload_file(struct JssClient *c,
                               const char *file_name,
                               const uint8_t *content,
                               uintptr_t content_len,
                               const char *doctype,
                               const char *docname,
                               const char *fieldname,
                               char **out_body);

int32_t jss_client_download_file(struct JssClient *c,
                                 const char *file_url,
                                 uint8_t **out_data,
                                 uintptr_t *out_len);

int32_t jss_client_download_pdf_kartu_piutang(struct JssClient *c,
                                              const char *doctype,
                                              const char *name,
                                              const char *format,
                                              int32_t no_letterhead,
                                              uint8_t **out_data,
                                              uintptr_t *out_len);

int32_t jss_client_run_report(struct JssClient *c,
                              const char *report_name,
                              const char *filters_json,
                              char **out_body);

int32_t jss_client_global_search(struct JssClient *c,
                                 const char *query,
                                 uint32_t limit,
                                 const char *doctype,
                                 char **out_body);

int32_t jss_client_boot_sitename(struct JssClient *c, char **out);

int32_t jss_client_boot_user_name(struct JssClient *c, char **out);

int32_t jss_client_boot_user_full_name(struct JssClient *c, char **out);

int32_t jss_client_boot_user_roles(struct JssClient *c, char **out_json);

int32_t jss_client_accessible_doctypes(struct JssClient *c, char **out_json);

int32_t jss_client_is_developer_mode(struct JssClient *c);

int32_t jss_client_is_read_only(struct JssClient *c);

int32_t jss_client_can_read(struct JssClient *c, const char *doctype);

int32_t jss_client_can_write(struct JssClient *c, const char *doctype);

int32_t jss_client_can_create(struct JssClient *c, const char *doctype);

int32_t jss_client_can_submit(struct JssClient *c, const char *doctype);

int32_t jss_client_can_delete(struct JssClient *c, const char *doctype);

void jss_string_free(char *s);

void jss_bytes_free(uint8_t *p, uintptr_t len);

#ifdef __cplusplus
}  
#endif  // __cplusplus

#endif  /* LIBRJSS_FFI_H */
```
## src/spjss/_native/librjss.py

```python

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

    candidates.append(os.path.join(here, name))

    triple = _target_triple()
    if triple:
        candidates.append(os.path.join(here, triple, name))
        candidates.append(
            os.path.join(parent, "target", triple, "release", name)
        )

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

    lib.jss_version.restype = c_void_p
    lib.jss_version.argtypes = []

    lib.jss_last_error.restype = c_void_p
    lib.jss_last_error.argtypes = []

    lib.jss_client_new.restype = c_void_p
    lib.jss_client_new.argtypes = [POINTER(JssClientConfig)]

    lib.jss_client_free.restype = None
    lib.jss_client_free.argtypes = [c_void_p]

    lib.jss_client_trace_id.restype = c_int32
    lib.jss_client_trace_id.argtypes = [c_void_p, POINTER(c_void_p)]

    lib.jss_client_is_authenticated.restype = c_int32
    lib.jss_client_is_authenticated.argtypes = [c_void_p]

    lib.jss_client_authenticate.restype = c_int32
    lib.jss_client_authenticate.argtypes = [c_void_p]

    lib.jss_client_logout.restype = c_int32
    lib.jss_client_logout.argtypes = [c_void_p]

    lib.jss_client_ensure_session.restype = c_int32
    lib.jss_client_ensure_session.argtypes = [c_void_p]

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

    lib.jss_client_run_report.restype = c_int32
    lib.jss_client_run_report.argtypes = [
        c_void_p, c_char_p, c_char_p, POINTER(c_void_p)
    ]

    lib.jss_client_global_search.restype = c_int32
    lib.jss_client_global_search.argtypes = [
        c_void_p, c_char_p, c_uint32, c_char_p, POINTER(c_void_p)
    ]

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

    lib.jss_string_free.restype = None
    lib.jss_string_free.argtypes = [c_void_p]

    lib.jss_bytes_free.restype = None
    lib.jss_bytes_free.argtypes = [c_void_p, c_size_t]


lib = _load()



class JssError(Exception):

    def __init__(self, code: int, message: Optional[str] = None) -> None:
        self.code = code
        self.message = message or _ERROR_NAMES.get(code, f"error {code}")
        name = _ERROR_NAMES.get(code, str(code))
        super().__init__(f"[{name}] {self.message}")

    @property
    def name(self) -> str:
        return _ERROR_NAMES.get(self.code, f"UNKNOWN({self.code})")



def version() -> str:
    raw = lib.jss_version()
    if not raw:
        return ""
    return ctypes.string_at(raw).decode("utf-8")


def last_error() -> Optional[str]:
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

        self._cfg = cfg

        handle = self._lib.jss_client_new(byref(cfg))
        if not handle:
            raise JssError(
                JSS_ERR_CONFIG,
                self._last_error() or "jss_client_new failed",
            )
        self._h = handle


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


    def authenticate(self) -> None:
        self._check(self._lib.jss_client_authenticate(self._handle()))

    def logout(self) -> None:
        self._check(self._lib.jss_client_logout(self._handle()))

    def ensure_session(self) -> None:
        self._check(self._lib.jss_client_ensure_session(self._handle()))


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
```
## src/spjss/__main__.py

```python
import sys


def main() -> int:
    from .app import App

    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
## src/spjss/worker.py

```python
import queue
import threading
from collections.abc import Callable
from typing import Any

_stop = threading.Event()


def reset_stop() -> None:
    _stop.clear()


def request_stop() -> None:
    _stop.set()


def should_stop() -> bool:
    return _stop.is_set()


def run(
    fn: Callable[..., Any], out: "queue.Queue", *args, **kwargs
) -> threading.Thread:
    def body() -> None:
        try:
            out.put(("ok", fn(*args, **kwargs)))
        except BaseException as e:
            out.put(("err", e))

    t = threading.Thread(target=body, daemon=True)
    t.start()
    return t
```
## src/spjss/data/about.txt

```text
spjss
=====

A desktop application for downloading PDF files from a Frappe or
ERPNext server in batch, given a range of document identifiers.


Purpose
-------

spjss exists because Frappe's web interface does not offer a way
to download many print-format PDFs at once. Doing it by hand for
dozens or hundreds of documents is impractical. This application
automates that process: you specify a range of document names, and
it requests each PDF from the server and writes it to a local
folder.


Scope
-----

spjss is a client. It does not read, store, or generate PDFs
itself. All PDF generation happens on the server, using the print
format you specify. spjss only requests the file and writes the
response to disk.

spjss does not modify any data on the server. It calls only the
read-only endpoint frappe.utils.print_format.download_pdf, which
returns a PDF for a single document. No writes, no submissions,
no cancellations, no deletions.


Version
-------

Version     : 0.1.0
Author      : mroczect <mroczect@proton.me>
Repository  : https://github.com/mroczect/librjss
License     : MIT
Language    : Python 3.10+ and tkinter


Dependencies
------------

  Python 3.10 or newer              https://python.org
  tkinter                           bundled with CPython
  ctypes                            bundled with CPython
  librjss-ffi 2.3.0 (Rust, MIT)     https://github.com/mroczect/librjss

tkinter and ctypes ship with CPython. Only librjss-ffi needs to be
obtained separately, either by building from source or from a
published release binary.


How to use
----------

  1. Read this page.
  2. Read the privacy notice.
  3. Enter server URL, email, and password.
  4. Enter DocType, start identifier, end identifier, and the
     folder where PDFs should be saved.
  5. Review the summary.
  6. Run.

Navigation is at the bottom of every page. Back moves to the
previous step without losing data you have already entered. Next
moves forward. On the last page, Run starts the download and
Finish closes the application.


Notes
-----

No credentials are stored by this application. See privacy.txt for
details on what is written to disk and what is not.

No data is sent to any third party. The only network destination
is the server URL you enter.


Warranty
--------

spjss is provided as is, without warranty of any kind. See
license.txt for the full MIT license text and terms.txt for the
additional disclaimer and terms of use.
```
## src/spjss/data/privacy.txt

```text
Privacy notice
==============

This notice describes what spjss records on your computer, where
it is kept, how long it is kept, and how to remove it. It is
written to be read by the person running the application.


What is stored
--------------

When you complete the download step for the first time, spjss
writes a configuration file to disk. That file contains the
following fields:

  base_url          Server URL, e.g. https://erp.example.com
  email             The email address you entered
  insecure_ssl      Whether invalid TLS certificates are allowed
  doctype           Frappe DocType, e.g. "Surat Peringatan KSP"
  print_format      Print format name, or empty for the default
  output_dir        Absolute path to the folder where PDFs go
  delay_ms          Delay in milliseconds between HTTP requests
  no_letterhead     Whether the PDF was requested without letterhead
  overwrite         Whether existing files were overwritten

The configuration file is written only after a batch download
completes. If you close the application before finishing, nothing
is written.


What is not stored
------------------

Your password is never written to disk. It is held in memory only
for the duration of a single run, and is discarded when you close
the application.

Session cookies issued by the server are not written to disk. A
new session is established every time you start the application.

No log file is created. The activity log you see on the Run page
exists only in memory and disappears when the window closes.

Nothing is transmitted to any server other than the one you
entered in the Credentials page. There is no telemetry, no crash
reporting, no update check.


Where the configuration file lives
----------------------------------

  Linux    $XDG_CONFIG_HOME/spjss/config.json
           (falls back to ~/.config/spjss/config.json)

  macOS    ~/.config/spjss/config.json

  Windows  %APPDATA%\spjss\config.json

The file is plain JSON and can be inspected with any text editor.


How to delete the configuration
-------------------------------

  Linux, macOS

    rm ~/.config/spjss/config.json

  Windows (PowerShell)

    Remove-Item "$env:APPDATA\spjss\config.json"

Deleting the file has no effect on the server. Your account,
documents, and session history are untouched.


Session lifetime
----------------

When a batch completes, spjss sends a logout request to the server
to invalidate the session. If you close the window before a batch
completes, the session remains open on the server until it expires
by Frappe's own session expiry setting. The default is 24 hours,
configurable in System Settings on the server side.


Network activity
----------------

During a run, spjss sends the following requests to the server
you specified:

  POST /api/method/login
        Called once at the start of each run. Sends your email and
        password. The server responds with a session cookie.

  GET  /app
        Called once after login. Used to obtain the CSRF token and
        the boot payload. Frappe requires this for session auth.

  GET  /api/method/frappe.auth.get_logged_user
        Called on re-login if the session expires.

  GET  /api/method/frappe.utils.print_format.download_pdf
        Called once per document in the range. Returns the PDF.

  POST /api/method/logout
        Called at the end of the run.

No other requests are made. No third-party hosts are contacted.


Basis for processing
--------------------

All data handled by spjss is either entered directly by you or
retrieved from the server you specified, using credentials you
supplied. The application does not process any data beyond what
is needed to perform the download you requested.


Contact
-------

Questions about this notice can be sent to:

  mroczect <mroczect@proton.me>

For questions about data held on the server itself, contact your
Frappe or ERPNext administrator. spjss has no visibility into
server-side data.
```
## src/spjss/data/license.txt

```text
MIT License
===========

Copyright (c) 2026 mroczect <mroczect@proton.me>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
```
## src/spjss/data/terms.txt

```text
Terms of use
============

By running spjss, you agree to the following terms. If you do not
agree, do not run the application.


1. Authorised use only

spjss authenticates to a server using credentials you supply. You
must be authorised to access that server and to retrieve the
documents you request. If your account lacks permission for a
document, the server will reject the request. spjss does not
attempt to bypass server-side permission checks and does not
include any feature that would do so.

Do not use spjss to access data you are not entitled to see.


2. Server load

Every document in a range produces at least one HTTP request.
Requesting a range that covers many thousands of documents places
load on the server. The delay_ms setting exists to spread requests
out. Do not set it to zero or a very low value on a production
server without first checking with your administrator.

If your administrator asks you to stop, stop.


3. No warranty

spjss is distributed under the MIT license, whose warranty
disclaimer applies. In plain language: the software may contain
defects. It may fail to download some documents. It may write
files to unexpected paths if you enter an incorrect output
folder. It may interpret a server response incorrectly.

You use spjss at your own risk. The author is not responsible for
lost data, missed documents, or any consequence of running the
application.


4. No support obligation

The author is not obligated to provide support, updates, bug
fixes, or responses to questions. Issues and pull requests on the
GitHub repository are welcome but may not be addressed promptly
or at all.


5. Compliance with local rules

Your organisation may have its own rules about which tools may
access production systems, how credentials may be handled, and
where downloaded files may be stored. It is your responsibility
to comply with those rules. spjss does not enforce any of them.


6. Changes

These terms may be revised in future versions. The version of
the terms that applies to you is the one shipped with the version
of spjss you are running.


7. Governing interpretation

Nothing in this document overrides the license in license.txt. In
case of conflict, the license controls.
```
## src/spjss/data/third_party.txt

```text
Third-party notices
===================

spjss includes or depends on the following third-party software.
Each is distributed under its own license. The license text below
is reproduced for reference. Refer to the upstream projects for
the authoritative text.


librjss-ffi 2.3.0
-----------------

Asynchronous Rust client for Frappe and ERPNext backends, with a
C ABI exposed for use from other languages.

  Source   https://github.com/mroczect/librjss
  License  MIT

The MIT license text appears in license.txt.


Python standard library
-----------------------

spjss uses the following modules from the Python standard library,
which is distributed under the Python Software Foundation License
Version 2. The modules used are:

  tkinter         GUI toolkit
  ctypes          Foreign function interface
  json            Configuration file format
  pathlib         Filesystem paths
  threading       Background worker
  queue           Thread-safe message passing
  os, sys         Platform utilities

  Source   https://docs.python.org/3/license.html
  License  PSF-2.0


Tcl/Tk
------

tkinter binds to Tcl/Tk. Tcl/Tk is distributed under a BSD-style
license.

  Source   https://www.tcl.tk/software/tcltk/license.html
  License  BSD-style
```
## src/spjss/legal.py

```python
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load(name: str) -> str:
    p = DATA_DIR / name
    if not p.is_file():
        return f"(berkas {name} tidak ditemukan)"
    return p.read_text("utf-8")
```
## src/spjss/pages/welcome.py

```python
from tkinter import ttk

from .. import legal
from .base import Page


class WelcomePage(Page):
    title = "Welcome"
    step_label = "Step 1 of 4"
    next_label = "Next >"
    show_back = False

    def build(self) -> None:
        ttk.Label(
            self,
            text="spjss",
            font=("TkDefaultFont", 20, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self,
            text="Batch PDF downloader for Frappe / ERPNext",
        ).pack(anchor="w", pady=(0, 12))

        self.readonly_text(self, legal.load("about.txt"), height=22)

    def on_next(self):
        from .privacy import PrivacyPage

        return PrivacyPage
```
## src/spjss/pages/privacy.py

```python
from .. import legal
from .base import Page


class PrivacyPage(Page):
    title = "Privacy"
    step_label = "Step 2 of 4"

    def build(self) -> None:
        self.readonly_text(self, legal.load("privacy.txt"), height=26)

    def on_next(self):
        from .terms import TermsPage

        return TermsPage

    def on_back(self):
        from .welcome import WelcomePage

        return WelcomePage
```
## src/spjss/pages/settings.py

```python
from pathlib import Path
from tkinter import filedialog, ttk

from .base import Page


class SettingsPage(Page):
    title = "Pengaturan unduhan"
    step_label = "Langkah 6 dari 7"

    def build(self) -> None:
        form = ttk.Frame(self)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="DocType").grid(row=0, column=0, sticky="w", pady=6)
        self.e_doctype = ttk.Entry(form)
        self.e_doctype.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(form, text="Print Format").grid(row=1, column=0, sticky="w", pady=6)
        self.e_format = ttk.Entry(form)
        self.e_format.grid(row=1, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(form, text="kosongkan untuk pakai format default").grid(
            row=1, column=2, sticky="w", padx=8
        )

        ttk.Label(form, text="Start ID").grid(row=2, column=0, sticky="w", pady=6)
        self.e_start = ttk.Entry(form)
        self.e_start.grid(row=2, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(form, text="contoh: JD4521").grid(row=2, column=2, sticky="w", padx=8)

        ttk.Label(form, text="End ID").grid(row=3, column=0, sticky="w", pady=6)
        self.e_end = ttk.Entry(form)
        self.e_end.grid(row=3, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(form, text="contoh: JD4546").grid(row=3, column=2, sticky="w", padx=8)

        ttk.Label(form, text="Folder output").grid(row=4, column=0, sticky="w", pady=6)
        self.e_out = ttk.Entry(form)
        self.e_out.grid(row=4, column=1, sticky="ew", padx=8, pady=6)
        ttk.Button(form, text="Pilih...", command=self._pick_dir).grid(
            row=4, column=2, padx=8
        )

        ttk.Label(form, text="Delay antar request (ms)").grid(
            row=5, column=0, sticky="w", pady=6
        )
        self.e_delay = ttk.Entry(form, width=10)
        self.e_delay.grid(row=5, column=1, sticky="w", padx=8, pady=6)

        self.v_no_letterhead = ttk.Checkbutton(form, text="Tanpa letterhead")
        self.v_no_letterhead.grid(row=6, column=1, sticky="w", padx=8, pady=6)

        self.v_overwrite = ttk.Checkbutton(form, text="Timpa berkas yang sudah ada")
        self.v_overwrite.grid(row=7, column=1, sticky="w", padx=8, pady=6)

        self.lbl_error = ttk.Label(self, text="", foreground="#b00020", wraplength=640)
        self.lbl_error.pack(anchor="w", pady=(12, 0))

    def _pick_dir(self) -> None:
        cur = self.e_out.get().strip() or str(Path.home())
        d = filedialog.askdirectory(initialdir=cur)
        if d:
            self.e_out.delete(0, "end")
            self.e_out.insert(0, d)

    def on_enter(self) -> None:
        s = self.app.state
        pairs = [
            (self.e_doctype, "doctype"),
            (self.e_format, "print_format"),
            (self.e_out, "output_dir"),
            (self.e_delay, "delay_ms"),
        ]
        for widget, key in pairs:
            if widget.get():
                continue
            v = s.get(key)
            if v:
                widget.insert(0, str(v))
        if not self.e_delay.get():
            self.e_delay.insert(0, "300")
        if s.get("no_letterhead"):
            self.v_no_letterhead.state(["selected"])
        if s.get("overwrite"):
            self.v_overwrite.state(["selected"])

    def on_next(self):
        doctype = self.e_doctype.get().strip()
        fmt = self.e_format.get().strip()
        start = self.e_start.get().strip().upper()
        end = self.e_end.get().strip().upper()
        out = self.e_out.get().strip()
        delay_raw = self.e_delay.get().strip() or "300"

        if not doctype:
            self.lbl_error.config(text="DocType wajib diisi.")
            return None
        if not start or not end:
            self.lbl_error.config(text="Start dan End ID wajib diisi.")
            return None
        if not out:
            self.lbl_error.config(text="Folder output wajib dipilih.")
            return None

        try:
            delay = int(delay_raw)
        except ValueError:
            self.lbl_error.config(text="Delay harus angka.")
            return None
        if delay < 0:
            self.lbl_error.config(text="Delay tidak boleh negatif.")
            return None

        out_path = Path(out).expanduser()
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_path

        self.app.state.update(
            doctype=doctype,
            print_format=fmt,
            start=start,
            end=end,
            output_dir=str(out_path),
            delay_ms=delay,
            no_letterhead=bool(self.v_no_letterhead.instate(["selected"])),
            overwrite=bool(self.v_overwrite.instate(["selected"])),
        )
        self.lbl_error.config(text="")
        from .review import ReviewPage

        return ReviewPage

    def on_back(self):
        from .login import LoginPage

        return LoginPage
```
## src/spjss/pages/review.py

```python
from tkinter import ttk

from ..downloader import expand_range
from .base import Page


class ReviewPage(Page):
    title = "Tinjau"
    step_label = "Langkah 7 dari 7"
    next_label = "Jalankan"

    def build(self) -> None:
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
        self.lbl_error = ttk.Label(self, text="", foreground="#b00020", wraplength=640)
        self.lbl_error.pack(anchor="w", pady=(12, 0))

    def on_enter(self) -> None:
        for w in self.body.winfo_children():
            w.destroy()

        s = self.app.state
        try:
            names = expand_range(s["start"], s["end"])
        except ValueError as e:
            self.lbl_error.config(text=f"Rentang tidak valid: {e}")
            names = []

        rows = [
            ("Base URL", s.get("base_url", "")),
            ("Email", s.get("email", "")),
            ("SSL tidak valid", "ya" if s.get("insecure_ssl") else "tidak"),
            ("DocType", s.get("doctype", "")),
            ("Print Format", s.get("print_format") or "(default)"),
            ("Start ID", s.get("start", "")),
            ("End ID", s.get("end", "")),
            ("Jumlah dokumen", str(len(names)) if names else "-"),
            ("Folder output", s.get("output_dir", "")),
            ("Delay (ms)", str(s.get("delay_ms", 300))),
            ("Tanpa letterhead", "ya" if s.get("no_letterhead") else "tidak"),
            ("Timpa berkas", "ya" if s.get("overwrite") else "tidak"),
        ]
        form = ttk.Frame(self.body)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        for i, (label, value) in enumerate(rows):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=4)
            ttk.Label(form, text=value, wraplength=520).grid(
                row=i, column=1, sticky="w", padx=8, pady=4
            )

        if names:
            ttk.Label(
                self.body,
                text=f"Akan mengunduh: {names[0]} ... {names[-1]}",
            ).pack(anchor="w", pady=(16, 0))
            self.lbl_error.config(text="")
        else:
            self.lbl_error.config(
                text="Rentang tidak valid. Tekan Kembali dan perbaiki."
            )

    def on_next(self):
        from .run import RunPage

        try:
            expand_range(self.app.state["start"], self.app.state["end"])
        except ValueError:
            return None
        return RunPage

    def on_back(self):
        from .settings import SettingsPage

        return SettingsPage
```
## src/spjss/pages/__init__.py

```python
from .base import Page
from .dashboard import DashboardPage
from .login import LoginPage
from .privacy import PrivacyPage
from .terms import TermsPage
from .third_party import ThirdPartyPage
from .welcome import WelcomePage

__all__ = [
    "DashboardPage",
    "LoginPage",
    "Page",
    "PrivacyPage",
    "TermsPage",
    "ThirdPartyPage",
    "WelcomePage",
]
```
## src/spjss/pages/terms.py

```python
from .. import legal
from .base import Page


class TermsPage(Page):
    title = "Terms of use"
    step_label = "Step 3 of 4"

    def build(self) -> None:
        self.readonly_text(self, legal.load("terms.txt"), height=26)

    def on_next(self):
        from .third_party import ThirdPartyPage

        return ThirdPartyPage

    def on_back(self):
        from .privacy import PrivacyPage

        return PrivacyPage
```
## src/spjss/pages/third_party.py

```python
from .. import config as cfgmod
from .. import legal
from .base import Page


class ThirdPartyPage(Page):
    title = "Third-party notices"
    step_label = "Step 4 of 4"
    next_label = "I agree, continue >"

    def build(self) -> None:
        self.readonly_text(self, legal.load("third_party.txt"), height=26)

    def on_next(self):
        cfgmod.mark_first_run_complete()
        from .login import LoginPage

        return LoginPage

    def on_back(self):
        from .terms import TermsPage

        return TermsPage
```
## src/spjss/pages/base.py

```python
from tkinter import ttk


class Page(ttk.Frame):

    title = ""
    step_label = ""
    next_label = "Next >"
    back_label = "< Back"
    show_next = True
    show_back = True

    def __init__(self, master, app):
        super().__init__(master, padding=16)
        self.app = app
        self.build()


    def build(self) -> None:
        raise NotImplementedError

    def on_enter(self) -> None:
        pass

    def on_leave(self) -> bool:
        return True

    def on_next(self):
        return None


    def readonly_text(self, parent, content: str, height: int = 20):
        import tkinter as tk

        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True)
        t = tk.Text(
            wrap,
            wrap="word",
            height=height,
            font=("TkDefaultFont", 10),
            borderwidth=1,
            relief="solid",
        )
        t.insert("1.0", content)
        t.config(state="disabled")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        t.pack(side="left", fill="both", expand=True)
        return t
```
## src/spjss/pages/dashboard.py

```python
import json
import os
import platform
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from .. import config as cfgmod
from .. import keyring_helper as keyring
from .. import presets, worker
from .._native import RjssClient
from ..downloader import (
    DEFAULT_FILENAME_TEMPLATE,
    download_range,
    expand_range,
)
from .base import Page


class DashboardPage(Page):
    title = "Download"
    step_label = "Download"
    next_label = "Exit"
    show_back = False
    show_next = True

    def build(self) -> None:
        self._running = False
        self._failed: list[str] = []
        self._last_summary = None
        self._run_started_at = 0.0
        self._client_for_test = None

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 6))

        ttk.Label(bar, text="Preset:").pack(side="left")
        self.cb_preset = ttk.Combobox(bar, width=24, state="readonly")
        self.cb_preset.pack(side="left", padx=6)
        self.cb_preset.bind("<<ComboboxSelected>>", self._on_preset_selected)

        ttk.Button(bar, text="Load", command=self._on_preset_load).pack(
            side="left", padx=2
        )
        ttk.Button(bar, text="Save", command=self._on_preset_save).pack(
            side="left", padx=2
        )
        ttk.Button(bar, text="Delete", command=self._on_preset_delete).pack(
            side="left", padx=2
        )

        form = ttk.LabelFrame(self, text="Settings", padding=10)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="DocType").grid(row=0, column=0, sticky="w", pady=4)
        self.e_doctype = ttk.Entry(form)
        self.e_doctype.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(form, text="Print Format").grid(row=1, column=0, sticky="w", pady=4)
        self.cb_format = ttk.Combobox(form)
        self.cb_format.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        ttk.Button(form, text="Detect", command=self._on_detect_formats).grid(
            row=1, column=2, padx=8
        )

        ttk.Label(form, text="Filename").grid(row=2, column=0, sticky="w", pady=4)
        self.e_filename = ttk.Entry(form)
        self.e_filename.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(
            form,
            text="contoh: Surat Peringatan {name}  |  {customer}",
        ).grid(row=2, column=2, sticky="w")

        ttk.Label(form, text="Start ID").grid(row=3, column=0, sticky="w", pady=4)
        self.e_start = ttk.Entry(form)
        self.e_start.grid(row=3, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(form, text="e.g. JD4521").grid(row=3, column=2, sticky="w")

        ttk.Label(form, text="End ID").grid(row=4, column=0, sticky="w", pady=4)
        self.e_end = ttk.Entry(form)
        self.e_end.grid(row=4, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(form, text="e.g. JD4546").grid(row=4, column=2, sticky="w")

        ttk.Label(form, text="Output folder").grid(row=5, column=0, sticky="w", pady=4)
        self.e_out = ttk.Entry(form)
        self.e_out.grid(row=5, column=1, sticky="ew", padx=8, pady=4)
        ttk.Button(form, text="Browse...", command=self._pick_dir).grid(
            row=5, column=2, padx=8
        )

        ttk.Label(form, text="Delay (ms)").grid(row=6, column=0, sticky="w", pady=4)
        self.e_delay = ttk.Entry(form, width=10)
        self.e_delay.grid(row=6, column=1, sticky="w", padx=8, pady=4)

        self.v_no_letterhead = ttk.Checkbutton(form, text="No letterhead")
        self.v_no_letterhead.grid(row=7, column=1, sticky="w", padx=8, pady=2)

        self.v_overwrite = ttk.Checkbutton(form, text="Overwrite existing files")
        self.v_overwrite.grid(row=8, column=1, sticky="w", padx=8, pady=2)

        self.v_open_after = ttk.Checkbutton(
            form, text="Open output folder when finished"
        )
        self.v_open_after.grid(row=9, column=1, sticky="w", padx=8, pady=2)

        self.v_notify = ttk.Checkbutton(form, text="Notify when finished")
        self.v_notify.grid(row=10, column=1, sticky="w", padx=8, pady=2)

        self.lbl_form_error = ttk.Label(
            form, text="", foreground="#b00020", wraplength=600
        )
        self.lbl_form_error.grid(row=11, column=1, sticky="w", padx=8, pady=(4, 0))

        act = ttk.Frame(self, padding=(0, 8))
        act.pack(fill="x")

        self.btn_start = ttk.Button(act, text="Start", command=self._on_start)
        self.btn_start.pack(side="left")

        self.btn_stop = ttk.Button(
            act, text="Stop", command=self._on_stop, state="disabled"
        )
        self.btn_stop.pack(side="left", padx=6)

        self.btn_test = ttk.Button(act, text="Test connection", command=self._on_test)
        self.btn_test.pack(side="left", padx=6)

        self.btn_retry = ttk.Button(
            act,
            text="Retry failed",
            command=self._on_retry_failed,
            state="disabled",
        )
        self.btn_retry.pack(side="left", padx=6)

        self.btn_open = ttk.Button(
            act,
            text="Open folder",
            command=self._on_open_folder,
            state="disabled",
        )
        self.btn_open.pack(side="left", padx=6)

        self.btn_export = ttk.Button(
            act, text="Export log", command=self._on_export_log
        )
        self.btn_export.pack(side="left", padx=6)

        self.btn_logout = ttk.Button(act, text="Sign out", command=self._on_logout)
        self.btn_logout.pack(side="right")

        self.lbl_status = ttk.Label(act, text="Ready")
        self.lbl_status.pack(side="right", padx=12)

        self.pbar = ttk.Progressbar(self, mode="determinate")
        self.pbar.pack(fill="x", pady=(0, 4))

        self.lbl_eta = ttk.Label(self, text="")
        self.lbl_eta.pack(anchor="w", pady=(0, 6))

        logf = ttk.LabelFrame(self, text="Activity log", padding=4)
        logf.pack(fill="both", expand=True)

        self.txt = tk.Text(
            logf,
            wrap="none",
            height=14,
            font=("Courier", 9),
            borderwidth=1,
            relief="solid",
        )
        sb = ttk.Scrollbar(logf, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt.pack(side="left", fill="both", expand=True)


    def on_enter(self) -> None:
        s = self.app.state
        self._prefill(self.e_doctype, s.get("doctype", ""))
        self._prefill(self.cb_format, s.get("print_format", ""))
        self._prefill(
            self.e_filename,
            s.get("filename_template", DEFAULT_FILENAME_TEMPLATE),
        )
        if not self.e_filename.get():
            self.e_filename.insert(0, DEFAULT_FILENAME_TEMPLATE)
        self._prefill(self.e_out, s.get("output_dir", ""))
        self._prefill(self.e_delay, str(s.get("delay_ms", "300")))
        if not self.e_delay.get():
            self.e_delay.insert(0, "300")

        if s.get("no_letterhead"):
            self.v_no_letterhead.state(["selected"])
        if s.get("overwrite"):
            self.v_overwrite.state(["selected"])
        if s.get("open_folder_after", True):
            self.v_open_after.state(["selected"])
        if s.get("notify_on_finish", True):
            self.v_notify.state(["selected"])

        self._refresh_presets()

        user = s.get("email", "")
        self._log(f"Signed in as: {user}" if user else "(not signed in)")

    def on_next(self):
        self.app._on_close()
        return None

    def on_leave(self) -> bool:
        if self._running:
            if not messagebox.askyesno("Exit", "Download is running. Stop and exit?"):
                return False
            worker.request_stop()
        return True

    @staticmethod
    def _prefill(widget, value: str) -> None:
        if not value:
            return
        if hasattr(widget, "set"):
            widget.set(value)
        elif not widget.get():
            widget.insert(0, value)


    def _refresh_presets(self) -> None:
        names = presets.list_names()
        self.cb_preset["values"] = names
        if names and not self.cb_preset.get():
            self.cb_preset.current(0)

    def _current_values(self) -> dict:
        return {
            "doctype": self.e_doctype.get().strip(),
            "print_format": self.cb_format.get().strip(),
            "filename_template": self.e_filename.get().strip()
            or DEFAULT_FILENAME_TEMPLATE,
            "output_dir": self.e_out.get().strip(),
            "delay_ms": self.e_delay.get().strip() or "300",
            "no_letterhead": bool(self.v_no_letterhead.instate(["selected"])),
            "overwrite": bool(self.v_overwrite.instate(["selected"])),
        }

    def _apply_values(self, values: dict) -> None:
        if values.get("doctype") is not None:
            self.e_doctype.delete(0, "end")
            self.e_doctype.insert(0, values["doctype"] or "")
        if values.get("print_format") is not None:
            self.cb_format.set(values["print_format"] or "")
        if values.get("filename_template") is not None:
            self.e_filename.delete(0, "end")
            self.e_filename.insert(
                0, values["filename_template"] or DEFAULT_FILENAME_TEMPLATE
            )
        if values.get("output_dir") is not None:
            self.e_out.delete(0, "end")
            self.e_out.insert(0, values["output_dir"] or "")
        if values.get("delay_ms") is not None:
            self.e_delay.delete(0, "end")
            self.e_delay.insert(0, str(values["delay_ms"]))
        self._apply_checkbox(self.v_no_letterhead, values.get("no_letterhead"))
        self._apply_checkbox(self.v_overwrite, values.get("overwrite"))

    @staticmethod
    def _apply_checkbox(var, value) -> None:
        if value is None:
            return
        var.state(["selected"] if value else ["!selected"])

    def _on_preset_selected(self, _event=None) -> None:
        self._on_preset_load()

    def _on_preset_load(self) -> None:
        name = self.cb_preset.get().strip()
        if not name:
            return
        values = presets.get(name)
        if values is None:
            messagebox.showerror("Preset", f"Preset {name!r} not found.")
            self._refresh_presets()
            return
        self._apply_values(values)
        self._log(f"Preset loaded: {name}")

    def _on_preset_save(self) -> None:
        name = simpledialog.askstring(
            "Save preset",
            "Preset name:",
            initialvalue=self.cb_preset.get().strip(),
            parent=self,
        )
        if not name:
            return
        try:
            presets.save(name, self._current_values())
        except ValueError as e:
            messagebox.showerror("Preset", str(e))
            return
        self._refresh_presets()
        self.cb_preset.set(name.strip())
        self._log(f"Preset saved: {name.strip()}")

    def _on_preset_delete(self) -> None:
        name = self.cb_preset.get().strip()
        if not name:
            return
        if not messagebox.askyesno("Preset", f"Delete preset {name!r}?"):
            return
        if presets.delete(name):
            self._log(f"Preset deleted: {name}")
            self.cb_preset.set("")
            self._refresh_presets()


    def _pick_dir(self) -> None:
        cur = self.e_out.get().strip() or str(Path.home())
        d = filedialog.askdirectory(initialdir=cur)
        if d:
            self.e_out.delete(0, "end")
            self.e_out.insert(0, d)

    def _collect(self) -> dict | None:
        s = dict(self.app.state)
        doctype = self.e_doctype.get().strip()
        fmt = self.cb_format.get().strip()
        filename_template = self.e_filename.get().strip() or DEFAULT_FILENAME_TEMPLATE
        start = self.e_start.get().strip().upper()
        end = self.e_end.get().strip().upper()
        out = self.e_out.get().strip()
        delay_raw = self.e_delay.get().strip() or "300"

        if not doctype:
            self.lbl_form_error.config(text="DocType is required.")
            return None
        if not start or not end:
            self.lbl_form_error.config(text="Start and End ID are required.")
            return None
        if not out:
            self.lbl_form_error.config(text="Output folder is required.")
            return None
        try:
            delay = int(delay_raw)
        except ValueError:
            self.lbl_form_error.config(text="Delay must be a number.")
            return None
        if delay < 0:
            self.lbl_form_error.config(text="Delay cannot be negative.")
            return None

        # validate template: only {name} and {customer} are allowed
        if "{" in filename_template or "}" in filename_template:
            try:
                filename_template.format(name="TEST", customer="TEST")
            except (KeyError, IndexError, ValueError) as e:
                self.lbl_form_error.config(
                    text=f"Filename template invalid: {e}. "
                    f"Use only {{name}} and {{customer}}."
                )
                return None

        out_path = Path(out).expanduser()
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_path

        s.update(
            doctype=doctype,
            print_format=fmt,
            filename_template=filename_template,
            start=start,
            end=end,
            output_dir=str(out_path),
            delay_ms=delay,
            no_letterhead=bool(self.v_no_letterhead.instate(["selected"])),
            overwrite=bool(self.v_overwrite.instate(["selected"])),
            open_folder_after=bool(self.v_open_after.instate(["selected"])),
            notify_on_finish=bool(self.v_notify.instate(["selected"])),
        )
        self.app.state.update(s)
        return s


    def _on_test(self) -> None:
        s = self._collect()
        if s is None:
            return
        pw = s.get("password", "")
        if not pw:
            messagebox.showerror("Test connection", "Password is missing.")
            return

        self._log("")
        self._log("=== test connection ===")
        self.lbl_status.config(text="testing...")
        self.btn_test.config(state="disabled")
        worker.run(self._job_test, self.app.queue, s)

    def _job_test(self, s: dict) -> None:
        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        try:
            client.authenticate()
            self.app.queue.put(
                (
                    "test.ok",
                    (
                        client.boot_sitename(),
                        client.boot_user_full_name(),
                        client.boot_user_roles(),
                    ),
                )
            )
        except Exception as e:
            self.app.queue.put(("test.err", e))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass

    def _on_detect_formats(self) -> None:
        s = self._collect()
        if s is None:
            return
        doctype = s.get("doctype", "")
        pw = s.get("password", "")
        if not doctype:
            messagebox.showerror("Detect", "Fill in DocType first.")
            return
        if not pw:
            messagebox.showerror("Detect", "Password is missing.")
            return

        self._log(f"Detecting print formats for {doctype!r}...")
        self.btn_start.config(state="disabled")
        worker.run(self._job_detect, self.app.queue, s)

    def _job_detect(self, s: dict) -> None:
        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        try:
            client.authenticate()
            import urllib.parse as _up

            doctype = s["doctype"]
            filters = json.dumps([["doc_type", "=", doctype]])
            fields = json.dumps(["name", "standard", "disabled"])
            path = (
                "/api/method/frappe.client.get_list"
                f"?doctype={_up.quote('Print Format')}"
                f"&filters={_up.quote(filters)}"
                f"&fields={_up.quote(fields)}"
                "&limit_page_length=0"
                "&order_by=standard desc"
            )
            raw = client.get(path)
            data = json.loads(raw)
            items = data.get("message") or []
            names = [
                it.get("name")
                for it in items
                if isinstance(it, dict) and not it.get("disabled")
            ]
            names = [n for n in names if n]
            self.app.queue.put(("detect.ok", names))
        except Exception as e:
            self.app.queue.put(("detect.err", e))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass

    def _on_start(self) -> None:
        if self._running:
            return
        s = self._collect()
        if s is None:
            return
        if not s.get("password"):
            messagebox.showerror("Start", "Password is missing.")
            return

        try:
            names = expand_range(s["start"], s["end"])
        except ValueError as e:
            self.lbl_form_error.config(text=str(e))
            return

        self.lbl_form_error.config(text="")
        self._failed = []
        self.btn_retry.config(state="disabled")
        self.btn_open.config(state="disabled")
        self._launch_run(s, names)

    def _on_retry_failed(self) -> None:
        if self._running or not self._failed:
            return
        s = self._collect()
        if s is None:
            return
        names = list(self._failed)
        self._failed = []
        self._log("")
        self._log(f"=== retrying {len(names)} failed item(s) ===")
        self._launch_run(s, names)

    def _launch_run(self, s: dict, names: list[str]) -> None:
        self._log("")
        self._log(f"=== starting {len(names)} document(s) ===")
        self._log(f"first   : {names[0]}")
        self._log(f"last    : {names[-1]}")
        self._log(f"doctype : {s['doctype']}")
        self._log(f"format  : {s['print_format'] or '(default)'}")
        self._log(f"filename: {s.get('filename_template', DEFAULT_FILENAME_TEMPLATE)}")
        self._log(f"output  : {s['output_dir']}")

        self._running = True
        self._run_started_at = time.monotonic()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_test.config(state="disabled")
        self.btn_logout.config(state="disabled")
        self.pbar.config(maximum=len(names), value=0)
        self.lbl_status.config(text="Signing in...")
        self.lbl_eta.config(text="")

        worker.reset_stop()
        worker.run(self._job, self.app.queue, dict(s), names)

    def _on_stop(self) -> None:
        worker.request_stop()
        self._log("(stop requested, waiting for current request)")
        self.lbl_status.config(text="Stopping...")

    def _on_open_folder(self) -> None:
        path = self.e_out.get().strip()
        if not path:
            return
        p = Path(path).expanduser()
        if not p.exists():
            messagebox.showerror("Open folder", f"Folder does not exist:\n{p}")
            return
        try:
            _open_path(p)
        except Exception as e:
            messagebox.showerror("Open folder", str(e))

    def _on_export_log(self) -> None:
        content = self.txt.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Export log", "Log is empty.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*"),
            ],
            initialfile="spjss.log",
        )
        if not path:
            return
        try:
            Path(path).write_text(content + "\n", encoding="utf-8")
            self._log(f"Log exported to {path}")
        except OSError as e:
            messagebox.showerror("Export log", str(e))

    def _on_logout(self) -> None:
        if self._running:
            return
        email = self.app.state.get("email", "")
        if email and not self.app.state.get("remember_password"):
            keyring.delete(email)
        self.app.state.pop("password", None)
        from .login import LoginPage

        self.app.history.clear()
        self.app._show(LoginPage, push=False)


    def _job(self, s: dict, names: list[str]) -> None:
        out_dir = Path(s["output_dir"])
        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        self.app.queue.put(("run.login", None))
        try:
            client.authenticate()
            self.app.queue.put(
                (
                    "run.logged_in",
                    (client.boot_sitename(), client.boot_user_full_name()),
                )
            )
            summary = download_range(
                client=client,
                doctype=s["doctype"],
                names=names,
                fmt=s["print_format"],
                out_dir=out_dir,
                delay_ms=s["delay_ms"],
                no_letterhead=s["no_letterhead"],
                overwrite=s["overwrite"],
                filename_template=s.get("filename_template", DEFAULT_FILENAME_TEMPLATE),
                customer_regex=s.get("customer_regex") or None,
                on_progress=lambda i, t, r: self.app.queue.put(
                    ("run.progress", (i, t, r))
                ),
                should_stop=worker.should_stop,
            )
            self.app.queue.put(("run.done", summary))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass


    def handle(self, kind: str, payload) -> None:
        if kind == "run.login":
            self.lbl_status.config(text="Signing in...")

        elif kind == "run.logged_in":
            site, user = payload
            self._log(f"Signed in: {user} @ {site}")
            self.lbl_status.config(text="Downloading...")

        elif kind == "run.progress":
            i, total, r = payload
            self.pbar.config(value=i)
            elapsed = time.monotonic() - self._run_started_at
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / rate if rate > 0 else 0
            eta_str = _fmt_duration(remaining)
            self.lbl_status.config(text=f"{i}/{total}")
            self.lbl_eta.config(
                text=f"ETA {eta_str}  |  {rate:.1f} item/s  |  elapsed {_fmt_duration(elapsed)}"
            )
            if r.ok:
                if r.skipped:
                    self._log(f"[{i}/{total}] {r.name}  skipped (already exists)")
                else:
                    kb = r.bytes / 1024.0
                    if getattr(r, "extraction_failed", False):
                        self._log(
                            f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB  "
                            f"(nama customer tidak terbaca, fallback ke ID)"
                        )
                    elif getattr(r, "customer", None) and r.customer != r.name:
                        self._log(
                            f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB  ({r.customer})"
                        )
                    else:
                        self._log(f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB")
            else:
                self._log(f"[{i}/{total}] {r.name}  FAILED: {r.error}")
                if r.name not in self._failed:
                    self._failed.append(r.name)

        elif kind == "run.done":
            summary = payload
            self._last_summary = summary
            self._running = False
            self._log("")
            self._log(
                f"Done: {summary.ok} ok "
                f"({summary.skipped} skipped), "
                f"{summary.failed} failed, "
                f"{summary.total} total"
            )
            if summary.aborted:
                self._log("(stopped by user, some items not processed)")

            elapsed = time.monotonic() - self._run_started_at
            self.lbl_eta.config(text=f"Elapsed {_fmt_duration(elapsed)}")

            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_test.config(state="normal")
            self.btn_logout.config(state="normal")

            if self._failed:
                self.btn_retry.config(state="normal")
            else:
                self.btn_retry.config(state="disabled")

            self.btn_open.config(state="normal")

            self.lbl_status.config(text=f"{summary.ok} ok / {summary.failed} failed")

            s = self.app.state
            cfgmod.save(
                {
                    "base_url": s.get("base_url", ""),
                    "email": s.get("email", ""),
                    "insecure_ssl": s.get("insecure_ssl", False),
                    "remember_password": s.get("remember_password", False),
                    "doctype": s.get("doctype", ""),
                    "print_format": s.get("print_format", ""),
                    "filename_template": s.get(
                        "filename_template", DEFAULT_FILENAME_TEMPLATE
                    ),
                    "customer_regex": s.get("customer_regex", ""),
                    "output_dir": s.get("output_dir", ""),
                    "delay_ms": str(s.get("delay_ms", 300)),
                    "no_letterhead": s.get("no_letterhead", False),
                    "overwrite": s.get("overwrite", False),
                    "open_folder_after": s.get("open_folder_after", True),
                    "notify_on_finish": s.get("notify_on_finish", True),
                }
            )

            if not summary.aborted:
                if s.get("notify_on_finish", True):
                    self.bell()
                    self.app.after(
                        100,
                        lambda: messagebox.showinfo(
                            "Download complete",
                            f"{summary.ok} ok "
                            f"({summary.skipped} skipped)\n"
                            f"{summary.failed} failed\n"
                            f"Elapsed {_fmt_duration(elapsed)}",
                        ),
                    )
                if s.get("open_folder_after", True) and summary.ok:
                    try:
                        _open_path(Path(s["output_dir"]))
                    except Exception as e:
                        self._log(f"(could not open folder: {e})")

        elif kind == "test.ok":
            site, user, roles = payload
            self.btn_test.config(state="normal")
            self.lbl_status.config(text="Connection OK")
            self._log("Connection OK")
            self._log(f"  site : {site}")
            self._log(f"  user : {user}")
            self._log(f"  roles: {', '.join(roles) if roles else '(none)'}")
            messagebox.showinfo(
                "Connection test",
                f"Site: {site}\nUser: {user}\nRoles: {len(roles)}",
            )

        elif kind == "test.err":
            self.btn_test.config(state="normal")
            self.lbl_status.config(text="Connection failed")
            self._log(f"Connection failed: {payload}")
            messagebox.showerror("Connection test", str(payload))

        elif kind == "detect.ok":
            names = payload
            self.btn_start.config(state="normal")
            if not names:
                self._log("No print formats found for that DocType.")
                messagebox.showinfo("Detect", "No print formats found.")
                return
            self.cb_format["values"] = names
            if not self.cb_format.get():
                self.cb_format.set(names[0])
            self._log(f"Found {len(names)} print format(s):")
            for n in names[:10]:
                self._log(f"  {n}")
            if len(names) > 10:
                self._log(f"  ... and {len(names) - 10} more")

        elif kind == "detect.err":
            self.btn_start.config(state="normal")
            self._log(f"Detect failed: {payload}")
            messagebox.showerror("Detect", str(payload))

        elif kind == "err":
            self._running = False
            self._log(f"ERROR: {payload}")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_test.config(state="normal")
            self.btn_logout.config(state="normal")
            self.lbl_status.config(text="Error")

    def _log(self, msg: str) -> None:
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")




def _fmt_duration(seconds: float) -> str:
    if seconds < 0 or seconds != seconds:
        return "--:--"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


def _open_path(path: Path) -> None:
    system = platform.system()
    if system == "Windows":
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
```
## src/spjss/pages/login.py

```python
from tkinter import ttk

from .. import config as cfgmod
from .. import keyring_helper as keyring
from .base import Page


class LoginPage(Page):
    title = "Sign in"
    step_label = "Sign in"

    def build(self) -> None:
        ttk.Label(
            self,
            text=(
                "Enter your credentials. Your password is sent only to "
                "the server you specify."
            ),
            wraplength=640,
        ).pack(anchor="w", pady=(0, 12))

        form = ttk.Frame(self)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Base URL").grid(row=0, column=0, sticky="w", pady=6)
        self.e_url = ttk.Entry(form)
        self.e_url.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(form, text="Email").grid(row=1, column=0, sticky="w", pady=6)
        self.e_email = ttk.Entry(form)
        self.e_email.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(form, text="Password").grid(row=2, column=0, sticky="w", pady=6)
        self.e_pw = ttk.Entry(form, show="\u2022")
        self.e_pw.grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        self.v_remember = ttk.Checkbutton(
            form,
            text=(
                f"Remember password on this device ({keyring.backend_name()})"
                if keyring.is_available()
                else "Remember password on this device (not available)"
            ),
        )
        if not keyring.is_available():
            self.v_remember.state(["disabled"])
        self.v_remember.grid(row=3, column=1, sticky="w", padx=8, pady=2)

        self.v_insecure = ttk.Checkbutton(
            form,
            text="Allow invalid SSL certificates (development only)",
        )
        self.v_insecure.grid(row=4, column=1, sticky="w", padx=8, pady=2)

        self.lbl_error = ttk.Label(self, text="", foreground="#b00020", wraplength=640)
        self.lbl_error.pack(anchor="w", pady=(12, 0))

    def on_enter(self) -> None:
        s = self.app.state
        if not self.e_url.get():
            self.e_url.insert(0, s.get("base_url", ""))
        if not self.e_email.get():
            self.e_email.insert(0, s.get("email", ""))

        if s.get("remember_password"):
            self.v_remember.state(["selected"])

        email = self.e_email.get().strip()
        if email and not self.e_pw.get() and keyring.is_available():
            saved = keyring.load(email)
            if saved:
                self.e_pw.insert(0, saved)

        self.v_insecure.state(
            ["selected"] if s.get("insecure_ssl", False) else ["!selected"]
        )

    def on_next(self):
        url = self.e_url.get().strip().rstrip("/")
        email = self.e_email.get().strip()
        pw = self.e_pw.get()
        remember = bool(self.v_remember.instate(["selected"]))
        insecure = bool(self.v_insecure.instate(["selected"]))

        if not url:
            self.lbl_error.config(text="Base URL is required.")
            return None
        if not url.startswith(("http://", "https://")):
            self.lbl_error.config(text="Base URL must start with http:// or https://")
            return None
        if not email:
            self.lbl_error.config(text="Email is required.")
            return None
        if not pw:
            self.lbl_error.config(text="Password is required.")
            return None

        self.app.state["base_url"] = url
        self.app.state["email"] = email
        self.app.state["password"] = pw
        self.app.state["remember_password"] = remember
        self.app.state["insecure_ssl"] = insecure

        if remember and keyring.is_available():
            keyring.save(email, pw)
        elif not remember and keyring.is_available():
            keyring.delete(email)

        cfgmod.save(
            {
                "base_url": url,
                "email": email,
                "insecure_ssl": insecure,
                "remember_password": remember,
            }
        )

        self.lbl_error.config(text="")
        from .dashboard import DashboardPage

        return DashboardPage

    def on_back(self):
        from .third_party import ThirdPartyPage

        return ThirdPartyPage
```
## src/spjss/pages/run.py

```python
import tkinter as tk
from tkinter import messagebox, ttk

from .. import config as cfgmod
from .. import worker
from .._native import RjssClient
from ..downloader import download_range, expand_range
from .base import Page


class RunPage(Page):
    title = "Menjalankan"
    step_label = "Unduhan"
    next_label = "Selesai"
    back_label = "< Ulangi"
    show_next = False

    def build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x")
        self.lbl_status = ttk.Label(top, text="menyiapkan...")
        self.lbl_status.pack(side="left")
        self.btn_stop = ttk.Button(top, text="Hentikan", command=self._on_stop)
        self.btn_stop.pack(side="right")

        self.pbar = ttk.Progressbar(self, mode="determinate")
        self.pbar.pack(fill="x", pady=8)

        logf = ttk.Frame(self)
        logf.pack(fill="both", expand=True)
        self.txt = tk.Text(
            logf,
            wrap="none",
            height=18,
            font=("Courier", 9),
            borderwidth=1,
            relief="solid",
        )
        sb = ttk.Scrollbar(logf, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt.pack(side="left", fill="both", expand=True)

        self._finished = False
        self._results: list = []

    def on_enter(self) -> None:
        if self._finished:
            return
        s = self.app.state
        try:
            names = expand_range(s["start"], s["end"])
        except ValueError as e:
            self._log(f"rentang tidak valid: {e}")
            self.lbl_status.config(text="error")
            return

        self.pbar.config(maximum=len(names), value=0)
        self.lbl_status.config(text=f"0/{len(names)}")
        self._log(f"login ke {s['base_url']} ...")

        worker.reset_stop()
        worker.run(self._job, self.app.queue, dict(s), names)

    def _log(self, msg: str) -> None:
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")

    def _on_stop(self) -> None:
        worker.request_stop()
        self._log("(stop diminta, tunggu request aktif selesai)")
        self.lbl_status.config(text="stop...")

    def _job(self, s: dict, names: list[str]) -> None:
        from pathlib import Path

        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        self.app.queue.put(("run.login", None))
        try:
            client.authenticate()
            self.app.queue.put(
                (
                    "run.logged_in",
                    (
                        client.boot_sitename(),
                        client.boot_user_full_name(),
                    ),
                )
            )

            out_dir = Path(s["output_dir"])
            results = download_range(
                client=client,
                doctype=s["doctype"],
                names=names,
                fmt=s["print_format"],
                out_dir=out_dir,
                delay_ms=s["delay_ms"],
                no_letterhead=s["no_letterhead"],
                overwrite=s["overwrite"],
                on_progress=lambda i, t, r: self.app.queue.put(
                    ("run.progress", (i, t, r))
                ),
                should_stop=worker.should_stop,
            )
            self.app.queue.put(("run.done", results))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass

    def handle(self, kind: str, payload) -> None:
        if kind == "run.login":
            self.lbl_status.config(text="login...")

        elif kind == "run.logged_in":
            site, user = payload
            self._log(f"login ok: {user} @ {site}")
            self.lbl_status.config(text="mengunduh...")

        elif kind == "run.progress":
            i, total, r = payload
            self.pbar.config(value=i)
            self.lbl_status.config(text=f"{i}/{total}")
            if r.ok:
                if r.error and r.error.startswith("skip"):
                    self._log(f"[{i}/{total}] {r.name}  {r.error}")
                else:
                    kb = r.bytes / 1024.0
                    self._log(f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB")
            else:
                self._log(f"[{i}/{total}] {r.name}  GAGAL: {r.error}")

        elif kind == "run.done":
            results = payload
            self._results = results
            ok = sum(1 for r in results if r.ok)
            fail = len(results) - ok
            self._log("")
            self._log(f"selesai: {ok} ok, {fail} gagal, total {len(results)}")

            s = self.app.state
            cfgmod.save(
                {
                    "base_url": s.get("base_url", ""),
                    "email": s.get("email", ""),
                    "insecure_ssl": s.get("insecure_ssl", False),
                    "doctype": s.get("doctype", ""),
                    "print_format": s.get("print_format", ""),
                    "output_dir": s.get("output_dir", ""),
                    "delay_ms": str(s.get("delay_ms", 300)),
                    "no_letterhead": s.get("no_letterhead", False),
                    "overwrite": s.get("overwrite", False),
                }
            )

            self._finished = True
            self.show_next = True
            self.btn_stop.config(state="disabled")
            self.lbl_status.config(text=f"{ok} ok / {fail} gagal")
            self.app.refresh_nav()

        elif kind == "err":
            self._log(f"ERROR: {payload!r}")
            self.btn_stop.config(state="disabled")
            self.lbl_status.config(text="error")
            self._finished = True
            self.show_next = True
            self.app.refresh_nav()


    def on_next(self):
        self.app.destroy()
        return None

    def on_back(self):
        self._finished = False
        from .review import ReviewPage

        return ReviewPage

    def on_leave(self) -> bool:
        if not self._finished and not worker.should_stop():
            if not messagebox.askyesno(
                "Keluar dari halaman ini?",
                "Unduhan sedang berjalan. Hentikan dan kembali?",
            ):
                return False
            worker.request_stop()
        return True
```
## src/spjss/app.py

```python
import queue
import tkinter as tk
from tkinter import messagebox, ttk

from . import config as cfgmod
from ._native import version as lib_version
from .pages import LoginPage, WelcomePage


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("spjss")
        self.geometry("960x820")
        self.minsize(820, 700)

        self.queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.state: dict = {}
        self.state.update(cfgmod.load())

        self.nav = ttk.Frame(self, padding=10)
        self.nav.pack(side="bottom", fill="x")

        self.lbl_step = ttk.Label(self.nav, text="")
        self.lbl_step.pack(side="left")

        self.btn_next = ttk.Button(self.nav, text="Next >", command=self.go_next)
        self.btn_next.pack(side="right")

        self.btn_back = ttk.Button(self.nav, text="< Back", command=self.go_back)
        self.btn_back.pack(side="right", padx=8)

        self.content = ttk.Frame(self)
        self.content.pack(side="top", fill="both", expand=True)

        self.current = None
        self.history: list = []

        if self.state.get("first_run_complete"):
            self._show(LoginPage, push=False)
        else:
            self._show(WelcomePage, push=False)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._pump)

        self._log(f"librjss-ffi: {lib_version()}")
        if cfgmod.exists():
            self._log(f"Config loaded from {cfgmod.CONFIG_PATH}")


    def _show(self, PageCls, push: bool = True) -> None:
        if self.current is not None:
            if not self.current.on_leave():
                return
            if push:
                self.history.append(type(self.current))
            self.current.destroy()

        page = PageCls(self.content, self)
        page.pack(fill="both", expand=True)
        self.current = page

        self.lbl_step.config(text=page.step_label or page.title)
        self.btn_back.config(
            text=page.back_label,
            state="normal" if page.show_back else "disabled",
        )
        self.btn_next.config(
            text=page.next_label,
            state="normal" if page.show_next else "disabled",
        )

        page.on_enter()

    def refresh_nav(self) -> None:
        p = self.current
        if p is None:
            return
        self.btn_next.config(
            text=p.next_label,
            state="normal" if p.show_next else "disabled",
        )
        self.btn_back.config(
            text=p.back_label,
            state="normal" if p.show_back else "disabled",
        )

    def go_next(self) -> None:
        if self.current is None:
            return
        result = self.current.on_next()
        if result is None:
            return
        if result == "back":
            self.go_back()
            return
        if isinstance(result, type):
            self._show(result, push=True)
            return
        if callable(result):
            result()

    def go_back(self) -> None:
        if not self.history:
            return
        prev = self.history.pop()
        self._show(prev, push=False)


    def _pump(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                self._dispatch(kind, payload)
        except queue.Empty:
            pass
        self.after(100, self._pump)

    def _dispatch(self, kind: str, payload) -> None:
        handler = getattr(self.current, "handle", None)
        if callable(handler):
            try:
                handler(kind, payload)
            except Exception as e:
                print(f"handler error: {e!r}")
        else:
            if kind == "err":
                messagebox.showerror("Error", str(payload))


    def _log(self, msg: str) -> None:
        log = getattr(self.current, "_log", None)
        if callable(log):
            log(msg)

    def _on_close(self) -> None:
        from . import worker

        if getattr(self.current, "_running", False):
            if not messagebox.askyesno("Exit", "Download is running. Stop and exit?"):
                return
            worker.request_stop()

        self.state.pop("password", None)
        self.destroy()
```
## src/spjss/config.py

```python
import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("APPDATA") or (Path.home() / ".config")) / "spjss"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULTS: dict = {
    "first_run_complete": False,
    "base_url": "",
    "email": "",
    "insecure_ssl": False,
    "remember_password": False,
    "doctype": "",
    "print_format": "",
    "filename_template": "{name}",
    "customer_regex": "",
    "output_dir": "",
    "delay_ms": "300",
    "no_letterhead": False,
    "overwrite": False,
    "open_folder_after": True,
    "notify_on_finish": True,
}

FIELDS_PERSISTED = tuple(DEFAULTS.keys())


def load() -> dict:
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.is_file():
        try:
            data = json.loads(CONFIG_PATH.read_text("utf-8"))
        except Exception:
            data = {}
        for k in FIELDS_PERSISTED:
            if k in data:
                cfg[k] = data[k]
    return cfg


def _write(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    out = {k: cfg.get(k, DEFAULTS[k]) for k in FIELDS_PERSISTED}
    CONFIG_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save(cfg: dict) -> None:
    current = load()
    current.update({k: v for k, v in cfg.items() if k in FIELDS_PERSISTED})
    _write(current)


def mark_first_run_complete() -> None:
    cfg = load()
    cfg["first_run_complete"] = True
    _write(cfg)


def exists() -> bool:
    return CONFIG_PATH.is_file()


def clear() -> None:
    if CONFIG_PATH.is_file():
        CONFIG_PATH.unlink()
```
## src/spjss/downloader.py

```python
"""
Batch downloader for Frappe print-format PDFs.

Public API:
    expand_range(start, end, max_items=1000) -> list[str]
    download_one(client, doctype, name, fmt, out_dir, ...) -> DownloadResult
    download_range(client, doctype, names, fmt, out_dir, ...) -> BatchSummary
"""

from __future__ import annotations

import io
import json
import re
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ._native import JssError, RjssClient

# ── optional PDF text extraction ─────────────────────────────────────

try:
    from pypdf import PdfReader as _PdfReader  # type: ignore
except ImportError:
    try:
        from PyPDF2 import PdfReader as _PdfReader  # type: ignore
    except ImportError:
        _PdfReader = None  # type: ignore


# ── constants ────────────────────────────────────────────────────────

DEFAULT_PRINT_FORMAT = "Standard"
DEFAULT_MAX_RANGE = 1000
DEFAULT_DELAY_MS = 300
DEFAULT_FILENAME_TEMPLATE = "{name}"
MAX_FILENAME_LEN = 200
PDF_MAGIC = b"%PDF-"
NAME_CACHE_FILE = ".spjss_names.json"


# ── result ───────────────────────────────────────────────────────────


@dataclass
class DownloadResult:
    name: str
    ok: bool
    path: Path | None = None
    error: str | None = None
    bytes: int = 0
    skipped: bool = False
    customer: str | None = None
    extraction_failed: bool = False

    @property
    def failed(self) -> bool:
        return not self.ok and not self.skipped

    def __str__(self) -> str:
        if self.ok and self.skipped:
            return f"{self.name}: skip (sudah ada)"
        if self.ok:
            kb = self.bytes / 1024.0
            tag = f" [{self.customer}]" if self.customer else ""
            return f"{self.name}: ok ({kb:.1f} KB){tag}"
        return f"{self.name}: gagal ({self.error})"


# ── range expansion ──────────────────────────────────────────────────


def _split_id(value: str) -> tuple[str, int]:
    value = value.strip()
    i = 0
    while i < len(value) and not value[i].isdigit():
        i += 1
    prefix = value[:i]
    digits = value[i:]
    if not prefix:
        raise ValueError(f"ID harus punya prefix huruf: {value!r}")
    if not digits:
        raise ValueError(f"ID harus punya angka di akhir: {value!r}")
    if not digits.isdigit():
        raise ValueError(f"angka tidak valid di ID: {value!r}")
    return prefix, int(digits)


def expand_range(
    start: str,
    end: str,
    max_items: int = DEFAULT_MAX_RANGE,
) -> list[str]:
    start = start.strip().upper()
    end = end.strip().upper()
    if not start:
        raise ValueError("Start ID wajib diisi.")
    if not end:
        raise ValueError("End ID wajib diisi.")

    p1, n1 = _split_id(start)
    p2, n2 = _split_id(end)

    if p1 != p2:
        raise ValueError(f"prefix Start dan End harus sama: {p1!r} vs {p2!r}")
    if n1 > n2:
        raise ValueError(f"Start ({n1}) lebih besar dari End ({n2}). Tukar posisinya.")

    count = n2 - n1 + 1
    if max_items > 0 and count > max_items:
        raise ValueError(
            f"rentang terlalu besar: {count} dokumen (maksimum {max_items} per batch)"
        )

    width = max(len(str(n1)), len(str(n2)))
    return [f"{p1}{n:0{width}d}" for n in range(n1, n2 + 1)]


# ── filename safety ──────────────────────────────────────────────────

_FORBIDDEN_CHARS = set('<>:"/\\|?*')
_CONTROL_CHARS = {chr(i) for i in range(0x20)} | {chr(0x7F)}


def _safe_filename(name: str) -> str:
    cleaned: list[str] = []
    for ch in name:
        if ch in _FORBIDDEN_CHARS or ch in _CONTROL_CHARS:
            cleaned.append("_")
        else:
            cleaned.append(ch)
    stem = "".join(cleaned).strip().rstrip(".")
    if not stem:
        raise ValueError(f"nama dokumen tidak valid: {name!r}")

    upper = stem.upper()
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if upper in reserved:
        stem = f"_{stem}"
    if len(stem) > MAX_FILENAME_LEN:
        stem = stem[:MAX_FILENAME_LEN]
    return stem


# ── template rendering ───────────────────────────────────────────────

_STRING_FORMATTER = __import__("string").Formatter()


def _template_uses_customer(template: str) -> bool:
    """Return True if the template references the {customer} placeholder."""
    if not template:
        return False
    try:
        for _, field_name, _, _ in _STRING_FORMATTER.parse(template):
            if field_name == "customer":
                return True
    except Exception:
        # invalid template; let _render_filename raise a proper error
        pass
    return False


def _render_filename(
    template: str,
    name: str,
    customer: str | None = None,
) -> str:
    """Render the filename template.

    Placeholders:
        {name}      document identifier, e.g. JD4521
        {customer}  customer name extracted from the PDF, e.g. SUHARTINA
    """
    tmpl = (template or "").strip() or DEFAULT_FILENAME_TEMPLATE
    values = {
        "name": name,
        "customer": customer if customer is not None else "",
    }
    try:
        return tmpl.format(**values)
    except (KeyError, IndexError, ValueError) as e:
        raise ValueError(f"template nama file tidak valid: {tmpl!r} ({e})")


# ── PDF text extraction ──────────────────────────────────────────────

_DEFAULT_CUSTOMER_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "Bapak/ Ibu SUHARTINA" followed by newline, JL., Perihal, etc.
    re.compile(
        r"Bapak\s*/\s*Ibu\s+"
        r"([A-Z][A-Za-z\s\.'\-]{1,80}?)"
        r"(?=\s*(?:Jl\.|JL\.|Perihal|PERIHAL|Alamat|ALAMAT|$))",
        re.MULTILINE,
    ),
    # Fallback: everything up to the end of the line
    re.compile(
        r"Bapak\s*/\s*Ibu\s+([^\n\r]{1,80})",
        re.IGNORECASE,
    ),
)


def _extract_pdf_text(pdf_bytes: bytes) -> str | None:
    """Return the concatenated text of all pages, or None on failure."""
    if _PdfReader is None:
        return None
    try:
        reader = _PdfReader(io.BytesIO(pdf_bytes))
    except Exception:
        return None
    parts: list[str] = []
    try:
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                parts.append("")
    except Exception:
        return None
    return "\n".join(parts)


def _extract_customer_name(
    pdf_bytes: bytes,
    custom_pattern: str | None = None,
) -> str | None:
    """Extract the customer name from a PDF.

    Tries the caller-supplied regex first (if any), then the built-in
    patterns that match common Indonesian letter openings such as
    'Bapak/ Ibu <NAME>'. Returns None if nothing is found.
    """
    text = _extract_pdf_text(pdf_bytes)
    if not text:
        return None

    if custom_pattern:
        try:
            rx = re.compile(custom_pattern, re.MULTILINE | re.IGNORECASE)
            m = rx.search(text)
            if m:
                captured = m.group(1) if m.groups() else m.group(0)
                cleaned = captured.strip().strip(".,;:")
                if cleaned:
                    return cleaned
        except re.error:
            pass

    for rx in _DEFAULT_CUSTOMER_PATTERNS:
        m = rx.search(text)
        if m:
            cleaned = m.group(1).strip().strip(".,;:")
            # collapse internal whitespace
            cleaned = re.sub(r"\s+", " ", cleaned)
            if cleaned:
                return cleaned
    return None


# ── name cache (name -> customer) ────────────────────────────────────


def _load_name_cache(out_dir: Path) -> dict[str, str]:
    p = out_dir / NAME_CACHE_FILE
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text("utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def _save_name_cache(out_dir: Path, cache: dict[str, str]) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / NAME_CACHE_FILE
        p.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass


# ── PDF sanity ───────────────────────────────────────────────────────


def _looks_like_pdf(data: bytes) -> bool:
    return len(data) >= len(PDF_MAGIC) and data.startswith(PDF_MAGIC)


def _error_snippet(data: bytes, limit: int = 120) -> str:
    if not data:
        return "(kosong)"
    chunk = data[:limit]
    try:
        text = chunk.decode("utf-8", errors="replace")
    except Exception:
        return repr(chunk)
    text = text.replace("\r", " ").replace("\n", " ").strip()
    if len(data) > limit:
        text += "..."
    return text


# ── single download ──────────────────────────────────────────────────


def download_one(
    client: RjssClient,
    doctype: str,
    name: str,
    fmt: str,
    out_dir: Path,
    no_letterhead: bool = False,
    overwrite: bool = False,
    filename_template: str = DEFAULT_FILENAME_TEMPLATE,
    customer_regex: str | None = None,
) -> DownloadResult:
    if not doctype or not doctype.strip():
        raise ValueError("doctype tidak boleh kosong")
    if not name or not name.strip():
        raise ValueError("name tidak boleh kosong")

    out_dir = Path(out_dir)
    fmt_effective = fmt.strip() if fmt else DEFAULT_PRINT_FORMAT
    uses_customer = _template_uses_customer(filename_template)

    # ── fast path: we can compute the destination without downloading
    if not uses_customer:
        try:
            stem = _safe_filename(_render_filename(filename_template, name))
        except ValueError as e:
            return DownloadResult(name=name, ok=False, error=str(e))
        dest = out_dir / f"{stem}.pdf"
        if dest.is_file() and not overwrite:
            try:
                size = dest.stat().st_size
            except OSError:
                size = 0
            return DownloadResult(
                name=name,
                ok=True,
                path=dest,
                bytes=size,
                error="skip (sudah ada)",
                skipped=True,
            )

    # ── cache lookup for customer-based templates
    cache: dict[str, str] = {}
    if uses_customer:
        cache = _load_name_cache(out_dir)
        cached = cache.get(name)
        if cached:
            try:
                stem = _safe_filename(_render_filename(filename_template, name, cached))
                dest = out_dir / f"{stem}.pdf"
                if dest.is_file() and not overwrite:
                    try:
                        size = dest.stat().st_size
                    except OSError:
                        size = 0
                    return DownloadResult(
                        name=name,
                        ok=True,
                        path=dest,
                        bytes=size,
                        error="skip (sudah ada)",
                        skipped=True,
                        customer=cached,
                    )
            except ValueError:
                pass

    # ── fetch from server
    try:
        data = client.download_pdf_kartu_piutang(
            doctype, name, fmt_effective, no_letterhead
        )
    except JssError as e:
        return DownloadResult(name=name, ok=False, error=f"{e}")
    except Exception as e:
        return DownloadResult(name=name, ok=False, error=f"unexpected: {e!r}")

    if not data:
        return DownloadResult(name=name, ok=False, error="response kosong")
    if not _looks_like_pdf(data):
        return DownloadResult(
            name=name,
            ok=False,
            error=f"bukan PDF (server mengembalikan): {_error_snippet(data)}",
        )

    # ── extract customer name if needed
    customer: str | None = None
    extraction_failed = False
    if uses_customer:
        customer = _extract_customer_name(data, customer_regex)
        if not customer:
            if _PdfReader is None:
                return DownloadResult(
                    name=name,
                    ok=False,
                    error=(
                        "template '{customer}' butuh modul 'pypdf' "
                        "(install: pip install pypdf)"
                    ),
                )
            customer = name
            extraction_failed = True

    # ── compute destination
    try:
        stem = _safe_filename(_render_filename(filename_template, name, customer))
    except ValueError as e:
        return DownloadResult(name=name, ok=False, error=str(e), customer=customer)

    dest = out_dir / f"{stem}.pdf"

    if dest.is_file() and not overwrite:
        try:
            size = dest.stat().st_size
        except OSError:
            size = 0
        if uses_customer and customer and not extraction_failed:
            cache[name] = customer
            _save_name_cache(out_dir, cache)
        return DownloadResult(
            name=name,
            ok=True,
            path=dest,
            bytes=size,
            error="skip (sudah ada)",
            skipped=True,
            customer=customer,
        )

    # ── write to disk
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return DownloadResult(
            name=name,
            ok=False,
            error=f"gagal buat folder {out_dir}: {e}",
        )

    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        tmp.write_bytes(data)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return DownloadResult(
            name=name,
            ok=False,
            error=f"gagal tulis {dest.name}: {e}",
        )

    try:
        tmp.replace(dest)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return DownloadResult(
            name=name,
            ok=False,
            error=f"gagal pindahkan file: {e}",
        )

    if uses_customer and customer and not extraction_failed:
        cache[name] = customer
        _save_name_cache(out_dir, cache)

    return DownloadResult(
        name=name,
        ok=True,
        path=dest,
        bytes=len(data),
        customer=customer,
        extraction_failed=extraction_failed,
    )


# ── batch download ───────────────────────────────────────────────────


@dataclass
class BatchSummary:
    total: int = 0
    ok: int = 0
    failed: int = 0
    skipped: int = 0
    aborted: bool = False
    results: list[DownloadResult] = field(default_factory=list)

    @property
    def downloaded(self) -> int:
        return self.ok - self.skipped


def download_range(
    client: RjssClient,
    doctype: str,
    names: Iterable[str],
    fmt: str,
    out_dir: Path,
    delay_ms: int = DEFAULT_DELAY_MS,
    no_letterhead: bool = False,
    overwrite: bool = False,
    filename_template: str = DEFAULT_FILENAME_TEMPLATE,
    customer_regex: str | None = None,
    on_progress: Callable[[int, int, DownloadResult], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> BatchSummary:
    names_list = list(names)
    total = len(names_list)
    summary = BatchSummary(total=total)

    if delay_ms < 0:
        delay_ms = 0

    for i, name in enumerate(names_list, 1):
        if should_stop and should_stop():
            summary.aborted = True
            break

        result = download_one(
            client=client,
            doctype=doctype,
            name=name,
            fmt=fmt,
            out_dir=out_dir,
            no_letterhead=no_letterhead,
            overwrite=overwrite,
            filename_template=filename_template,
            customer_regex=customer_regex,
        )

        summary.results.append(result)
        if result.ok and result.skipped:
            summary.skipped += 1
            summary.ok += 1
        elif result.ok:
            summary.ok += 1
        else:
            summary.failed += 1

        if on_progress:
            try:
                on_progress(i, total, result)
            except Exception:
                pass

        if delay_ms > 0 and i < total:
            if should_stop and should_stop():
                summary.aborted = True
                break
            time.sleep(delay_ms / 1000.0)

    return summary
```
## src/spjss/keyring_helper.py

```python

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
```
## src/spjss/presets.py

```python

from __future__ import annotations

import json
import re

from . import config as cfgmod

PRESETS_PATH = cfgmod.CONFIG_DIR / "presets.json"

_FIELDS = (
    "doctype",
    "print_format",
    "filename_template",
    "output_dir",
    "delay_ms",
    "no_letterhead",
    "overwrite",
)

_NAME_RE = re.compile(r"^[A-Za-z0-9 _.\-]{1,60}$")


def _load_raw() -> dict:
    if not PRESETS_PATH.is_file():
        return {}
    try:
        data = json.loads(PRESETS_PATH.read_text("utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _write_raw(data: dict) -> None:
    cfgmod.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PRESETS_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def list_names() -> list[str]:
    return sorted(_load_raw().keys())


def get(name: str) -> dict | None:
    data = _load_raw()
    entry = data.get(name)
    if not isinstance(entry, dict):
        return None
    return {k: entry.get(k) for k in _FIELDS if k in entry}


def save(name: str, values: dict) -> None:
    name = name.strip()
    if not _NAME_RE.match(name):
        raise ValueError(
            "Preset name must be 1-60 characters, letters, digits, "
            "spaces, dot, dash, or underscore."
        )
    data = _load_raw()
    data[name] = {k: values.get(k) for k in _FIELDS}
    _write_raw(data)


def delete(name: str) -> bool:
    data = _load_raw()
    if name not in data:
        return False
    del data[name]
    _write_raw(data)
    return True
```
## src/spjss/update_check.py

```python
import json
import urllib.request

from . import __version__

RELEASES_API = "https://api.github.com/repos/mroczect/librjss/releases/latest"


def check() -> str | None:
    """Return latest version string if newer than current, else None."""
    try:
        req = urllib.request.Request(
            RELEASES_API,
            headers={"User-Agent": f"spjss/{__version__}"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.load(r)
    except Exception:
        return None
    latest = (data.get("tag_name") or "").lstrip("v")
    if not latest:
        return None
    if _newer(latest, __version__):
        return latest
    return None


def _newer(a: str, b: str) -> bool:
    def parts(s):
        out = []
        for x in s.split("."):
            try:
                out.append(int(x))
            except ValueError:
                out.append(0)
        return out

    return parts(a) > parts(b)
```
