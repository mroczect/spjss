from .. import legal
from .base import Page


class TermsPage(Page):
    title = "Terms of use"
    step_label = "Step 3 of 4"

    def build(self) -> None:
        self.readonly_text(self, legal.load("terms.txt"), height=26)

    def on_next(self):
        from .third_party import ThirdPartyPage

        return ThirdPartyPage

    def on_back(self):
        from .privacy import PrivacyPage

        return PrivacyPage
