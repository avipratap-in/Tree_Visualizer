"""State management, playback controller, history/undo stack, and settings.

Coordinates playback timelines, speed multipliers, undo stacks,
and visualizer state without UI dependencies.

CRITICAL: Never import tkinter in this package.
"""
from __future__ import annotations

from tree_visualizer.state.controller import Controller
from tree_visualizer.state.player import Player
from tree_visualizer.state.settings import Settings
from tree_visualizer.state.share import decode_share_code, encode_share_code

__all__ = [
    "Player",
    "Settings",
    "Controller",
    "encode_share_code",
    "decode_share_code",
]
