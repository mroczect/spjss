
from __future__ import annotations

import io
import json
import re
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ._native import JssError, RjssClient


try:
    from pypdf import PdfReader as _PdfReader  # type: ignore
except ImportError:
    try:
        from PyPDF2 import PdfReader as _PdfReader  # type: ignore
    except ImportError:
        _PdfReader = None  # type: ignore



DEFAULT_PRINT_FORMAT = "Standard"
DEFAULT_MAX_RANGE = 1000
DEFAULT_DELAY_MS = 300
DEFAULT_FILENAME_TEMPLATE = "{name}"
MAX_FILENAME_LEN = 200
PDF_MAGIC = b"%PDF-"
NAME_CACHE_FILE = ".spjss_names.json"




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



_STRING_FORMATTER = __import__("string").Formatter()


def _template_uses_customer(template: str) -> bool:
    if not template:
        return False
    try:
        for _, field_name, _, _ in _STRING_FORMATTER.parse(template):
            if field_name == "customer":
                return True
    except Exception:
        pass
    return False


def _render_filename(
    template: str,
    name: str,
    customer: str | None = None,
) -> str:
    tmpl = (template or "").strip() or DEFAULT_FILENAME_TEMPLATE
    values = {
        "name": name,
        "customer": customer if customer is not None else "",
    }
    try:
        return tmpl.format(**values)
    except (KeyError, IndexError, ValueError) as e:
        raise ValueError(f"template nama file tidak valid: {tmpl!r} ({e})")



_DEFAULT_CUSTOMER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"Bapak\s*/\s*Ibu\s+"
        r"([A-Z][A-Za-z\s\.'\-]{1,80}?)"
        r"(?=\s*(?:Jl\.|JL\.|Perihal|PERIHAL|Alamat|ALAMAT|$))",
        re.MULTILINE,
    ),
    re.compile(
        r"Bapak\s*/\s*Ibu\s+([^\n\r]{1,80})",
        re.IGNORECASE,
    ),
)


def _extract_pdf_text(pdf_bytes: bytes) -> str | None:
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
            cleaned = re.sub(r"\s+", " ", cleaned)
            if cleaned:
                return cleaned
    return None




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
