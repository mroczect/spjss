# spjss

Batch PDF downloader for Frappe / ERPNext. Desktop app, Python + tkinter.

Give it a range of document names (e.g. `JD4521` to `JD4546`) and it
downloads each one as PDF from the server.

---

## What it does

- Logs in to a Frappe / ERPNext server with email + password
- Downloads PDFs for a range of documents in one batch
- Names each file from a template — `{name}`, `{customer}`, or both
- Extracts the customer name from the PDF text (optional)
- Shows progress, ETA, and a live log
- Auto-checks for updates from GitHub Releases

Only calls `frappe.utils.print_format.download_pdf`. No writes, no
submissions, no deletes.

---

## Install

### Windows

Download `spjss-setup-<version>.exe` from the
[latest release](https://github.com/mroczect/spjss/releases/latest)
and run it. No Python required.

### From source

Needs Python 3.10+ with tkinter and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/mroczect/spjss
cd spjss
uv sync
uv run spjss
```

The native library (`librjss_ffi`) must be present in
`src/spjss/_native/` — see below.

---

## Native library

The app uses `librjss-ffi`, a Rust library with a C ABI. Grab the build
for your platform from the
[librjss releases](https://github.com/mroczect/librjss/releases).

| OS      | File name in `src/spjss/_native/` |
| ------- | --------------------------------- |
| Linux   | `liblibrjss_ffi.so`               |
| macOS   | `liblibrjss_ffi.dylib`            |
| Windows | `librjss_ffi.dll`                 |

For the Windows installer this is handled automatically. For source
builds, extract the archive and drop the shared library into
`src/spjss/_native/`.

The library can also be pointed to at runtime with the `LIBRJSS_FFI`
environment variable.

---

## Usage

First run shows welcome, privacy, terms, and third-party pages. After
that it goes straight to login.

1. **Sign in** — server URL, email, password. Optionally save the password
   with the OS keyring.
2. **Download** — fill in:
   - **DocType** — e.g. `Surat Peringatan KSP`
   - **Print Format** — leave blank for the server default, or click
     **Detect** to query available formats for that DocType
   - **Filename** — template for output file names
   - **Start ID** / **End ID** — e.g. `JD4521` and `JD4546`
   - **Output folder**
   - **Delay** between requests, in ms (default 300)
   - Optional: no letterhead, overwrite existing files, open folder when
     finished, notify when finished
3. Click **Start**.

### Filename template

Placeholders:

| Placeholder  | Value                                                  |
| ------------ | ------------------------------------------------------ |
| `{name}`     | document identifier, e.g. `JD4521`                     |
| `{customer}` | customer name extracted from the PDF, e.g. `SUHARTINA` |

Examples:

```
{name}                             → JD4521.pdf
Surat Peringatan {name}            → Surat Peringatan JD4521.pdf
{name} {customer}                  → JD4521 SUHARTINA.pdf
```

`{customer}` requires the optional `pypdf` dependency (installed by
default) and works by reading the "Bapak/ Ibu <NAME>" line from the PDF.
A custom regex can be configured in `config.json` under `customer_regex`.

Extracted customer names are cached in `.spjss_names.json` inside the
output folder, so the PDF isn't re-parsed on subsequent runs.

---

## Configuration

After a successful run, settings are saved to:

| OS      | Path                          |
| ------- | ----------------------------- |
| Linux   | `~/.config/spjss/config.json` |
| macOS   | `~/.config/spjss/config.json` |
| Windows | `%APPDATA%\spjss\config.json` |

Saved: server URL, email, DocType, print format, filename template,
output folder, delay, checkbox states.

Not saved: password (unless keyring is enabled), start ID, end ID.

Delete the file to reset:

```bash
# Linux / macOS
rm ~/.config/spjss/config.json
```

```powershell
# Windows
Remove-Item "$env:APPDATA\spjss\config.json"
```

---

## Presets

Save the current form values under a name with **Save** next to the
preset dropdown. Load later with **Load**. Delete with **Delete**.
Stored in `presets.json` next to `config.json`.

---

## Updates

spjss checks GitHub Releases once per session and offers to download and
install newer versions. The check can also be triggered manually from
**Help → Check for updates…**.

To skip a specific version, click **Lewati versi ini** in the update
dialog. Clear `_skipped_version` in `config.json` to see it again.

---

## Build

### Windows installer

```bat
build.bat
```

Produces `dist\spjss.exe` and `installer_out\spjss-setup-<version>.exe`.

### Linux / macOS binary

```bash
./build.sh
```

Produces `dist/spjss`. Inno Setup is Windows-only, so the installer step
is skipped unless `iscc` or `wine` is available.

### Via GitHub Actions

Push a tag:

```bash
git tag v0.3.0
git push origin v0.3.0
```

The `release` workflow builds `spjss.exe` and `spjss-setup-<version>.exe`,
attaches both to the GitHub release, and syncs the version into
`pyproject.toml`, `src/spjss/__init__.py`, and `installer.iss`.

## Uninstall Windows

run this command to clean the program

```ps1
irm https://raw.githubusercontent.com/mroczect/spjss/master/uninstall.ps1 | iex
```

---

## Requirements

- Python 3.10+ (with tkinter)
- `keyring` — optional at runtime, for saving passwords
- `pypdf` — optional at runtime, for `{customer}` in filename templates
- Rust 1.85+ — only if building `librjss-ffi` from source

Runtime deps are declared in `pyproject.toml` and installed by `uv sync`.

---

## License

MIT. See `src/spjss/data/license.txt` for the full text. The app also
bundles a privacy notice and terms of use, shown on first run.
