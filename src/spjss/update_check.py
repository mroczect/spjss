
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from . import __version__


GITHUB_OWNER = "mroczect"
GITHUB_REPO = "librjss"
RELEASES_API = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)
USER_AGENT = f"spjss/{__version__}"
CHUNK_SIZE = 64 * 1024
META_TIMEOUT = 6
DOWNLOAD_TIMEOUT = 180




@dataclass(frozen=True)
class UpdateInfo:
    version: str  
    tag: str  
    html_url: str  
    notes: str  
    published_at: str  
    asset_url: str | None  
    asset_name: str | None  
    asset_size: int  

    @property
    def has_installer(self) -> bool:
        return bool(self.asset_url)


@dataclass
class CheckResult:

    info: UpdateInfo | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @property
    def has_update(self) -> bool:
        return self.info is not None




_NUM_RE = re.compile(r"\d+")


def _parse_version(v: str) -> tuple[int, ...]:
    parts = tuple(int(x) for x in _NUM_RE.findall(v))
    return parts or (0,)


def is_newer(candidate: str, current: str) -> bool:
    return _parse_version(candidate) > _parse_version(current)




def check(current: str | None = None) -> CheckResult:
    current = current or __version__
    try:
        req = urllib.request.Request(
            RELEASES_API,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(req, timeout=META_TIMEOUT) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return CheckResult(error="Repo atau rilis tidak ditemukan (404).")
        return CheckResult(error=f"HTTP {e.code}")
    except urllib.error.URLError as e:
        return CheckResult(error=f"Gagal konek: {e.reason}")
    except (OSError, ValueError, TimeoutError) as e:
        return CheckResult(error=f"Gagal: {e!r}")

    tag = (data.get("tag_name") or "").strip()
    if not tag:
        return CheckResult(error="Rilis tidak punya tag.")

    latest = tag.lstrip("vV")
    if not is_newer(latest, current):
        return CheckResult()  

    asset = _select_asset(data.get("assets") or [])
    return CheckResult(
        info=UpdateInfo(
            version=latest,
            tag=tag,
            html_url=data.get("html_url") or "",
            notes=(data.get("body") or "").strip(),
            published_at=data.get("published_at") or "",
            asset_url=(asset or {}).get("browser_download_url"),
            asset_name=(asset or {}).get("name"),
            asset_size=int((asset or {}).get("size") or 0),
        )
    )


def _select_asset(assets: list[dict]) -> dict | None:
    system = platform.system()
    machine = platform.machine().lower()

    def _names_lower():
        return [(a, (a.get("name") or "").lower()) for a in assets]

    if system == "Windows":
        for a, name in _names_lower():
            if name.endswith(".exe") and ("setup" in name or "installer" in name):
                return a
        for a, name in _names_lower():
            if name.endswith(".exe"):
                return a

    elif system == "Darwin":
        for a, name in _names_lower():
            if name.endswith(".dmg") and machine in name:
                return a
        for a, name in _names_lower():
            if name.endswith(".dmg"):
                return a

    elif system == "Linux":
        for a, name in _names_lower():
            if name.endswith(".appimage") and machine in name:
                return a
        for a, name in _names_lower():
            if name.endswith(".appimage"):
                return a

    return None




def download_installer(
    info: UpdateInfo,
    dest_dir: Path | None = None,
    on_progress: Callable[[int, int], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> Path:
    if not info.asset_url:
        raise RuntimeError("Rilis ini tidak menyediakan installer untuk platform kamu.")

    dest_dir = Path(dest_dir or tempfile.gettempdir())
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = info.asset_name or f"spjss-setup-{info.version}"
    dst = dest_dir / filename
    tmp = dst.with_suffix(dst.suffix + ".part")

    req = urllib.request.Request(
        info.asset_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/octet-stream",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as r:
            total = int(r.headers.get("Content-Length") or info.asset_size or 0)
            got = 0
            with open(tmp, "wb") as f:
                while True:
                    if should_stop and should_stop():
                        raise RuntimeError("dibatalkan oleh pengguna")
                    chunk = r.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if on_progress:
                        try:
                            on_progress(got, total)
                        except Exception:
                            pass
        tmp.replace(dst)
    except BaseException:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise

    return dst




def launch_installer(installer: Path) -> None:
    path = str(installer)
    system = platform.system()

    if system == "Windows":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0)
        subprocess.Popen(
            [path, "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"],
            close_fds=True,
            creationflags=flags,
        )
    elif system == "Darwin":
        subprocess.Popen(["open", path], close_fds=True)
    else:
        p = Path(path)
        if p.suffix.lower() == ".appimage":
            try:
                os.chmod(p, 0o755)
            except OSError:
                pass
            subprocess.Popen([path], close_fds=True)
        else:
            subprocess.Popen(["xdg-open", path], close_fds=True)
