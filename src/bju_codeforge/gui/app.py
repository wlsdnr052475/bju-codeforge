"""Compose the default Mock application at the desktop entry point."""

import sys

from PySide6.QtWidgets import QApplication

from bju_codeforge.core.agent import ChatAgent
from bju_codeforge.gui.main_window import MainWindow
from bju_codeforge.providers.mock import MockProvider


def main(argv: list[str] | None = None) -> int:
    """Start the Qt event loop using the replaceable Mock Provider."""
    arguments = list(sys.argv if argv is None else argv)
    smoke_test = "--smoke-test" in arguments
    app = QApplication([argument for argument in arguments if argument != "--smoke-test"])
    app.setApplicationName("BJU CodeForge")
    app.setOrganizationName("BJU")
    window = MainWindow(ChatAgent(MockProvider()))
    window.show()
    if smoke_test:
        from bju_codeforge.gui.smoke import run_smoke_test

        return run_smoke_test(app, window)
    return app.exec()
