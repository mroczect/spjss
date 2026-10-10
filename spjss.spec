# spjss.spec
# build: pyinstaller spjss.spec --clean --noconfirm

import platform
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).resolve()
PKG = ROOT / "src" / "spjss"


# ── data files ───────────────────────────────────────────────────────
# Collect manually. Do NOT call collect_data_files("spjss") — that
# would import spjss, which loads the native DLL at import time.

data_dir = PKG / "data"
datas = [
    (str(p), "spjss/data")
    for p in data_dir.glob("*.txt")
]
if not datas:
    raise SystemExit(f"no data files found in {data_dir}")


# ── native library ───────────────────────────────────────────────────

def _native_filename() -> str:
    system = platform.system()
    if system == "Windows":
        return "librjss_ffi.dll"
    if system == "Darwin":
        return "liblibrjss_ffi.dylib"
    return "liblibrjss_ffi.so"


def _target_triple() -> str | None:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Windows" and machine in ("amd64", "x86_64"):
        return "x86_64-pc-windows-msvc"
    if system == "Windows" and machine in ("x86", "i386", "i686"):
        return "i686-pc-windows-msvc"
    if system == "Darwin" and machine == "arm64":
        return "aarch64-apple-darwin"
    if system == "Darwin" and machine == "x86_64":
        return "x86_64-apple-darwin"
    if system == "Linux" and machine == "x86_64":
        return "x86_64-unknown-linux-gnu"
    if system == "Linux" and machine in ("aarch64", "arm64"):
        return "aarch64-unknown-linux-gnu"
    return None


def _find_native() -> Path:
    here = PKG / "_native"
    name = _native_filename()

    candidates = [here / name]
    triple = _target_triple()
    if triple:
        candidates.append(here / triple / name)
    # cargo target dir fallback
    candidates.append(ROOT / "target" / "release" / name)
    if triple:
        candidates.append(ROOT / "target" / triple / "release" / name)

    for p in candidates:
        if p.is_file():
            return p

    listing = "\n  ".join(str(p) for p in candidates)
    raise SystemExit(
        f"native library not found. Looked in:\n  {listing}\n"
        f"Build librjss-ffi or drop the shared library into "
        f"{here}."
    )


native = _find_native()
binaries = [(str(native), "spjss/_native")]


# ── hidden imports ───────────────────────────────────────────────────
# keyring and pypdf are imported inside try/except in the source, so
# PyInstaller cannot see them by static analysis.

hiddenimports = [
    "pypdf",
    "keyring",
]
hiddenimports += collect_submodules("keyring.backends")


# ── icon ─────────────────────────────────────────────────────────────

icon_path = ROOT / "assets" / "spjss.ico"
icon = str(icon_path) if icon_path.is_file() else None


# ── build ────────────────────────────────────────────────────────────

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="spjss",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                       # UPX corrupts native DLLs, keep off
    runtime_tmpdir=None,
    console=False,                   # set True to see tracebacks
    disable_windowed_traceback=False,
    icon=icon,
)
