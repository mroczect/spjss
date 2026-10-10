import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from . import __version__
from . import config as cfgmod
from ._native import version as lib_version
from .pages import LoginPage, WelcomePage


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("spjss")
        self.geometry("960x820")
        self.minsize(820, 700)

        self.queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.state: dict = {}
        self.state.update(cfgmod.load())

        self._update_checked = False

        self._build_menu()

        self.nav = ttk.Frame(self, padding=10)
        self.nav.pack(side="bottom", fill="x")

        self.lbl_step = ttk.Label(self.nav, text="")
        self.lbl_step.pack(side="left")

        self.btn_next = ttk.Button(self.nav, text="Next >", command=self.go_next)
        self.btn_next.pack(side="right")

        self.btn_back = ttk.Button(self.nav, text="< Back", command=self.go_back)
        self.btn_back.pack(side="right", padx=8)

        self.content = ttk.Frame(self)
        self.content.pack(side="top", fill="both", expand=True)

        self.current = None
        self.history: list = []

        if self.state.get("first_run_complete"):
            self._show(LoginPage, push=False)
        else:
            self._show(WelcomePage, push=False)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._pump)

        self._log(f"librjss-ffi: {lib_version()}")
        if cfgmod.exists():
            self._log(f"Config loaded from {cfgmod.CONFIG_PATH}")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Check for updates…", command=self._on_menu_update)
        help_menu.add_separator()
        help_menu.add_command(label="About spjss", command=self._on_menu_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _on_menu_update(self) -> None:
        from . import update_check

        def job() -> None:
            try:
                result = update_check.check()
                self.queue.put(("menu.update", result))
            except Exception as e:
                self.queue.put(("menu.update.err", e))

        threading.Thread(target=job, daemon=True).start()

    def _on_menu_about(self) -> None:
        messagebox.showinfo(
            "About spjss",
            f"spjss {__version__}\n"
            f"librjss-ffi {lib_version()}\n\n"
            f"Batch PDF downloader for Frappe / ERPNext.\n"
            f"MIT license — see License menu for details.",
        )

    def _show_update_auto(self, info) -> None:
        if self.state.get("_skipped_version") == info.version:
            return
        from .update_dialog import UpdateDialog

        UpdateDialog(self, info)

    def _show_update_result(self, result, manual: bool = False) -> None:
        if result.error:
            if manual:
                messagebox.showerror(
                    "Check for updates", f"Gagal cek update:\n{result.error}"
                )
            return
        if result.has_update:
            from .update_dialog import UpdateDialog

            dlg = UpdateDialog(self, result.info)
            if manual:
                dlg.wait_window()
        elif manual:
            messagebox.showinfo("Check for updates", "Sudah versi terbaru.")

    def _show(self, PageCls, push: bool = True) -> None:
        if self.current is not None:
            if not self.current.on_leave():
                return
            if push:
                self.history.append(type(self.current))
            self.current.destroy()

        page = PageCls(self.content, self)
        page.pack(fill="both", expand=True)
        self.current = page

        self.lbl_step.config(text=page.step_label or page.title)
        self.btn_back.config(
            text=page.back_label,
            state="normal" if page.show_back else "disabled",
        )
        self.btn_next.config(
            text=page.next_label,
            state="normal" if page.show_next else "disabled",
        )

        page.on_enter()

    def refresh_nav(self) -> None:
        p = self.current
        if p is None:
            return
        self.btn_next.config(
            text=p.next_label,
            state="normal" if p.show_next else "disabled",
        )
        self.btn_back.config(
            text=p.back_label,
            state="normal" if p.show_back else "disabled",
        )

    def go_next(self) -> None:
        if self.current is None:
            return
        result = self.current.on_next()
        if result is None:
            return
        if result == "back":
            self.go_back()
            return
        if isinstance(result, type):
            self._show(result, push=True)
            return
        if callable(result):
            result()

    def go_back(self) -> None:
        if not self.history:
            return
        prev = self.history.pop()
        self._show(prev, push=False)

    def _pump(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                self._dispatch(kind, payload)
        except queue.Empty:
            pass
        self.after(100, self._pump)

    def _dispatch(self, kind: str, payload) -> None:
        if kind == "menu.update":
            self._show_update_result(payload, manual=True)
            return
        if kind == "menu.update.err":
            messagebox.showerror("Update", f"Gagal cek update:\n{payload}")
            return
        if kind == "update.auto":
            self._show_update_auto(payload)
            return
        if kind == "update.manual":
            self._show_update_result(payload, manual=True)
            return
        if kind == "update.manual.err":
            messagebox.showerror("Update", f"Gagal cek update:\n{payload}")
            return

        handler = getattr(self.current, "handle", None)
        if callable(handler):
            try:
                handler(kind, payload)
            except Exception as e:
                print(f"handler error: {e!r}")
        else:
            if kind == "err":
                messagebox.showerror("Error", str(payload))

    def _log(self, msg: str) -> None:
        log = getattr(self.current, "_log", None)
        if callable(log):
            log(msg)

    def _on_close(self) -> None:
        from . import worker

        if getattr(self.current, "_running", False):
            if not messagebox.askyesno("Exit", "Download is running. Stop and exit?"):
                return
            worker.request_stop()

        self.state.pop("password", None)
        self.destroy()
