"""Helper build script for packaging Tree_Visualizer into a standalone executable."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def build():
    root = Path(__file__).resolve().parent.parent
    icon_path = root / "tree_visualizer" / "assets" / "icon.ico"
    assets_src = root / "tree_visualizer" / "assets"

    sep = ";" if sys.platform.startswith("win") else ":"
    add_data = f"{assets_src}{sep}tree_visualizer/assets"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "Tree_Visualizer",
        "--windowed",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--icon",
        str(icon_path),
        "--add-data",
        add_data,
        str(root / "tree_visualizer" / "__main__.py"),
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(root), check=True)


if __name__ == "__main__":
    build()

