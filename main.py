
import sys


def main() -> int:
    from spjss.app import App

    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())