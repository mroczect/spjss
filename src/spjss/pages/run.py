import tkinter as tk
from tkinter import messagebox, ttk

from .. import config as cfgmod
from .. import worker
from .._native import RjssClient
from ..downloader import download_range, expand_range
from .base import Page


class RunPage(Page):
    title = "Menjalankan"
    step_label = "Unduhan"
    next_label = "Selesai"
    back_label = "< Ulangi"
    show_next = False

    def build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x")
        self.lbl_status = ttk.Label(top, text="menyiapkan...")
        self.lbl_status.pack(side="left")
        self.btn_stop = ttk.Button(top, text="Hentikan", command=self._on_stop)
        self.btn_stop.pack(side="right")

        self.pbar = ttk.Progressbar(self, mode="determinate")
        self.pbar.pack(fill="x", pady=8)

        logf = ttk.Frame(self)
        logf.pack(fill="both", expand=True)
        self.txt = tk.Text(
            logf,
            wrap="none",
            height=18,
            font=("Courier", 9),
            borderwidth=1,
            relief="solid",
        )
        sb = ttk.Scrollbar(logf, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt.pack(side="left", fill="both", expand=True)

        self._finished = False
        self._results: list = []

    def on_enter(self) -> None:
        if self._finished:
            return
        s = self.app.state
        try:
            names = expand_range(s["start"], s["end"])
        except ValueError as e:
            self._log(f"rentang tidak valid: {e}")
            self.lbl_status.config(text="error")
            return

        self.pbar.config(maximum=len(names), value=0)
        self.lbl_status.config(text=f"0/{len(names)}")
        self._log(f"login ke {s['base_url']} ...")

        worker.reset_stop()
        worker.run(self._job, self.app.queue, dict(s), names)

    def _log(self, msg: str) -> None:
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")

    def _on_stop(self) -> None:
        worker.request_stop()
        self._log("(stop diminta, tunggu request aktif selesai)")
        self.lbl_status.config(text="stop...")

    def _job(self, s: dict, names: list[str]) -> None:
        from pathlib import Path

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
                    (
                        client.boot_sitename(),
                        client.boot_user_full_name(),
                    ),
                )
            )

            out_dir = Path(s["output_dir"])
            results = download_range(
                client=client,
                doctype=s["doctype"],
                names=names,
                fmt=s["print_format"],
                out_dir=out_dir,
                delay_ms=s["delay_ms"],
                no_letterhead=s["no_letterhead"],
                overwrite=s["overwrite"],
                on_progress=lambda i, t, r: self.app.queue.put(
                    ("run.progress", (i, t, r))
                ),
                should_stop=worker.should_stop,
            )
            self.app.queue.put(("run.done", results))
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
            self.lbl_status.config(text="login...")

        elif kind == "run.logged_in":
            site, user = payload
            self._log(f"login ok: {user} @ {site}")
            self.lbl_status.config(text="mengunduh...")

        elif kind == "run.progress":
            i, total, r = payload
            self.pbar.config(value=i)
            self.lbl_status.config(text=f"{i}/{total}")
            if r.ok:
                if r.error and r.error.startswith("skip"):
                    self._log(f"[{i}/{total}] {r.name}  {r.error}")
                else:
                    kb = r.bytes / 1024.0
                    self._log(f"[{i}/{total}] {r.name}  ok  {kb:.1f} KB")
            else:
                self._log(f"[{i}/{total}] {r.name}  GAGAL: {r.error}")

        elif kind == "run.done":
            results = payload
            self._results = results
            ok = sum(1 for r in results if r.ok)
            fail = len(results) - ok
            self._log("")
            self._log(f"selesai: {ok} ok, {fail} gagal, total {len(results)}")

            s = self.app.state
            cfgmod.save(
                {
                    "base_url": s.get("base_url", ""),
                    "email": s.get("email", ""),
                    "insecure_ssl": s.get("insecure_ssl", False),
                    "doctype": s.get("doctype", ""),
                    "print_format": s.get("print_format", ""),
                    "output_dir": s.get("output_dir", ""),
                    "delay_ms": str(s.get("delay_ms", 300)),
                    "no_letterhead": s.get("no_letterhead", False),
                    "overwrite": s.get("overwrite", False),
                }
            )

            self._finished = True
            self.show_next = True
            self.btn_stop.config(state="disabled")
            self.lbl_status.config(text=f"{ok} ok / {fail} gagal")
            self.app.refresh_nav()

        elif kind == "err":
            self._log(f"ERROR: {payload!r}")
            self.btn_stop.config(state="disabled")
            self.lbl_status.config(text="error")
            self._finished = True
            self.show_next = True
            self.app.refresh_nav()

        # "ok" dari worker wrapper (setelah _job selesai) diabaikan
        # karena sudah ditangani oleh event "run.done".

    def on_next(self):
        self.app.destroy()
        return None

    def on_back(self):
        self._finished = False
        from .review import ReviewPage

        return ReviewPage

    def on_leave(self) -> bool:
        if not self._finished and not worker.should_stop():
            if not messagebox.askyesno(
                "Keluar dari halaman ini?",
                "Unduhan sedang berjalan. Hentikan dan kembali?",
            ):
                return False
            worker.request_stop()
        return True
