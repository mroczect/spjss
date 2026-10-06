from .. import legal
from .base import Page


class PrivacyPage(Page):
    title = "Privacy"
    step_label = "Step 2 of 4"

    def build(self) -> None:
        self.readonly_text(self, legal.load("privacy.txt"), height=26)

    def on_next(self):
        from .terms import TermsPage

        return TermsPage

    def on_back(self):
        from .welcome import WelcomePage

        return WelcomePage
