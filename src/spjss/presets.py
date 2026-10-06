"""Named download presets, stored as JSON next to config.json."""

from __future__ import annotations

import json
import re

from . import config as cfgmod

PRESETS_PATH = cfgmod.CONFIG_DIR / "presets.json"

_FIELDS = (
    "doctype",
    "print_format",
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
