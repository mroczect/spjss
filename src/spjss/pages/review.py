from tkinter import ttk

from ..downloader import expand_range
from .base import Page


class ReviewPage(Page):
    title = "Tinjau"
    step_label = "Langkah 7 dari 7"
    next_label = "Jalankan"

    def build(self) -> None:
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
        self.lbl_error = ttk.Label(self, text="", foreground="#b00020", wraplength=640)
        self.lbl_error.pack(anchor="w", pady=(12, 0))

    def on_enter(self) -> None:
        for w in self.body.winfo_children():
            w.destroy()

        s = self.app.state
        try:
            names = expand_range(s["start"], s["end"])
        except ValueError as e:
            self.lbl_error.config(text=f"Rentang tidak valid: {e}")
            names = []

        rows = [
            ("Base URL", s.get("base_url", "")),
            ("Email", s.get("email", "")),
            ("SSL tidak valid", "ya" if s.get("insecure_ssl") else "tidak"),
            ("DocType", s.get("doctype", "")),
            ("Print Format", s.get("print_format") or "(default)"),
            ("Start ID", s.get("start", "")),
            ("End ID", s.get("end", "")),
            ("Jumlah dokumen", str(len(names)) if names else "-"),
            ("Folder output", s.get("output_dir", "")),
            ("Delay (ms)", str(s.get("delay_ms", 300))),
            ("Tanpa letterhead", "ya" if s.get("no_letterhead") else "tidak"),
            ("Timpa berkas", "ya" if s.get("overwrite") else "tidak"),
        ]
        form = ttk.Frame(self.body)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        for i, (label, value) in enumerate(rows):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=4)
            ttk.Label(form, text=value, wraplength=520).grid(
                row=i, column=1, sticky="w", padx=8, pady=4
            )

        if names:
            ttk.Label(
                self.body,
                text=f"Akan mengunduh: {names[0]} ... {names[-1]}",
            ).pack(anchor="w", pady=(16, 0))
            self.lbl_error.config(text="")
        else:
            self.lbl_error.config(
                text="Rentang tidak valid. Tekan Kembali dan perbaiki."
            )

    def on_next(self):
        from .run import RunPage

        try:
            expand_range(self.app.state["start"], self.app.state["end"])
        except ValueError:
            return None
        return RunPage

    def on_back(self):
        from .settings import SettingsPage

        return SettingsPage
