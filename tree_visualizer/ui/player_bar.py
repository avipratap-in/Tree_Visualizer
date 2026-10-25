"""Bottom animation player bar.

Provides controls for:
- Navigation: Skip to start (⏮), Step back (◀), Play/Pause toggle (▶/⏸), Step forward (▶), Skip to end (⏭)
- Scrubber slider tracking animation progress
- Frame step counter (e.g. '0 / 0' or '3 / 12')
- Speed selector (0.25x, 0.5x, 1.0x, 2.0x, 4.0x)
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional
from tree_visualizer.state.player import Player
from tree_visualizer.ui.fonts import get_ui_font
from tree_visualizer.ui.theme import ThemeManager


class PlayerBar(ttk.Frame):
    """Bottom timeline control bar with playback buttons, scrubber, and speed settings."""

    def __init__(
        self,
        master: tk.Widget,
        player: Player,
        theme_manager: ThemeManager,
        **kwargs,
    ) -> None:
        super().__init__(master, style="PlayerBar.TFrame", padding=(12, 6), **kwargs)
        self.player: Player = player
        self.theme_manager: ThemeManager = theme_manager

        self._is_scrubbing: bool = False
        self._build_ui()
        self._bind_player_observers()

    def _build_ui(self) -> None:
        # Left: Playback buttons
        btn_frame = ttk.Frame(self, style="PlayerBar.TFrame")
        btn_frame.pack(side=tk.LEFT, padx=(0, 16))

        self.btn_first = ttk.Button(
            btn_frame,
            text="⏮",
            width=3,
            style="Action.TButton",
            command=self.player.skip_to_start,
        )
        self.btn_first.pack(side=tk.LEFT, padx=2)

        self.btn_back = ttk.Button(
            btn_frame,
            text="◀",
            width=3,
            style="Action.TButton",
            command=self.player.step_back,
        )
        self.btn_back.pack(side=tk.LEFT, padx=2)

        self.btn_play = ttk.Button(
            btn_frame,
            text="▶",
            width=3,
            style="Primary.TButton",
            command=self.player.toggle_play,
        )
        self.btn_play.pack(side=tk.LEFT, padx=2)

        self.btn_forward = ttk.Button(
            btn_frame,
            text="▶",
            width=3,
            style="Action.TButton",
            command=self.player.step_forward,
        )
        self.btn_forward.pack(side=tk.LEFT, padx=2)

        self.btn_last = ttk.Button(
            btn_frame,
            text="⏭",
            width=3,
            style="Action.TButton",
            command=self.player.skip_to_end,
        )
        self.btn_last.pack(side=tk.LEFT, padx=2)

        # Center: Progress Scrubber Slider
        scrubber_frame = ttk.Frame(self, style="PlayerBar.TFrame")
        scrubber_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        self.scrubber_var = tk.DoubleVar(value=0)
        self.scrubber = ttk.Scale(
            scrubber_frame,
            from_=0,
            to=0,
            orient="horizontal",
            variable=self.scrubber_var,
            style="Horizontal.TScale",
            command=self._on_scrubber_change,
        )
        self.scrubber.pack(fill=tk.X, expand=True)
        self.scrubber.bind("<ButtonPress-1>", lambda e: self._set_scrubbing(True))
        self.scrubber.bind("<ButtonRelease-1>", lambda e: self._set_scrubbing(False))

        # Right: Step Counter and Speed Selector
        right_frame = ttk.Frame(self, style="PlayerBar.TFrame")
        right_frame.pack(side=tk.RIGHT, padx=(16, 0))

        self.lbl_counter = ttk.Label(
            right_frame,
            text="0 / 0",
            style="Panel.TLabel",
            font=get_ui_font(10, bold=True),
            width=8,
            anchor="center",
        )
        self.lbl_counter.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(right_frame, text="Speed:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.speed_cb = ttk.Combobox(
            right_frame,
            values=["0.25x", "0.5x", "1.0x", "2.0x", "4.0x"],
            width=6,
            state="readonly",
        )
        self.speed_cb.set("1.0x")
        self.speed_cb.pack(side=tk.LEFT)
        self.speed_cb.bind("<<ComboboxSelected>>", self._on_speed_changed)

    def _bind_player_observers(self) -> None:
        """Connect observers from Player engine to UI widgets."""
        self.player.add_step_listener(self._on_step_changed)
        self.player.add_play_state_listener(self._on_play_state_changed)

    def _on_step_changed(self, current_idx: int, step: Any) -> None:
        total = self.player.total_steps
        if total <= 1:
            self.lbl_counter.configure(text=f"{total} / {total}")
            self.scrubber.configure(from_=0, to=0)
            self.scrubber_var.set(0)
        else:
            self.lbl_counter.configure(text=f"{current_idx + 1} / {total}")
            self.scrubber.configure(from_=0, to=total - 1)
            if not self._is_scrubbing:
                self.scrubber_var.set(current_idx)

    def _on_play_state_changed(self, is_playing: bool) -> None:
        self.btn_play.configure(text="⏸" if is_playing else "▶")

    def _set_scrubbing(self, is_scrubbing: bool) -> None:
        self._is_scrubbing = is_scrubbing
        if not is_scrubbing:
            target = int(round(self.scrubber_var.get()))
            self.player.seek(target)

    def _on_scrubber_change(self, value: str) -> None:
        if self._is_scrubbing:
            target = int(round(float(value)))
            self.player.seek(target)

    def _on_speed_changed(self, event: tk.Event) -> None:
        val_str = self.speed_cb.get().replace("x", "")
        try:
            mult = float(val_str)
            self.player.set_speed(mult)
        except ValueError:
            pass
