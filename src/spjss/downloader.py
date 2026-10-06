"""
Batch downloader for Frappe print-format PDFs.

Public API:
    expand_range(start, end, max_items=1000) -> list[str]
    download_one(client, doctype, name, fmt, out_dir, ...) -> DownloadResult
    download_range(client, doctype, names, fmt, out_dir, ...) -> list[DownloadResult]
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ._native import JssError, RjssClient

# ── constants ────────────────────────────────────────────────────────

DEFAULT_PRINT_FORMAT = "Standard"
DEFAULT_MAX_RANGE = 1000
DEFAULT_DELAY_MS = 300
MAX_FILENAME_LEN = 200
PDF_MAGIC = b"%PDF-"


# ── result ───────────────────────────────────────────────────────────


@dataclass
class DownloadResult:
    name: str
    ok: bool
    path: Path | None = None
    error: str | None = None
    bytes: int = 0
    skipped: bool = False

    @property
    def failed(self) -> bool:
        return not self.ok and not self.skipped

    def __str__(self) -> str:
        if self.ok and self.skipped:
            return f"{self.name}: skip (sudah ada)"
        if self.ok:
            kb = self.bytes / 1024.0
            return f"{self.name}: ok ({kb:.1f} KB)"
        return f"{self.name}: gagal ({self.error})"


# ── range expansion ──────────────────────────────────────────────────


def _split_id(value: str) -> tuple[str, int]:
    """Split an identifier like 'JD4521' into ('JD', 4521)."""
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
    """Expand 'JD4521'..'JD4546' into an inclusive list of identifiers.

    Rules:
      - both start and end must be non-empty
      - both must use the same letter prefix
      - the numeric part of start must be <= the numeric part of end
      - the total count must not exceed max_items

    Returns the list in ascending numeric order, zero-padded to the
    width of the larger number so the identifiers look uniform.
    """
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
    """Return a filesystem-safe stem for a document name.

    Removes path separators, control characters, and other characters
    that are illegal on Windows or dangerous on POSIX. Enforces a
    maximum length so we never exceed NAME_MAX on any platform.
    """
    cleaned: list[str] = []
    for ch in name:
        if ch in _FORBIDDEN_CHARS or ch in _CONTROL_CHARS:
            cleaned.append("_")
        else:
            cleaned.append(ch)

    stem = "".join(cleaned).strip().rstrip(".")

    if not stem:
        raise ValueError(f"nama dokumen tidak valid: {name!r}")

    # Windows reserved names
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


# ── single download ──────────────────────────────────────────────────


def _looks_like_pdf(data: bytes) -> bool:
    return len(data) >= len(PDF_MAGIC) and data.startswith(PDF_MAGIC)


def _error_snippet(data: bytes, limit: int = 120) -> str:
    """Decode the first bytes of a non-PDF response for the log."""
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


def download_one(
    client: RjssClient,
    doctype: str,
    name: str,
    fmt: str,
    out_dir: Path,
    no_letterhead: bool = False,
    overwrite: bool = False,
) -> DownloadResult:
    """Download a single document as PDF.

    Returns a DownloadResult. Never raises for network or server
    errors: those are captured and returned with ok=False.
    Raises ValueError only for invalid arguments that the caller
    should have caught before calling.
    """
    if not doctype or not doctype.strip():
        raise ValueError("doctype tidak boleh kosong")
    if not name or not name.strip():
        raise ValueError("name tidak boleh kosong")

    out_dir = Path(out_dir)

    # Frappe requires a format parameter. Empty means "use the server
    # default", but the FFI signature insists on a non-empty string,
    # so we pass the conventional default name.
    fmt_effective = fmt.strip() if fmt else DEFAULT_PRINT_FORMAT

    # resolve the destination path
    try:
        stem = _safe_filename(name)
    except ValueError as e:
        return DownloadResult(name=name, ok=False, error=str(e))

    dest = out_dir / f"{stem}.pdf"

    # skip if already present and overwrite is off
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

    # fetch from server
    try:
        data = client.download_pdf_kartu_piutang(
            doctype, name, fmt_effective, no_letterhead
        )
    except JssError as e:
        return DownloadResult(name=name, ok=False, error=f"{e}")
    except Exception as e:
        return DownloadResult(name=name, ok=False, error=f"unexpected: {e!r}")

    # sanity check the payload
    if not data:
        return DownloadResult(name=name, ok=False, error="response kosong")
    if not _looks_like_pdf(data):
        return DownloadResult(
            name=name,
            ok=False,
            error=f"bukan PDF (server mengembalikan): {_error_snippet(data)}",
        )

    # write to disk
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return DownloadResult(
            name=name, ok=False, error=f"gagal buat folder {out_dir}: {e}"
        )

    # write to a temp file first, then rename, so a crash mid-write
    # never leaves a truncated PDF at the final destination
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        tmp.write_bytes(data)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return DownloadResult(
            name=name, ok=False, error=f"gagal tulis {dest.name}: {e}"
        )

    try:
        tmp.replace(dest)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return DownloadResult(name=name, ok=False, error=f"gagal pindahkan file: {e}")

    return DownloadResult(
        name=name,
        ok=True,
        path=dest,
        bytes=len(data),
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
        """Files actually written to disk this run."""
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
    on_progress: Callable[[int, int, DownloadResult], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> BatchSummary:
    """Download every name in the iterable.

    Calls on_progress(i, total, result) after each attempt.
    Stops early if should_stop() returns True, marking the summary
    as aborted. Never raises for individual failures.
    """
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

        # do not sleep after the last item, and do not sleep if the
        # caller has already asked us to stop
        if delay_ms > 0 and i < total:
            if should_stop and should_stop():
                summary.aborted = True
                break
            time.sleep(delay_ms / 1000.0)

    return summary
