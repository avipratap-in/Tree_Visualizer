"""Helper build script for packaging Tree_Visualizer into a standalone executable."""
from __future__ import annotations

import subprocess
import sys


def build():
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "Tree_Visualizer",
        "--windowed",
        "--onefile",
        "--add-data",
        "tree_visualizer/assets;tree_visualizer/assets",
        "tree_visualizer/__main__.py",
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build()
