"""Main entry point for Tree_Visualizer application."""
from __future__ import annotations

import sys
import tkinter as tk
from tree_visualizer.constants import (
    APP_NAME,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
)


def main() -> int:
    """Launch the Tree_Visualizer desktop application."""
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    # Placeholder/scaffold background matching default dark theme
    root.configure(bg="#0f172a")

    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
