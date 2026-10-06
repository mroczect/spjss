from pathlib import Path
from tkinter import filedialog, ttk

from .base import Page


class SettingsPage(Page):
    title = "Pengaturan unduhan"
    step_label = "Langkah 6 dari 7"

    def build(self) -> None:
        form = ttk.Frame(self)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="DocType").grid(row=0, column=0, sticky="w", pady=6)
        self.e_doctype = ttk.Entry(form)
        self.e_doctype.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(form, text="Print Format").grid(row=1, column=0, sticky="w", pady=6)
        self.e_format = ttk.Entry(form)
        self.e_format.grid(row=1, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(form, text="kosongkan untuk pakai format default").grid(
            row=1, column=2, sticky="w", padx=8
        )

        ttk.Label(form, text="Start ID").grid(row=2, column=0, sticky="w", pady=6)
        self.e_start = ttk.Entry(form)
        self.e_start.grid(row=2, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(form, text="contoh: JD4521").grid(row=2, column=2, sticky="w", padx=8)

        ttk.Label(form, text="End ID").grid(row=3, column=0, sticky="w", pady=6)
        self.e_end = ttk.Entry(form)
        self.e_end.grid(row=3, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(form, text="contoh: JD4546").grid(row=3, column=2, sticky="w", padx=8)

        ttk.Label(form, text="Folder output").grid(row=4, column=0, sticky="w", pady=6)
        self.e_out = ttk.Entry(form)
        self.e_out.grid(row=4, column=1, sticky="ew", padx=8, pady=6)
        ttk.Button(form, text="Pilih...", command=self._pick_dir).grid(
            row=4, column=2, padx=8
        )

        ttk.Label(form, text="Delay antar request (ms)").grid(
            row=5, column=0, sticky="w", pady=6
        )
        self.e_delay = ttk.Entry(form, width=10)
        self.e_delay.grid(row=5, column=1, sticky="w", padx=8, pady=6)

        self.v_no_letterhead = ttk.Checkbutton(form, text="Tanpa letterhead")
        self.v_no_letterhead.grid(row=6, column=1, sticky="w", padx=8, pady=6)

        self.v_overwrite = ttk.Checkbutton(form, text="Timpa berkas yang sudah ada")
        self.v_overwrite.grid(row=7, column=1, sticky="w", padx=8, pady=6)

        self.lbl_error = ttk.Label(self, text="", foreground="#b00020", wraplength=640)
        self.lbl_error.pack(anchor="w", pady=(12, 0))

    def _pick_dir(self) -> None:
        cur = self.e_out.get().strip() or str(Path.home())
        d = filedialog.askdirectory(initialdir=cur)
        if d:
            self.e_out.delete(0, "end")
            self.e_out.insert(0, d)

    def on_enter(self) -> None:
        s = self.app.state
        pairs = [
            (self.e_doctype, "doctype"),
            (self.e_format, "print_format"),
            (self.e_out, "output_dir"),
            (self.e_delay, "delay_ms"),
        ]
        for widget, key in pairs:
            if widget.get():
                continue
            v = s.get(key)
            if v:
                widget.insert(0, str(v))
        if not self.e_delay.get():
            self.e_delay.insert(0, "300")
        if s.get("no_letterhead"):
            self.v_no_letterhead.state(["selected"])
        if s.get("overwrite"):
            self.v_overwrite.state(["selected"])

    def on_next(self):
        doctype = self.e_doctype.get().strip()
        fmt = self.e_format.get().strip()
        start = self.e_start.get().strip().upper()
        end = self.e_end.get().strip().upper()
        out = self.e_out.get().strip()
        delay_raw = self.e_delay.get().strip() or "300"

        if not doctype:
            self.lbl_error.config(text="DocType wajib diisi.")
            return None
        if not start or not end:
            self.lbl_error.config(text="Start dan End ID wajib diisi.")
            return None
        if not out:
            self.lbl_error.config(text="Folder output wajib dipilih.")
            return None

        try:
            delay = int(delay_raw)
        except ValueError:
            self.lbl_error.config(text="Delay harus angka.")
            return None
        if delay < 0:
            self.lbl_error.config(text="Delay tidak boleh negatif.")
            return None

        out_path = Path(out).expanduser()
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_path

        self.app.state.update(
            doctype=doctype,
            print_format=fmt,
            start=start,
            end=end,
            output_dir=str(out_path),
            delay_ms=delay,
            no_letterhead=bool(self.v_no_letterhead.instate(["selected"])),
            overwrite=bool(self.v_overwrite.instate(["selected"])),
        )
        self.lbl_error.config(text="")
        from .review import ReviewPage

        return ReviewPage

    def on_back(self):
        from .login import LoginPage

        return LoginPage
