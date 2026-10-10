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
    "_skipped_version": "",
    "last_update_check": 0,
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
