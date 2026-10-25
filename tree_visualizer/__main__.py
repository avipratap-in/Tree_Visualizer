"""Main entry point for Tree_Visualizer application."""
from __future__ import annotations

import sys
from tree_visualizer.ui.main_window import MainWindow


def main() -> int:
    """Launch the Tree_Visualizer desktop application."""
    app = MainWindow()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
