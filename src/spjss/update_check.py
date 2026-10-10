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
