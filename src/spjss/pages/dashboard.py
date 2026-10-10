import json
import os
import platform
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from .. import config as cfgmod
from .. import keyring_helper as keyring
from .. import presets, worker
from .._native import RjssClient
from ..downloader import (
    DEFAULT_FILENAME_TEMPLATE,
    download_range,
    expand_range,
)
from .base import Page


class DashboardPage(Page):
    title = "Download"
    step_label = "Download"
    next_label = "Exit"
    show_back = False
    show_next = True

    def build(self) -> None:
        self._running = False
        self._failed: list[str] = []
        self._last_summary = None
        self._run_started_at = 0.0
        self._client_for_test = None

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 6))

        ttk.Label(bar, text="Preset:").pack(side="left")
        self.cb_preset = ttk.Combobox(bar, width=24, state="readonly")
        self.cb_preset.pack(side="left", padx=6)
        self.cb_preset.bind("<<ComboboxSelected>>", self._on_preset_selected)

        ttk.Button(bar, text="Load", command=self._on_preset_load).pack(
            side="left", padx=2
        )
        ttk.Button(bar, text="Save", command=self._on_preset_save).pack(
            side="left", padx=2
        )
        ttk.Button(bar, text="Delete", command=self._on_preset_delete).pack(
            side="left", padx=2
        )

        form = ttk.LabelFrame(self, text="Settings", padding=10)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="DocType").grid(row=0, column=0, sticky="w", pady=4)
        self.e_doctype = ttk.Entry(form)
        self.e_doctype.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(form, text="Print Format").grid(row=1, column=0, sticky="w", pady=4)
        self.cb_format = ttk.Combobox(form)
        self.cb_format.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        ttk.Button(form, text="Detect", command=self._on_detect_formats).grid(
            row=1, column=2, padx=8
        )

        ttk.Label(form, text="Filename").grid(row=2, column=0, sticky="w", pady=4)
        self.e_filename = ttk.Entry(form)
        self.e_filename.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(
            form,
            text="contoh: Surat Peringatan {name}  |  {customer}",
        ).grid(row=2, column=2, sticky="w")

        ttk.Label(form, text="Start ID").grid(row=3, column=0, sticky="w", pady=4)
        self.e_start = ttk.Entry(form)
        self.e_start.grid(row=3, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(form, text="e.g. JD4521").grid(row=3, column=2, sticky="w")

        ttk.Label(form, text="End ID").grid(row=4, column=0, sticky="w", pady=4)
        self.e_end = ttk.Entry(form)
        self.e_end.grid(row=4, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(form, text="e.g. JD4546").grid(row=4, column=2, sticky="w")

        ttk.Label(form, text="Output folder").grid(row=5, column=0, sticky="w", pady=4)
        self.e_out = ttk.Entry(form)
        self.e_out.grid(row=5, column=1, sticky="ew", padx=8, pady=4)
        ttk.Button(form, text="Browse...", command=self._pick_dir).grid(
            row=5, column=2, padx=8
        )

        ttk.Label(form, text="Delay (ms)").grid(row=6, column=0, sticky="w", pady=4)
        self.e_delay = ttk.Entry(form, width=10)
        self.e_delay.grid(row=6, column=1, sticky="w", padx=8, pady=4)

        self.v_no_letterhead = ttk.Checkbutton(form, text="No letterhead")
        self.v_no_letterhead.grid(row=7, column=1, sticky="w", padx=8, pady=2)

        self.v_overwrite = ttk.Checkbutton(form, text="Overwrite existing files")
        self.v_overwrite.grid(row=8, column=1, sticky="w", padx=8, pady=2)

        self.v_open_after = ttk.Checkbutton(
            form, text="Open output folder when finished"
        )
        self.v_open_after.grid(row=9, column=1, sticky="w", padx=8, pady=2)

        self.v_notify = ttk.Checkbutton(form, text="Notify when finished")
        self.v_notify.grid(row=10, column=1, sticky="w", padx=8, pady=2)

        self.lbl_form_error = ttk.Label(
            form, text="", foreground="#b00020", wraplength=600
        )
        self.lbl_form_error.grid(row=11, column=1, sticky="w", padx=8, pady=(4, 0))

        act = ttk.Frame(self, padding=(0, 8))
        act.pack(fill="x")

        self.btn_start = ttk.Button(act, text="Start", command=self._on_start)
        self.btn_start.pack(side="left")

        self.btn_stop = ttk.Button(
            act, text="Stop", command=self._on_stop, state="disabled"
        )
        self.btn_stop.pack(side="left", padx=6)

        self.btn_test = ttk.Button(act, text="Test connection", command=self._on_test)
        self.btn_test.pack(side="left", padx=6)

        self.btn_retry = ttk.Button(
            act,
            text="Retry failed",
            command=self._on_retry_failed,
            state="disabled",
        )
        self.btn_retry.pack(side="left", padx=6)

        self.btn_open = ttk.Button(
            act,
            text="Open folder",
            command=self._on_open_folder,
            state="disabled",
        )
        self.btn_open.pack(side="left", padx=6)

        self.btn_export = ttk.Button(
            act, text="Export log", command=self._on_export_log
        )
        self.btn_export.pack(side="left", padx=6)

        self.btn_logout = ttk.Button(act, text="Sign out", command=self._on_logout)
        self.btn_logout.pack(side="right")

        self.lbl_status = ttk.Label(act, text="Ready")
        self.lbl_status.pack(side="right", padx=12)

        self.pbar = ttk.Progressbar(self, mode="determinate")
        self.pbar.pack(fill="x", pady=(0, 4))

        self.lbl_eta = ttk.Label(self, text="")
        self.lbl_eta.pack(anchor="w", pady=(0, 6))

        logf = ttk.LabelFrame(self, text="Activity log", padding=4)
        logf.pack(fill="both", expand=True)

        self.txt = tk.Text(
            logf,
            wrap="none",
            height=14,
            font=("Courier", 9),
            borderwidth=1,
            relief="solid",
        )
        sb = ttk.Scrollbar(logf, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt.pack(side="left", fill="both", expand=True)


    def on_enter(self) -> None:
        s = self.app.state
        self._prefill(self.e_doctype, s.get("doctype", ""))
        self._prefill(self.cb_format, s.get("print_format", ""))
        self._prefill(
            self.e_filename,
            s.get("filename_template", DEFAULT_FILENAME_TEMPLATE),
        )
        if not self.e_filename.get():
            self.e_filename.insert(0, DEFAULT_FILENAME_TEMPLATE)
        self._prefill(self.e_out, s.get("output_dir", ""))
        self._prefill(self.e_delay, str(s.get("delay_ms", "300")))
        if not self.e_delay.get():
            self.e_delay.insert(0, "300")

        if s.get("no_letterhead"):
            self.v_no_letterhead.state(["selected"])
        if s.get("overwrite"):
            self.v_overwrite.state(["selected"])
        if s.get("open_folder_after", True):
            self.v_open_after.state(["selected"])
        if s.get("notify_on_finish", True):
            self.v_notify.state(["selected"])

        self._refresh_presets()

        user = s.get("email", "")
        self._log(f"Signed in as: {user}" if user else "(not signed in)")

    def on_next(self):
        self.app._on_close()
        return None

    def on_leave(self) -> bool:
        if self._running:
            if not messagebox.askyesno("Exit", "Download is running. Stop and exit?"):
                return False
            worker.request_stop()
        return True

    @staticmethod
    def _prefill(widget, value: str) -> None:
        if not value:
            return
        if hasattr(widget, "set"):
            widget.set(value)
        elif not widget.get():
            widget.insert(0, value)


    def _refresh_presets(self) -> None:
        names = presets.list_names()
        self.cb_preset["values"] = names
        if names and not self.cb_preset.get():
            self.cb_preset.current(0)

    def _current_values(self) -> dict:
        return {
            "doctype": self.e_doctype.get().strip(),
            "print_format": self.cb_format.get().strip(),
            "filename_template": self.e_filename.get().strip()
            or DEFAULT_FILENAME_TEMPLATE,
            "output_dir": self.e_out.get().strip(),
            "delay_ms": self.e_delay.get().strip() or "300",
            "no_letterhead": bool(self.v_no_letterhead.instate(["selected"])),
            "overwrite": bool(self.v_overwrite.instate(["selected"])),
        }

    def _apply_values(self, values: dict) -> None:
        if values.get("doctype") is not None:
            self.e_doctype.delete(0, "end")
            self.e_doctype.insert(0, values["doctype"] or "")
        if values.get("print_format") is not None:
            self.cb_format.set(values["print_format"] or "")
        if values.get("filename_template") is not None:
            self.e_filename.delete(0, "end")
            self.e_filename.insert(
                0, values["filename_template"] or DEFAULT_FILENAME_TEMPLATE
            )
        if values.get("output_dir") is not None:
            self.e_out.delete(0, "end")
            self.e_out.insert(0, values["output_dir"] or "")
        if values.get("delay_ms") is not None:
            self.e_delay.delete(0, "end")
            self.e_delay.insert(0, str(values["delay_ms"]))
        self._apply_checkbox(self.v_no_letterhead, values.get("no_letterhead"))
        self._apply_checkbox(self.v_overwrite, values.get("overwrite"))

    @staticmethod
    def _apply_checkbox(var, value) -> None:
        if value is None:
            return
        var.state(["selected"] if value else ["!selected"])

    def _on_preset_selected(self, _event=None) -> None:
        self._on_preset_load()

    def _on_preset_load(self) -> None:
        name = self.cb_preset.get().strip()
        if not name:
            return
        values = presets.get(name)
        if values is None:
            messagebox.showerror("Preset", f"Preset {name!r} not found.")
            self._refresh_presets()
            return
        self._apply_values(values)
        self._log(f"Preset loaded: {name}")

    def _on_preset_save(self) -> None:
        name = simpledialog.askstring(
            "Save preset",
            "Preset name:",
            initialvalue=self.cb_preset.get().strip(),
            parent=self,
        )
        if not name:
            return
        try:
            presets.save(name, self._current_values())
        except ValueError as e:
            messagebox.showerror("Preset", str(e))
            return
        self._refresh_presets()
        self.cb_preset.set(name.strip())
        self._log(f"Preset saved: {name.strip()}")

    def _on_preset_delete(self) -> None:
        name = self.cb_preset.get().strip()
        if not name:
            return
        if not messagebox.askyesno("Preset", f"Delete preset {name!r}?"):
            return
        if presets.delete(name):
            self._log(f"Preset deleted: {name}")
            self.cb_preset.set("")
            self._refresh_presets()


    def _pick_dir(self) -> None:
        cur = self.e_out.get().strip() or str(Path.home())
        d = filedialog.askdirectory(initialdir=cur)
        if d:
            self.e_out.delete(0, "end")
            self.e_out.insert(0, d)

    def _collect(self) -> dict | None:
        s = dict(self.app.state)
        doctype = self.e_doctype.get().strip()
        fmt = self.cb_format.get().strip()
        filename_template = self.e_filename.get().strip() or DEFAULT_FILENAME_TEMPLATE
        start = self.e_start.get().strip().upper()
        end = self.e_end.get().strip().upper()
        out = self.e_out.get().strip()
        delay_raw = self.e_delay.get().strip() or "300"

        if not doctype:
            self.lbl_form_error.config(text="DocType is required.")
            return None
        if not start or not end:
            self.lbl_form_error.config(text="Start and End ID are required.")
            return None
        if not out:
            self.lbl_form_error.config(text="Output folder is required.")
            return None
        try:
            delay = int(delay_raw)
        except ValueError:
            self.lbl_form_error.config(text="Delay must be a number.")
            return None
        if delay < 0:
            self.lbl_form_error.config(text="Delay cannot be negative.")
            return None

        # validate template: only {name} and {customer} are allowed
        if "{" in filename_template or "}" in filename_template:
            try:
                filename_template.format(name="TEST", customer="TEST")
            except (KeyError, IndexError, ValueError) as e:
                self.lbl_form_error.config(
                    text=f"Filename template invalid: {e}. "
                    f"Use only {{name}} and {{customer}}."
                )
                return None

        out_path = Path(out).expanduser()
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_path

        s.update(
            doctype=doctype,
            print_format=fmt,
            filename_template=filename_template,
            start=start,
            end=end,
            output_dir=str(out_path),
            delay_ms=delay,
            no_letterhead=bool(self.v_no_letterhead.instate(["selected"])),
            overwrite=bool(self.v_overwrite.instate(["selected"])),
            open_folder_after=bool(self.v_open_after.instate(["selected"])),
            notify_on_finish=bool(self.v_notify.instate(["selected"])),
        )
        self.app.state.update(s)
        return s


    def _on_test(self) -> None:
        s = self._collect()
        if s is None:
            return
        pw = s.get("password", "")
        if not pw:
            messagebox.showerror("Test connection", "Password is missing.")
            return

        self._log("")
        self._log("=== test connection ===")
        self.lbl_status.config(text="testing...")
        self.btn_test.config(state="disabled")
        worker.run(self._job_test, self.app.queue, s)

    def _job_test(self, s: dict) -> None:
        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        try:
            client.authenticate()
            self.app.queue.put(
                (
                    "test.ok",
                    (
                        client.boot_sitename(),
                        client.boot_user_full_name(),
                        client.boot_user_roles(),
                    ),
                )
            )
        except Exception as e:
            self.app.queue.put(("test.err", e))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass

    def _on_detect_formats(self) -> None:
        s = self._collect()
        if s is None:
            return
        doctype = s.get("doctype", "")
        pw = s.get("password", "")
        if not doctype:
            messagebox.showerror("Detect", "Fill in DocType first.")
            return
        if not pw:
            messagebox.showerror("Detect", "Password is missing.")
            return

        self._log(f"Detecting print formats for {doctype!r}...")
        self.btn_start.config(state="disabled")
        worker.run(self._job_detect, self.app.queue, s)

    def _job_detect(self, s: dict) -> None:
        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        try:
            client.authenticate()
            import urllib.parse as _up

            doctype = s["doctype"]
            filters = json.dumps([["doc_type", "=", doctype]])
            fields = json.dumps(["name", "standard", "disabled"])
            path = (
                "/api/method/frappe.client.get_list"
                f"?doctype={_up.quote('Print Format')}"
                f"&filters={_up.quote(filters)}"
                f"&fields={_up.quote(fields)}"
                "&limit_page_length=0"
                "&order_by=standard desc"
            )
            raw = client.get(path)
            data = json.loads(raw)
            items = data.get("message") or []
            names = [
                it.get("name")
                for it in items
                if isinstance(it, dict) and not it.get("disabled")
            ]
            names = [n for n in names if n]
            self.app.queue.put(("detect.ok", names))
        except Exception as e:
            self.app.queue.put(("detect.err", e))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass

    def _on_start(self) -> None:
        if self._running:
            return
        s = self._collect()
        if s is None:
            return
        if not s.get("password"):
            messagebox.showerror("Start", "Password is missing.")
            return

        try:
            names = expand_range(s["start"], s["end"])
        except ValueError as e:
            self.lbl_form_error.config(text=str(e))
            return

        self.lbl_form_error.config(text="")
        self._failed = []
        self.btn_retry.config(state="disabled")
        self.btn_open.config(state="disabled")
        self._launch_run(s, names)

    def _on_retry_failed(self) -> None:
        if self._running or not self._failed:
            return
        s = self._collect()
        if s is None:
            return
        names = list(self._failed)
        self._failed = []
        self._log("")
        self._log(f"=== retrying {len(names)} failed item(s) ===")
        self._launch_run(s, names)

    def _launch_run(self, s: dict, names: list[str]) -> None:
        self._log("")
        self._log(f"=== starting {len(names)} document(s) ===")
        self._log(f"first   : {names[0]}")
        self._log(f"last    : {names[-1]}")
        self._log(f"doctype : {s['doctype']}")
        self._log(f"format  : {s['print_format'] or '(default)'}")
        self._log(f"filename: {s.get('filename_template', DEFAULT_FILENAME_TEMPLATE)}")
        self._log(f"output  : {s['output_dir']}")

        self._running = True
        self._run_started_at = time.monotonic()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_test.config(state="disabled")
        self.btn_logout.config(state="disabled")
        self.pbar.config(maximum=len(names), value=0)
        self.lbl_status.config(text="Signing in...")
        self.lbl_eta.config(text="")

        worker.reset_stop()
        worker.run(self._job, self.app.queue, dict(s), names)

    def _on_stop(self) -> None:
        worker.request_stop()
        self._log("(stop requested, waiting for current request)")
        self.lbl_status.config(text="Stopping...")

    def _on_open_folder(self) -> None:
        path = self.e_out.get().strip()
        if not path:
            return
        p = Path(path).expanduser()
        if not p.exists():
            messagebox.showerror("Open folder", f"Folder does not exist:\n{p}")
            return
        try:
            _open_path(p)
        except Exception as e:
            messagebox.showerror("Open folder", str(e))

    def _on_export_log(self) -> None:
        content = self.txt.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Export log", "Log is empty.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*"),
            ],
            initialfile="spjss.log",
        )
        if not path:
            return
        try:
            Path(path).write_text(content + "\n", encoding="utf-8")
            self._log(f"Log exported to {path}")
        except OSError as e:
            messagebox.showerror("Export log", str(e))

    def _on_logout(self) -> None:
        if self._running:
            return
        email = self.app.state.get("email", "")
        if email and not self.app.state.get("remember_password"):
            keyring.delete(email)
        self.app.state.pop("password", None)
        from .login import LoginPage

        self.app.history.clear()
        self.app._show(LoginPage, push=False)


    def _job(self, s: dict, names: list[str]) -> None:
        out_dir = Path(s["output_dir"])
        client = RjssClient(
            s["base_url"],
            email=s["email"],
            password=s["password"],
            insecure_ssl=s["insecure_ssl"],
        )
        self.app.queue.put(("run.login", None))
        try:
            client.authenticate()
            self.app.queue.put(
                (
                    "run.logged_in",
                    (client.boot_sitename(), client.boot_user_full_name()),
                )
            )
            summary = download_range(
                client=client,
                doctype=s["doctype"],
                names=names,
                fmt=s["print_format"],
                out_dir=out_dir,
                delay_ms=s["delay_ms"],
                no_letterhead=s["no_letterhead"],
                overwrite=s["overwrite"],
                filename_template=s.get("filename_template", DEFAULT_FILENAME_TEMPLATE),
                customer_regex=s.get("customer_regex") or None,
                on_progress=lambda i, t, r: self.app.queue.put(
                    ("run.progress", (i, t, r))
                ),
                should_stop=worker.should_stop,
            )
            self.app.queue.put(("run.done", summary))
        finally:
            try:
                client.logout()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass


    def handle(self, kind: str, payload) -> None:
        if kind == "run.login":
            self.lbl_status.config(text="Signing in...")

        elif kind == "run.logged_in":
            site, user = payload
            self._log(f"Signed in: {user} @ {site}")
            self.lbl_status.config(text="Downloading...")

        elif kind == "run.progress":
            i, total, r = payload
            self.pbar.config(value=i)
            elapsed = time.monotonic() - self._run_started_at
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / rate if rate > 0 else 0
            eta_str = _fmt_duration(remaining)
            self.lbl_status.config(text=f"{i}/{total}")
            self.lbl_eta.config(
                text=f"ETA {eta_str}  |  {rate:.1f} item/s  |  elapsed {_fmt_duration(elapsed)}"
            )
            if r.ok:
                if r.skipped:
                    self._log(f"[{i}/{total}] {r.name}  skipped (already exists)")
                else:
                    kb = r.bytes / 1024.0
                    if getattr(r, "extraction_failed", False):
                        self._log(
                            f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB  "
                            f"(nama customer tidak terbaca, fallback ke ID)"
                        )
                    elif getattr(r, "customer", None) and r.customer != r.name:
                        self._log(
                            f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB  ({r.customer})"
                        )
                    else:
                        self._log(f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB")
            else:
                self._log(f"[{i}/{total}] {r.name}  FAILED: {r.error}")
                if r.name not in self._failed:
                    self._failed.append(r.name)

        elif kind == "run.done":
            summary = payload
            self._last_summary = summary
            self._running = False
            self._log("")
            self._log(
                f"Done: {summary.ok} ok "
                f"({summary.skipped} skipped), "
                f"{summary.failed} failed, "
                f"{summary.total} total"
            )
            if summary.aborted:
                self._log("(stopped by user, some items not processed)")

            elapsed = time.monotonic() - self._run_started_at
            self.lbl_eta.config(text=f"Elapsed {_fmt_duration(elapsed)}")

            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_test.config(state="normal")
            self.btn_logout.config(state="normal")

            if self._failed:
                self.btn_retry.config(state="normal")
            else:
                self.btn_retry.config(state="disabled")

            self.btn_open.config(state="normal")

            self.lbl_status.config(text=f"{summary.ok} ok / {summary.failed} failed")

            s = self.app.state
            cfgmod.save(
                {
                    "base_url": s.get("base_url", ""),
                    "email": s.get("email", ""),
                    "insecure_ssl": s.get("insecure_ssl", False),
                    "remember_password": s.get("remember_password", False),
                    "doctype": s.get("doctype", ""),
                    "print_format": s.get("print_format", ""),
                    "filename_template": s.get(
                        "filename_template", DEFAULT_FILENAME_TEMPLATE
                    ),
                    "customer_regex": s.get("customer_regex", ""),
                    "output_dir": s.get("output_dir", ""),
                    "delay_ms": str(s.get("delay_ms", 300)),
                    "no_letterhead": s.get("no_letterhead", False),
                    "overwrite": s.get("overwrite", False),
                    "open_folder_after": s.get("open_folder_after", True),
                    "notify_on_finish": s.get("notify_on_finish", True),
                }
            )

            if not summary.aborted:
                if s.get("notify_on_finish", True):
                    self.bell()
                    self.app.after(
                        100,
                        lambda: messagebox.showinfo(
                            "Download complete",
                            f"{summary.ok} ok "
                            f"({summary.skipped} skipped)\n"
                            f"{summary.failed} failed\n"
                            f"Elapsed {_fmt_duration(elapsed)}",
                        ),
                    )
                if s.get("open_folder_after", True) and summary.ok:
                    try:
                        _open_path(Path(s["output_dir"]))
                    except Exception as e:
                        self._log(f"(could not open folder: {e})")

        elif kind == "test.ok":
            site, user, roles = payload
            self.btn_test.config(state="normal")
            self.lbl_status.config(text="Connection OK")
            self._log("Connection OK")
            self._log(f"  site : {site}")
            self._log(f"  user : {user}")
            self._log(f"  roles: {', '.join(roles) if roles else '(none)'}")
            messagebox.showinfo(
                "Connection test",
                f"Site: {site}\nUser: {user}\nRoles: {len(roles)}",
            )

        elif kind == "test.err":
            self.btn_test.config(state="normal")
            self.lbl_status.config(text="Connection failed")
            self._log(f"Connection failed: {payload}")
            messagebox.showerror("Connection test", str(payload))

        elif kind == "detect.ok":
            names = payload
            self.btn_start.config(state="normal")
            if not names:
                self._log("No print formats found for that DocType.")
                messagebox.showinfo("Detect", "No print formats found.")
                return
            self.cb_format["values"] = names
            if not self.cb_format.get():
                self.cb_format.set(names[0])
            self._log(f"Found {len(names)} print format(s):")
            for n in names[:10]:
                self._log(f"  {n}")
            if len(names) > 10:
                self._log(f"  ... and {len(names) - 10} more")

        elif kind == "detect.err":
            self.btn_start.config(state="normal")
            self._log(f"Detect failed: {payload}")
            messagebox.showerror("Detect", str(payload))

        elif kind == "err":
            self._running = False
            self._log(f"ERROR: {payload}")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_test.config(state="normal")
            self.btn_logout.config(state="normal")
            self.lbl_status.config(text="Error")

    def _log(self, msg: str) -> None:
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")




def _fmt_duration(seconds: float) -> str:
    if seconds < 0 or seconds != seconds:
        return "--:--"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


def _open_path(path: Path) -> None:
    system = platform.system()
    if system == "Windows":
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
