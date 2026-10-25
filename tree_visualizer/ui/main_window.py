"""Main application window layout and lifecycle manager.

Integrates:
- Windows DPI awareness (SetProcessDpiAwareness)
- TopBar, CollapsibleSidebar, CanvasView (with Overlays), and PlayerBar
- State Controller, Player animation timer loop, and Settings persistence
- Keyboard shortcuts (Space, Left/Right, Ctrl+Z) with focus suppression
- Auto-collapse sidebar behavior on narrow windows (< 980px)
- Multi-resolution app icon integration
"""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from PIL import Image, ImageTk

from tree_visualizer.constants import (
    APP_NAME,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)
from tree_visualizer.state.controller import Controller
from tree_visualizer.ui.canvas_view import CanvasView
from tree_visualizer.ui.fonts import load_custom_fonts
from tree_visualizer.ui.icon import save_app_icons
from tree_visualizer.ui.player_bar import PlayerBar
from tree_visualizer.ui.sidebar import CollapsibleSidebar
from tree_visualizer.ui.theme import ThemeManager
from tree_visualizer.ui.top_bar import TopBar


def enable_windows_dpi_awareness() -> None:
    """Set Windows process DPI awareness so fonts and canvas render crisply."""
    if sys.platform == "win32":
        try:
            import ctypes
            # PROCESS_SYSTEM_DPI_AWARE = 1
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


class MainWindow:
    """The master Tkinter desktop window for Tree_Visualizer."""

    AUTO_COLLAPSE_WIDTH: int = 980

    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        enable_windows_dpi_awareness()

        self.root: tk.Tk = root if root is not None else tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Load fonts and icons
        load_custom_fonts()
        self._setup_window_icon()

        # State and settings
        self.controller: Controller = Controller()
        self.theme_manager: ThemeManager = ThemeManager(
            self.root,
            initial_theme=self.controller.settings.theme,
        )

        # Track auto-collapsed state
        self._auto_collapsed: bool = False
        self._last_width: int = DEFAULT_WINDOW_WIDTH

        # Build UI layout
        self._build_layout()
        self._bind_controller_and_player()
        self._bind_keyboard_shortcuts()

        # Window resize event for auto-collapse
        self.root.bind("<Configure>", self._on_window_configure)

        # Start animation timer loop
        self._schedule_next_tick()

    def _setup_window_icon(self) -> None:
        """Generate and assign application window icon."""
        try:
            png_path, ico_path = save_app_icons()
            if sys.platform == "win32" and os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                img = Image.open(png_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                self._icon_photo_ref = photo  # keep reference
        except Exception:
            pass

    def _build_layout(self) -> None:
        # Top Bar
        self.top_bar = TopBar(
            self.root,
            theme_manager=self.theme_manager,
            on_tab_selected=self._on_tab_selected,
            on_undo=self.controller.undo,
            on_clear=self.controller.clear,
            on_export_json=self._handle_export_json,
            on_export_png=self._handle_export_png,
            on_share=self._handle_share,
            on_theme_toggle=self._handle_theme_toggle,
        )
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        # Player Bar (Bottom)
        self.player_bar = PlayerBar(
            self.root,
            player=self.controller.player,
            theme_manager=self.theme_manager,
        )
        self.player_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Center Container: Sidebar + Canvas View
        self.center_frame = ttk.Frame(self.root, style="TFrame")
        self.center_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.sidebar = CollapsibleSidebar(
            self.center_frame,
            theme_manager=self.theme_manager,
            on_collapse_toggled=self._on_sidebar_collapse_toggled,
            initial_bt_label_type=self.controller.settings.bt_label_type,
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_view = CanvasView(
            self.center_frame,
            theme_manager=self.theme_manager,
            on_expand_sidebar=self.sidebar.expand,
        )
        self.canvas_view.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Connect Sidebar callbacks to Controller
        self._connect_sidebar_callbacks()

    def _connect_sidebar_callbacks(self) -> None:
        """Route sidebar operation button triggers to Controller methods."""
        c = self.controller
        self.sidebar.callbacks.update({
            "bst_random": c.bst_random,
            "bst_load_array": c.bst_load_array,
            "load_preset": c.load_preset,
            "bst_insert": c.bst_insert,
            "bst_search": c.bst_search,
            "bst_remove": c.bst_remove,
            "bst_min": c.bst_min,
            "bst_max": c.bst_max,
            "bst_predecessor": c.bst_predecessor,
            "bst_successor": c.bst_successor,
            "bst_rank": c.bst_rank,
            "bst_select": c.bst_select,
            "binary_random": c.binary_random,
            "binary_load_level_order": c.binary_load_level_order,
            "run_traversal": c.run_traversal,
            "build_reconstruct": c.build_reconstruct,
            "build_random": c.build_random,
            "bt_label_type_changed": self._on_bt_label_type_changed,
            "show_status": c.set_status,
        })

    def _on_bt_label_type_changed(self, label_type: str) -> None:
        """Persist selected label type choice in user settings."""
        self.controller.settings.bt_label_type = label_type
        self.controller.settings.save()

    def _bind_controller_and_player(self) -> None:
        """Connect observers from Controller and Player to UI presentation."""
        c = self.controller

        # Tab changes
        c.on_tab_changed = self._on_controller_tab_changed

        # Tree changes
        c.on_tree_changed = self._on_tree_changed

        # Status messages
        c.on_status_message = lambda msg, sev: self.canvas_view.status_box.set_message(msg, sev)

        # Undo availability
        c.on_undo_state_changed = self.top_bar.set_undo_enabled

        # Properties changes
        c.on_properties_changed = self.sidebar.update_properties

        # Player frame updates
        c.player.add_step_listener(self._on_player_step_changed)
        c.player.add_play_state_listener(self._on_play_state_changed)

    def _on_play_state_changed(self, is_playing: bool) -> None:
        """Disable operation buttons while animation plays; re-enable when stopped."""
        self.sidebar.set_operations_enabled(not is_playing)
        self.top_bar.btn_clear.configure(state="disabled" if is_playing else "normal")
        if is_playing:
            self.top_bar.btn_undo.configure(state="disabled")
        else:
            self.top_bar.set_undo_enabled(self.controller.can_undo)

    def _on_tree_changed(self, tab: str, tree: Optional[TreeNode]) -> None:
        """Handle tree modification in controller."""
        if tab == self.controller.active_tab:
            self.canvas_view.set_tree(tree)

    def _on_player_step_changed(self, current_idx: int, step: Optional[Any]) -> None:
        """Handle step change in Player animation."""
        self.canvas_view.set_pseudocode(self.controller.player.pseudocode, getattr(step, "pseudo_line", None))
        self.canvas_view.set_step(step)

    def _on_tab_selected(self, tab_id: str) -> None:
        """User switched tab in TopBar."""
        self.controller.set_active_tab(tab_id)
        self.sidebar.set_tab(tab_id)
        self.canvas_view.set_tab(tab_id)
        self.canvas_view.set_tree(self.controller.current_tree)

    def _on_controller_tab_changed(self, tab_id: str) -> None:
        self.top_bar.select_tab(tab_id)
        self.sidebar.set_tab(tab_id)
        self.canvas_view.set_tab(tab_id)
        self.canvas_view.set_tree(self.controller.current_tree)

    def _on_sidebar_collapse_toggled(self, is_collapsed: bool) -> None:
        self.canvas_view.set_sidebar_collapsed(is_collapsed)

    def _on_window_configure(self, event: tk.Event) -> None:
        """Handle window resize and auto-collapse on narrow screens."""
        if event.widget == self.root:
            curr_w = event.width
            if curr_w != self._last_width:
                self._last_width = curr_w
                if curr_w < self.AUTO_COLLAPSE_WIDTH and not self.sidebar.is_collapsed:
                    self._auto_collapsed = True
                    self.sidebar.collapse()
                elif curr_w >= self.AUTO_COLLAPSE_WIDTH and self._auto_collapsed:
                    self._auto_collapsed = False
                    self.sidebar.expand()

    def _handle_theme_toggle(self) -> None:
        """Toggle dark / light theme and persist setting."""
        new_theme = self.theme_manager.toggle_theme()
        self.controller.settings.theme = new_theme
        self.controller.settings.save()

    def _handle_export_json(self) -> None:
        """Prompt to export tree to JSON file."""
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Tree as JSON",
        )
        if path:
            import json
            tree_dict = self.controller.current_tree.to_dict() if self.controller.current_tree else None
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(tree_dict, f, indent=2)
                self.controller.set_status(f"Exported tree to {os.path.basename(path)}", severity="info")
            except Exception as e:
                self.controller.set_status(f"Export failed: {e}", severity="error")

    def _handle_export_png(self) -> None:
        """Placeholder for high-res PNG export (implemented fully in Step 7)."""
        self.controller.set_status("PNG export will be processed in export module.", severity="info")

    def _handle_share(self) -> None:
        """Copy share code to system clipboard."""
        code = self.controller.get_share_code()
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.controller.set_status("Share code copied to clipboard!", severity="info")

    # =========================================================================
    # Keyboard Shortcuts
    # =========================================================================

    def _bind_keyboard_shortcuts(self) -> None:
        self.root.bind("<space>", self._on_key_space)
        self.root.bind("<Left>", self._on_key_left)
        self.root.bind("<Right>", self._on_key_right)
        self.root.bind("<Control-z>", self._on_key_undo)
        self.root.bind("<Control-Z>", self._on_key_undo)

    def _is_entry_focused(self) -> bool:
        """Check if active focus is inside an Entry or Text widget."""
        focused = self.root.focus_get()
        return isinstance(focused, (tk.Entry, ttk.Entry, tk.Text))

    def _on_key_space(self, event: tk.Event) -> None:
        if not self._is_entry_focused():
            self.controller.player.toggle_play()

    def _on_key_left(self, event: tk.Event) -> None:
        if not self._is_entry_focused():
            self.controller.player.step_back()

    def _on_key_right(self, event: tk.Event) -> None:
        if not self._is_entry_focused():
            self.controller.player.step_forward()

    def _on_key_undo(self, event: tk.Event) -> None:
        if not self._is_entry_focused():
            self.controller.undo()

    # =========================================================================
    # Animation Timer Loop
    # =========================================================================

    def _schedule_next_tick(self) -> None:
        """Heartbeat loop advancing Player frames via after()."""
        try:
            if not self.root.winfo_exists():
                return
            delay = self.controller.player.delay_ms
            self._after_id = self.root.after(delay, self._on_tick)
        except (tk.TclError, Exception):
            pass

    def _on_tick(self) -> None:
        try:
            if not self.root.winfo_exists():
                return
            if self.controller.player.is_playing:
                self.controller.player.tick()
            self._schedule_next_tick()
        except (tk.TclError, Exception):
            pass

    def destroy(self) -> None:
        """Cleanly destroy window and cancel pending timers."""
        if hasattr(self, "_after_id") and self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if hasattr(self, "canvas_view") and self.canvas_view:
            try:
                self.canvas_view.destroy()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self) -> None:
        """Start the Tkinter event loop."""
        self.root.mainloop()
