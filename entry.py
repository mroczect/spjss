"""PyInstaller entry point.

Lives outside the package so PyInstaller can run it as a top-level
script. Imports are absolute, since there is no parent package at
runtime when bundled.
"""

import sys


def main() -> int:
    from spjss.app import App

    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())