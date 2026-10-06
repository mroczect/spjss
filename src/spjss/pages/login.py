from tkinter import ttk

from .. import config as cfgmod
from .. import keyring_helper as keyring
from .base import Page


class LoginPage(Page):
    title = "Sign in"
    step_label = "Sign in"

    def build(self) -> None:
        ttk.Label(
            self,
            text=(
                "Enter your credentials. Your password is sent only to "
                "the server you specify."
            ),
            wraplength=640,
        ).pack(anchor="w", pady=(0, 12))

        form = ttk.Frame(self)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Base URL").grid(row=0, column=0, sticky="w", pady=6)
        self.e_url = ttk.Entry(form)
        self.e_url.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(form, text="Email").grid(row=1, column=0, sticky="w", pady=6)
        self.e_email = ttk.Entry(form)
        self.e_email.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(form, text="Password").grid(row=2, column=0, sticky="w", pady=6)
        self.e_pw = ttk.Entry(form, show="\u2022")
        self.e_pw.grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        self.v_remember = ttk.Checkbutton(
            form,
            text=(
                f"Remember password on this device ({keyring.backend_name()})"
                if keyring.is_available()
                else "Remember password on this device (not available)"
            ),
        )
        if not keyring.is_available():
            self.v_remember.state(["disabled"])
        self.v_remember.grid(row=3, column=1, sticky="w", padx=8, pady=2)

        self.v_insecure = ttk.Checkbutton(
            form,
            text="Allow invalid SSL certificates (development only)",
        )
        self.v_insecure.grid(row=4, column=1, sticky="w", padx=8, pady=2)

        self.lbl_error = ttk.Label(self, text="", foreground="#b00020", wraplength=640)
        self.lbl_error.pack(anchor="w", pady=(12, 0))

    def on_enter(self) -> None:
        s = self.app.state
        if not self.e_url.get():
            self.e_url.insert(0, s.get("base_url", ""))
        if not self.e_email.get():
            self.e_email.insert(0, s.get("email", ""))

        if s.get("remember_password"):
            self.v_remember.state(["selected"])

        # try to load saved password for this email
        email = self.e_email.get().strip()
        if email and not self.e_pw.get() and keyring.is_available():
            saved = keyring.load(email)
            if saved:
                self.e_pw.insert(0, saved)

        self.v_insecure.state(
            ["selected"] if s.get("insecure_ssl", False) else ["!selected"]
        )

    def on_next(self):
        url = self.e_url.get().strip().rstrip("/")
        email = self.e_email.get().strip()
        pw = self.e_pw.get()
        remember = bool(self.v_remember.instate(["selected"]))
        insecure = bool(self.v_insecure.instate(["selected"]))

        if not url:
            self.lbl_error.config(text="Base URL is required.")
            return None
        if not url.startswith(("http://", "https://")):
            self.lbl_error.config(text="Base URL must start with http:// or https://")
            return None
        if not email:
            self.lbl_error.config(text="Email is required.")
            return None
        if not pw:
            self.lbl_error.config(text="Password is required.")
            return None

        self.app.state["base_url"] = url
        self.app.state["email"] = email
        self.app.state["password"] = pw
        self.app.state["remember_password"] = remember
        self.app.state["insecure_ssl"] = insecure

        # persist password if requested
        if remember and keyring.is_available():
            keyring.save(email, pw)
        elif not remember and keyring.is_available():
            keyring.delete(email)

        # persist non-secret bits to config
        cfgmod.save(
            {
                "base_url": url,
                "email": email,
                "insecure_ssl": insecure,
                "remember_password": remember,
            }
        )

        self.lbl_error.config(text="")
        from .dashboard import DashboardPage

        return DashboardPage

    def on_back(self):
        from .third_party import ThirdPartyPage

        return ThirdPartyPage
