"""State management, playback controller, history/undo stack, and settings.

Coordinates playback timelines, speed multipliers, undo stacks,
and visualizer state without UI dependencies.

CRITICAL: Never import tkinter in this package.
"""
from __future__ import annotations
