from .. import config as cfgmod
from .. import legal
from .base import Page


class ThirdPartyPage(Page):
    title = "Third-party notices"
    step_label = "Step 4 of 4"
    next_label = "I agree, continue >"

    def build(self) -> None:
        self.readonly_text(self, legal.load("third_party.txt"), height=26)

    def on_next(self):
        cfgmod.mark_first_run_complete()
        from .login import LoginPage

        return LoginPage

    def on_back(self):
        from .terms import TermsPage

        return TermsPage
