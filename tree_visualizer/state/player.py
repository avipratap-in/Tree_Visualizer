"""Animation timeline player and playback controller.

Coordinates step-by-step navigation, scrubber progress, speed adjustments,
and time-stepped animation ticks without UI dependencies.

Complexity:
- Navigation operations (step, seek, skip): O(1) time and space.
"""
from __future__ import annotations

from typing import Any, Callable, List, Optional
from tree_visualizer.recorder.steps import Step


class Player:
    """Timeline player that manages algorithm step frames and playback state."""

    SPEED_MULTIPLIERS = [0.25, 0.5, 1.0, 2.0, 4.0]

    def __init__(self, base_delay_ms: int = 1000) -> None:
        self.base_delay_ms: int = base_delay_ms
        self.speed_multiplier: float = 1.0
        self.steps: List[Step] = []
        self.pseudocode: List[str] = []
        self.current_index: int = 0
        self.is_playing: bool = False

        # Observer callbacks & listeners
        self.on_step_changed: Optional[Callable[[int, Optional[Step]], None]] = None
        self.on_play_state_changed: Optional[Callable[[bool], None]] = None
        self._step_listeners: List[Callable[[int, Optional[Step]], None]] = []
        self._play_state_listeners: List[Callable[[bool], None]] = []

    def add_step_listener(self, listener: Callable[[int, Optional[Step]], None]) -> None:
        """Register a callback for step changes."""
        self._step_listeners.append(listener)

    def add_play_state_listener(self, listener: Callable[[bool], None]) -> None:
        """Register a callback for play/pause state changes."""
        self._play_state_listeners.append(listener)

    @property
    def total_steps(self) -> int:
        """Return total number of animation steps loaded."""
        return len(self.steps)

    @property
    def current_step(self) -> Optional[Step]:
        """Return the current active Step frame, or None if no steps exist."""
        if not self.steps or self.current_index < 0 or self.current_index >= len(self.steps):
            return None
        return self.steps[self.current_index]

    @property
    def delay_ms(self) -> int:
        """Calculate active frame delay in milliseconds based on speed multiplier."""
        return max(50, int(self.base_delay_ms / self.speed_multiplier))

    def set_speed(self, multiplier: float) -> None:
        """Set playback speed multiplier (e.g. 0.25, 0.5, 1.0, 2.0, 4.0)."""
        if multiplier > 0:
            self.speed_multiplier = multiplier

    def load_timeline(
        self,
        pseudocode: List[str],
        steps: List[Step],
        auto_play: bool = False,
    ) -> None:
        """Load an animation timeline into the player.

        Safely resets indices and correctly handles 0 or 1 step timelines.
        """
        self.pause()
        self.pseudocode = list(pseudocode)
        self.steps = list(steps)
        self.current_index = 0

        self._notify_step()

        if auto_play and len(self.steps) > 1:
            self.play()

    def play(self) -> None:
        """Start automatic playback."""
        if len(self.steps) <= 1:
            self.is_playing = False
            self._notify_play_state()
            return

        # If at the last step, wrap back to start before playing
        if self.current_index >= len(self.steps) - 1:
            self.current_index = 0
            self._notify_step()

        self.is_playing = True
        self._notify_play_state()

    def pause(self) -> None:
        """Pause automatic playback."""
        if self.is_playing:
            self.is_playing = False
            self._notify_play_state()

    def toggle_play(self) -> None:
        """Toggle between playing and paused."""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def step_forward(self) -> bool:
        """Advance by one step. Returns True if advanced, False if at the end."""
        self.pause()
        if not self.steps:
            return False
        if self.current_index < len(self.steps) - 1:
            self.current_index += 1
            self._notify_step()
            return True
        return False

    def step_back(self) -> bool:
        """Step back by one step. Returns True if moved back, False if at start."""
        self.pause()
        if not self.steps:
            return False
        if self.current_index > 0:
            self.current_index -= 1
            self._notify_step()
            return True
        return False

    def skip_to_start(self) -> None:
        """Jump to the very first step frame (index 0)."""
        self.pause()
        if self.steps and self.current_index != 0:
            self.current_index = 0
            self._notify_step()

    def skip_to_end(self) -> None:
        """Jump to the final step frame."""
        self.pause()
        if self.steps and self.current_index != len(self.steps) - 1:
            self.current_index = len(self.steps) - 1
            self._notify_step()

    def seek(self, index: int) -> None:
        """Seek directly to a specific 0-based step index."""
        self.pause()
        if not self.steps:
            self.current_index = 0
            return
        target = max(0, min(index, len(self.steps) - 1))
        if target != self.current_index:
            self.current_index = target
            self._notify_step()

    def replay(self) -> None:
        """Reset to start and begin playback."""
        self.skip_to_start()
        self.play()

    def tick(self) -> bool:
        """Advance one frame if currently playing.

        Called by the UI timer loop (e.g. root.after(delay_ms, tick)).
        Returns True if playback is still active, False if playback paused or reached end.
        """
        if not self.is_playing or not self.steps:
            return False

        if self.current_index < len(self.steps) - 1:
            self.current_index += 1
            self._notify_step()
            return True
        else:
            # Reached final step
            self.pause()
            return False

    def _notify_step(self) -> None:
        if self.on_step_changed is not None:
            self.on_step_changed(self.current_index, self.current_step)
        for listener in self._step_listeners:
            listener(self.current_index, self.current_step)

    def _notify_play_state(self) -> None:
        if self.on_play_state_changed is not None:
            self.on_play_state_changed(self.is_playing)
        for listener in self._play_state_listeners:
            listener(self.is_playing)
