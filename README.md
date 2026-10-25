# Tree_Visualizer

> A Binary Tree & BST visualizer, built from scratch as a 100% Python desktop application (`tkinter`/`ttk`) for the capstone **Data Structures & Algorithms using Python**.

## Overview
**Tree_Visualizer** provides an interactive, stepped visualization of binary tree algorithms, binary search trees (with frequency-counter duplicate handling), traversals, property validations, and unique tree reconstructions from traversal pairs.

## Requirements
- Python 3.11+
- Standard library `tkinter` and `ttk`
- Optional runtime packages: `Pillow` (for PNG exports), `tkextrafont` (optional custom font loader on non-Windows)
- Development dependencies: `pytest`, `PyInstaller`

## Quick Start
```bash
# Clone the repository
git clone https://github.com/avipratap-in/Tree_Visualizer.git
cd Tree_Visualizer

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run Tree_Visualizer
python -m tree_visualizer
```

## Running Tests
```bash
pytest
```
