"""Compose the default Mock application at the desktop entry point."""

import sys

from PySide6.QtWidgets import QApplication

from bju_codeforge.core.agent import ChatAgent
from bju_codeforge.gui.main_window import MainWindow
from bju_codeforge.providers.mock import MockProvider


def main(argv: list[str] | None = None) -> int:
    """Start the Qt event loop using the replaceable Mock Provider."""
    app = QApplication(sys.argv if argv is None else argv)
    app.setApplicationName("BJU CodeForge")
    app.setOrganizationName("BJU")
    window = MainWindow(ChatAgent(MockProvider()))
    window.show()
    return app.exec()
