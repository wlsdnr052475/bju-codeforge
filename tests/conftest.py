"""Shared Qt event-loop helpers; no additional GUI test dependency is required."""

from collections.abc import Callable, Iterator
from time import monotonic

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> Iterator[QApplication]:
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    yield app
    app.processEvents()


@pytest.fixture
def wait_until(qapp: QApplication) -> Callable[[Callable[[], bool]], None]:
    """Pump Qt events until a condition is true, with a bounded failure timeout."""

    def wait(condition: Callable[[], bool]) -> None:
        deadline = monotonic() + 6
        while not condition() and monotonic() < deadline:
            QTest.qWait(5)
        assert condition(), "Qt condition did not become true within 6 seconds"

    return wait
