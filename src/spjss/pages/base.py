from tkinter import ttk


class Page(ttk.Frame):
    """One step of the wizard.

    Subclasses must override build(). They may override:
      on_enter()  - called every time the page is shown
      on_next()   - return None to stay, a Page subclass to
                    navigate to it, "back" to trigger the back
                    action, or a callable to invoke it
      on_leave()  - return False to cancel navigation
    """

    title = ""
    step_label = ""
    next_label = "Next >"
    back_label = "< Back"
    show_next = True
    show_back = True

    def __init__(self, master, app):
        super().__init__(master, padding=16)
        self.app = app
        self.build()

    # -- overridable --

    def build(self) -> None:
        raise NotImplementedError

    def on_enter(self) -> None:
        pass

    def on_leave(self) -> bool:
        return True

    def on_next(self):
        return None

    # -- helpers --

    def readonly_text(self, parent, content: str, height: int = 20):
        import tkinter as tk

        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True)
        t = tk.Text(
            wrap,
            wrap="word",
            height=height,
            font=("TkDefaultFont", 10),
            borderwidth=1,
            relief="solid",
        )
        t.insert("1.0", content)
        t.config(state="disabled")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        t.pack(side="left", fill="both", expand=True)
        return t
