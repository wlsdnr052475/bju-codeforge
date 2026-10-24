"""Allow ``python -m bju_codeforge`` to start the desktop application."""

from bju_codeforge.gui.app import main

if __name__ == "__main__":
    raise SystemExit(main())
