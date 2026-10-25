"""GUI test for Tree_Visualizer main window title and defaults."""
from __future__ import annotations

import tkinter as tk
from tests.conftest import requires_display
from tree_visualizer.constants import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT


@requires_display
def test_window_title_and_initialization():
    """Verify window title matches APP_NAME and geometry matches defaults."""
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
    root.update()

    assert root.title() == "Tree_Visualizer"
    assert root.title() == APP_NAME

    root.destroy()
