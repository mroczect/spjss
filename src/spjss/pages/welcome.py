from tkinter import ttk

from .. import legal
from .base import Page


class WelcomePage(Page):
    title = "Welcome"
    step_label = "Step 1 of 4"
    next_label = "Next >"
    show_back = False

    def build(self) -> None:
        ttk.Label(
            self,
            text="spjss",
            font=("TkDefaultFont", 20, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self,
            text="Batch PDF downloader for Frappe / ERPNext",
        ).pack(anchor="w", pady=(0, 12))

        self.readonly_text(self, legal.load("about.txt"), height=22)

    def on_next(self):
        from .privacy import PrivacyPage

        return PrivacyPage
