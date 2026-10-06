# spjss

Batch PDF downloader for Frappe / ERPNext. Desktop app, Python + tkinter.

Give it a range of document names (e.g. `JD4521` to `JD4546`), it downloads
each one as PDF from the server.

---

## What it does

- Logs in to a Frappe / ERPNext server with email + password
- Downloads PDFs for a range of documents in one batch
- Saves each file as `<ID>.pdf` to a folder you choose
- Shows progress, ETA, and a log

It only calls `frappe.utils.print_format.download_pdf`. No writes, no
submissions, no deletes.

---

## Install

### Windows

Download `spjss-setup-0.1.0.exe` from the latest release and run it.

### Linux / macOS

Needs Python 3.10+ with tkinter.

```bash
git clone https://github.com/mroczect/spjss
cd spjss

# install native library first (see below)
cp liblibrjss_ffi.so src/spjss/_native/

pip install -e ".[keyring]"
spjss
```

Or without installing:

```bash
PYTHONPATH=src python -m spjss
```

---

## Native library

The app uses `librjss-ffi`, a Rust library with a C ABI. Download the
build for your platform from the librjss release page:

https://github.com/mroczect/librjss/releases

Pick the file that matches your OS:

| OS      | File                                | Put in               |
| ------- | ----------------------------------- | -------------------- |
| Linux   | `librjss-ffi-*-linux-x86_64.tar.gz` | `src/spjss/_native/` |
| macOS   | `librjss-ffi-*-macos-arm64.tar.gz`  | `src/spjss/_native/` |
| Windows | `librjss-ffi-*-windows-x86_64.zip`  | `src/spjss/_native/` |

Extract and copy the shared library into `src/spjss/_native/`:

- Linux: `liblibrjss_ffi.so`
- macOS: `liblibrjss_ffi.dylib`
- Windows: `librjss_ffi.dll`

---

## Usage

First run shows the welcome, privacy, terms, and third-party pages. After
that, it goes straight to login.

1. **Sign in** — server URL, email, password. Optionally save the password
   with the OS keyring.
2. **Download** — fill in:
   - DocType (e.g. `Surat Peringatan KSP`)
   - Print Format (leave blank to use the server default)
   - Start ID and End ID (e.g. `JD4521` and `JD4546`)
   - Output folder
   - Delay between requests (default 300 ms)
   - Optionally: no letterhead, overwrite existing files
3. Click **Start**.

If you don't know the print format name, click **Detect** — it queries the
server for available print formats for that DocType.

---

## Configuration

After a successful run, settings are saved to:

```
Linux    ~/.config/spjss/config.json
macOS    ~/.config/spjss/config.json
Windows  %APPDATA%\spjss\config.json
```

Saved: server URL, email, DocType, print format, output folder, delay,
and the checkboxes.

Not saved: password (unless you enable keyring), start ID, end ID.

Delete the file to reset:

```bash
rm ~/.config/spjss/config.json
```

---

## Presets

Save the current form values under a name with the **Save** button next to
the preset dropdown. Load later with **Load**. Stored in
`presets.json` next to `config.json`.

---

## Build

### Windows installer (via GitHub Actions)

Push a tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The `release` workflow builds `spjss.exe` and `spjss-setup-0.1.0.exe` and
attaches them to the GitHub release.

### Local build (Linux, for testing)

```bash
cargo build -p librjss-ffi --release   # in the librjss repo
cp target/release/liblibrjss_ffi.so /path/to/spjss/src/spjss/_native/

cd /path/to/spjss
PYTHONPATH=src python -m spjss
```

---

## Requirements

- Python 3.10+ (with tkinter)
- Rust 1.85+ (only for building librjss-ffi)
- `keyring` (optional, for saving passwords)

---

## License

MIT
