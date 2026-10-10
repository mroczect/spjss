
from __future__ import annotations

import queue
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk

from . import __version__, update_check, worker
from ._native import version as lib_version


class UpdateDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, info: update_check.UpdateInfo):
        super().__init__(master)
        self.title("Update tersedia")
        self.transient(master)
        self.resizable(False, False)

        self._info = info
        self._installer: Path | None = None
        self._downloading = False
        self._queue: queue.Queue[tuple[str, object]] = queue.Queue()

        self._build()
        self._center_on(master)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda _e: self._on_close())

        self.after(100, self._pump)


    def _build(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        ttk.Label(
            root,
            text=f"spjss {self._info.version} tersedia",
            font=("TkDefaultFont", 14, "bold"),
        ).pack(anchor="w")

        meta = f"Versi terpasang: {__version__}  •  librjss-ffi {lib_version()}"
        if self._info.published_at:
            meta += f"  •  dirilis {self._info.published_at[:10]}"
        ttk.Label(root, text=meta, foreground="#666").pack(anchor="w", pady=(0, 12))

        if self._info.notes:
            notes_frame = ttk.LabelFrame(root, text="Catatan rilis", padding=6)
            notes_frame.pack(fill="both", expand=True, pady=(0, 12))
            txt = tk.Text(
                notes_frame,
                wrap="word",
                height=12,
                width=72,
                font=("TkDefaultFont", 9),
                borderwidth=0,
            )
            txt.insert("1.0", self._info.notes)
            txt.config(state="disabled")
            sb = ttk.Scrollbar(notes_frame, orient="vertical", command=txt.yview)
            txt.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            txt.pack(side="left", fill="both", expand=True)

        self.lbl_note = ttk.Label(root, text="", foreground="#b00020", wraplength=520)
        self.lbl_note.pack(anchor="w")

        self.pbar = ttk.Progressbar(root, mode="determinate")
        self.pbar.pack(fill="x", pady=(8, 4))

        self.lbl_status = ttk.Label(root, text="")
        self.lbl_status.pack(anchor="w", pady=(0, 12))

        btns = ttk.Frame(root)
        btns.pack(fill="x")

        self.btn_skip = ttk.Button(btns, text="Lewati versi ini", command=self._on_skip)
        self.btn_skip.pack(side="left")

        ttk.Button(btns, text="Halaman rilis", command=self._open_page).pack(
            side="left", padx=6
        )

        self.btn_close = ttk.Button(btns, text="Nanti", command=self._on_close)
        self.btn_close.pack(side="right")

        self.btn_action = ttk.Button(
            btns,
            text="Download & Install",
            command=self._on_action,
            state="normal" if self._info.has_installer else "disabled",
        )
        self.btn_action.pack(side="right", padx=6)

        if not self._info.has_installer:
            self.lbl_note.config(
                text=(
                    "Rilis ini tidak menyediakan installer untuk platform "
                    "kamu. Buka halaman rilis untuk update manual."
                )
            )

    def _center_on(self, master: tk.Misc) -> None:
        self.update_idletasks()
        try:
            mx, my = master.winfo_rootx(), master.winfo_rooty()
            mw, mh = master.winfo_width(), master.winfo_height()
        except tk.TclError:
            return
        w, h = self.winfo_width(), self.winfo_height()
        x = max(mx + (mw - w) // 2, 0)
        y = max(my + (mh - h) // 2, 0)
        self.geometry(f"+{x}+{y}")


    def _on_action(self) -> None:
        if self._installer is not None:
            self._install_now()
            return
        if self._downloading:
            return
        self._start_download()

    def _start_download(self) -> None:
        self._downloading = True
        self.btn_action.config(state="disabled", text="Mengunduh...")
        self.btn_close.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self.pbar.config(value=0, maximum=100)
        self.lbl_status.config(text="Menghubungi server...")
        self.lbl_note.config(text="")

        worker.reset_stop()
        worker.run(self._job_download, self._queue, self._info)

    def _job_download(self, info: update_check.UpdateInfo) -> None:
        try:
            path = update_check.download_installer(
                info,
                on_progress=lambda got, total: self._queue.put(
                    ("dl.progress", (got, total))
                ),
                should_stop=worker.should_stop,
            )
            self._queue.put(("dl.done", path))
        except Exception as e:
            self._queue.put(("dl.err", e))

    def _install_now(self) -> None:
        assert self._installer is not None
        if not messagebox.askyesno(
            "Install update",
            "Aplikasi akan ditutup dan installer dijalankan.\n"
            "Setelah selesai, spjss akan terbuka lagi.\n\n"
            "Lanjutkan?",
            parent=self,
        ):
            return
        try:
            update_check.launch_installer(self._installer)
        except Exception as e:
            messagebox.showerror(
                "Install", f"Gagal menjalankan installer:\n{e}", parent=self
            )
            return
        try:
            self.master.destroy()
        except Exception:
            pass

    def _on_skip(self) -> None:
        try:
            from . import config as cfgmod

            cfgmod.save({"_skipped_version": self._info.version})
        except Exception:
            pass
        self._on_close()

    def _open_page(self) -> None:
        if self._info.html_url:
            try:
                webbrowser.open(self._info.html_url)
            except Exception:
                pass

    def _on_close(self) -> None:
        if self._downloading:
            if not messagebox.askyesno(
                "Batalkan unduhan?",
                "Unduhan sedang berjalan. Batalkan?",
                parent=self,
            ):
                return
            worker.request_stop()
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


    def _pump(self) -> None:
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                self._handle(kind, payload)
        except queue.Empty:
            pass
        if self.winfo_exists():
            self.after(100, self._pump)

    def _handle(self, kind: str, payload) -> None:
        if kind == "dl.progress":
            got, total = payload
            if total > 0:
                pct = int(got * 100 / total)
                self.pbar.config(value=pct)
                self.lbl_status.config(
                    text=f"{got / 1024 / 1024:.1f} MB / "
                    f"{total / 1024 / 1024:.1f} MB  ({pct}%)"
                )
            else:
                self.lbl_status.config(text=f"{got / 1024 / 1024:.1f} MB")

        elif kind == "dl.done":
            self._downloading = False
            self._installer = payload
            self.btn_action.config(text="Install & Restart", state="normal")
            self.btn_close.config(state="normal")
            self.btn_skip.config(state="normal")
            self.pbar.config(value=100)
            self.lbl_status.config(text="Unduhan selesai.")

        elif kind == "dl.err":
            self._downloading = False
            self.btn_action.config(text="Coba lagi", state="normal")
            self.btn_close.config(state="normal")
            self.btn_skip.config(state="normal")
            self.lbl_status.config(text="")
            self.lbl_note.config(text=f"Gagal: {payload}")
