from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load(name: str) -> str:
    p = DATA_DIR / name
    if not p.is_file():
        return f"(berkas {name} tidak ditemukan)"
    return p.read_text("utf-8")
