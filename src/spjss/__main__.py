import sys


def main() -> int:
    from .app import App

    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
