"""Unit tests for the Player playback controller."""
from __future__ import annotations

import pytest
from tree_visualizer.recorder.steps import Step
from tree_visualizer.state.player import Player


def test_player_empty():
    player = Player()
    assert player.total_steps == 0
    assert player.current_step is None
    assert player.is_playing is False
    assert player.tick() is False
    assert player.step_forward() is False
    assert player.step_back() is False

    # Calling play on empty player stays paused
    player.play()
    assert player.is_playing is False


def test_player_single_step():
    player = Player()
    s = Step(tree=None, message="Single step")
    player.load_timeline(["line 0"], [s], auto_play=True)

    # 1-step timelines must NOT auto-play
    assert player.total_steps == 1
    assert player.current_index == 0
    assert player.is_playing is False
    assert player.step_forward() is False
    assert player.step_back() is False
    assert player.tick() is False


def test_player_multi_step_navigation():
    player = Player()
    steps = [Step(message=f"Step {i}") for i in range(5)]
    player.load_timeline(["p0", "p1"], steps, auto_play=False)

    assert player.total_steps == 5
    assert player.current_index == 0
    assert player.is_playing is False

    # Step forward
    assert player.step_forward() is True
    assert player.current_index == 1

    # Step back
    assert player.step_back() is True
    assert player.current_index == 0

    # Skip end
    player.skip_to_end()
    assert player.current_index == 4
    assert player.step_forward() is False

    # Skip start
    player.skip_to_start()
    assert player.current_index == 0

    # Seek
    player.seek(3)
    assert player.current_index == 3


def test_player_tick_and_auto_pause():
    player = Player()
    steps = [Step(message=f"Step {i}") for i in range(3)]
    player.load_timeline(["p0"], steps)

    player.play()
    assert player.is_playing is True

    # Advance step 0 -> 1
    assert player.tick() is True
    assert player.current_index == 1

    # Advance step 1 -> 2 (last step)
    assert player.tick() is True
    assert player.current_index == 2

    # Next tick reaches end and pauses
    assert player.tick() is False
    assert player.is_playing is False


def test_player_speed_multipliers():
    player = Player(base_delay_ms=1000)
    assert player.delay_ms == 1000

    player.set_speed(2.0)
    assert player.delay_ms == 500

    player.set_speed(0.5)
    assert player.delay_ms == 2000

    player.set_speed(4.0)
    assert player.delay_ms == 250


def test_player_observer_callbacks():
    player = Player()
    notified_steps = []
    notified_play_states = []

    player.on_step_changed = lambda idx, step: notified_steps.append(idx)
    player.on_play_state_changed = lambda playing: notified_play_states.append(playing)

    steps = [Step(message="S0"), Step(message="S1")]
    player.load_timeline(["p"], steps)

    assert 0 in notified_steps
    player.play()
    assert True in notified_play_states

    player.pause()
    assert False in notified_play_states
