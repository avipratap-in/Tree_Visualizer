"""Collapsible Operations Sidebar for Tree_Visualizer.

Contains dedicated controls for:
- BST Tab: Random/Array creation, Presets, Insert, Search, Remove, Min/Max, Pred/Succ, Rank/Select.
- Binary Tree Tab: Random generation, Level-order loader, Traversals, Properties card grid.
- Build from Traversal Tab: Mode selection, Sequence inputs, Validation box, Build & Animate.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional
from tree_visualizer.ui.fonts import get_ui_font
from tree_visualizer.ui.theme import ThemeManager


class CollapsibleSidebar(ttk.Frame):
    """Collapsible left operations sidebar with tab-specific control panels."""

    PANEL_WIDTH: int = 320

    def __init__(
        self,
        master: tk.Widget,
        theme_manager: ThemeManager,
        on_collapse_toggled: Optional[Callable[[bool], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, style="Sidebar.TFrame", width=self.PANEL_WIDTH, **kwargs)
        self.theme_manager: ThemeManager = theme_manager
        self.on_collapse_toggled: Optional[Callable[[bool], None]] = on_collapse_toggled
        self.is_collapsed: bool = False
        self.active_tab: str = "bst"

        # Callbacks hooked to Controller
        self.callbacks: Dict[str, Callable[..., Any]] = {}

        self.pack_propagate(False)
        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_updated)

    def _build_ui(self) -> None:
        # Header bar
        self.header_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=(12, 10))
        self.header_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(
            self.header_frame,
            text="BST Operations",
            style="Header.TLabel",
            font=get_ui_font(11, bold=True),
        )
        self.title_label.pack(side=tk.LEFT)

        self.btn_collapse = ttk.Button(
            self.header_frame,
            text="✕",
            width=3,
            style="Action.TButton",
            command=self.toggle_collapse,
        )
        self.btn_collapse.pack(side=tk.RIGHT)

        # Scrollable container for tab contents
        self.canvas_container = tk.Canvas(
            self,
            bg=self.theme_manager.current["bg_panel"],
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas_container.yview,
        )
        self.scrollable_frame = ttk.Frame(self.canvas_container, style="Sidebar.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_container.configure(
                scrollregion=self.canvas_container.bbox("all")
            ),
        )
        self.canvas_window = self.canvas_container.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.PANEL_WIDTH - 20,
        )

        self.canvas_container.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8))

        # Mousewheel scroll binding
        self.canvas_container.bind_all("<MouseWheel>", self._on_mousewheel)

        # Tab panels
        self.panels: Dict[str, ttk.Frame] = {}
        self._build_bst_panel()
        self._build_binary_panel()
        self._build_build_panel()

        self.set_tab("bst")

    def _on_mousewheel(self, event: tk.Event) -> None:
        # Only scroll if cursor is within sidebar canvas
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        if widget and str(self.canvas_container) in str(widget):
            self.canvas_container.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_tab(self, tab: str) -> None:
        """Switch active sidebar control panel."""
        self.active_tab = tab
        titles = {
            "bst": "BST Operations",
            "binary": "Binary Tree Operations",
            "build": "Build from Traversal",
        }
        self.title_label.configure(text=titles.get(tab, "Operations"))

        for tid, panel in self.panels.items():
            if tid == tab:
                panel.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            else:
                panel.pack_forget()

        # Reset scroll position
        self.canvas_container.yview_moveto(0)

    def toggle_collapse(self) -> None:
        """Toggle sidebar collapsed / expanded state."""
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.pack_forget()
        else:
            self.pack(side=tk.LEFT, fill=tk.Y)

        if self.on_collapse_toggled:
            self.on_collapse_toggled(self.is_collapsed)

    def collapse(self) -> None:
        """Explicitly collapse the sidebar."""
        if not self.is_collapsed:
            self.toggle_collapse()

    def expand(self) -> None:
        """Explicitly expand the sidebar."""
        if self.is_collapsed:
            self.toggle_collapse()

    # =========================================================================
    # BST Panel UI
    # =========================================================================

    def _build_bst_panel(self) -> None:
        panel = ttk.Frame(self.scrollable_frame, style="Sidebar.TFrame")
        self.panels["bst"] = panel

        # Section: Create BST
        sec_create = self._create_section(panel, "Create BST")
        # Random BST
        row_rnd = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_rnd.pack(fill=tk.X, pady=(2, 6))
        ttk.Label(row_rnd, text="Count N:", style="Panel.TLabel").pack(side=tk.LEFT)
        self.bst_count_entry = ttk.Entry(row_rnd, width=5)
        self.bst_count_entry.insert(0, "7")
        self.bst_count_entry.pack(side=tk.LEFT, padx=6)
        ttk.Button(
            row_rnd,
            text="Random",
            style="TButton",
            command=self._handle_bst_random,
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Custom Array Load
        row_arr = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_arr.pack(fill=tk.X, pady=(2, 6))
        self.bst_array_entry = ttk.Entry(row_arr)
        self.bst_array_entry.insert(0, "50, 30, 70, 20")
        self.bst_array_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_arr,
            text="Load",
            style="TButton",
            command=self._handle_bst_load_array,
        ).pack(side=tk.RIGHT)

        # Preset Dropdown
        row_preset = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_preset.pack(fill=tk.X, pady=(2, 2))
        self.bst_preset_cb = ttk.Combobox(
            row_preset,
            values=[
                "Select a Preset BST...",
                "1. Balanced BST (7 nodes)",
                "2. Right-Skewed BST (5 nodes)",
                "3. BST with Duplicates",
                "4. Full & Perfect Tree",
            ],
            state="readonly",
        )
        self.bst_preset_cb.current(0)
        self.bst_preset_cb.pack(fill=tk.X)
        self.bst_preset_cb.bind("<<ComboboxSelected>>", self._handle_preset_selected)

        # Section: Insert
        sec_insert = self._create_section(panel, "Insert")
        row_ins = ttk.Frame(sec_insert, style="Sidebar.TFrame")
        row_ins.pack(fill=tk.X)
        self.bst_insert_entry = ttk.Entry(row_ins)
        self.bst_insert_entry.insert(0, "45")
        self.bst_insert_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_ins,
            text="Insert",
            style="Primary.TButton",
            command=self._handle_bst_insert,
        ).pack(side=tk.RIGHT)

        # Section: Search & Remove
        sec_sr = self._create_section(panel, "Search & Remove")
        row_search = ttk.Frame(sec_sr, style="Sidebar.TFrame")
        row_search.pack(fill=tk.X, pady=(0, 4))
        self.bst_search_entry = ttk.Entry(row_search)
        self.bst_search_entry.insert(0, "50")
        self.bst_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_search,
            text="Search",
            style="TButton",
            command=self._handle_bst_search,
        ).pack(side=tk.RIGHT)

        row_remove = ttk.Frame(sec_sr, style="Sidebar.TFrame")
        row_remove.pack(fill=tk.X)
        self.bst_remove_entry = ttk.Entry(row_remove)
        self.bst_remove_entry.insert(0, "50")
        self.bst_remove_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_remove,
            text="Remove",
            style="Danger.TButton",
            command=self._handle_bst_remove,
        ).pack(side=tk.RIGHT)

        # Section: Min & Max
        sec_minmax = self._create_section(panel, "Min & Max")
        row_mm = ttk.Frame(sec_minmax, style="Sidebar.TFrame")
        row_mm.pack(fill=tk.X)
        ttk.Button(
            row_mm,
            text="Find Min",
            style="TButton",
            command=self._handle_bst_min,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(
            row_mm,
            text="Find Max",
            style="TButton",
            command=self._handle_bst_max,
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        # Section: Predecessor & Successor
        sec_ps = self._create_section(panel, "Predecessor & Successor")
        self.bst_ps_entry = ttk.Entry(sec_ps)
        self.bst_ps_entry.insert(0, "50")
        self.bst_ps_entry.pack(fill=tk.X, pady=(0, 4))
        row_ps_btns = ttk.Frame(sec_ps, style="Sidebar.TFrame")
        row_ps_btns.pack(fill=tk.X)
        ttk.Button(
            row_ps_btns,
            text="Predecessor",
            style="TButton",
            command=self._handle_bst_pred,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(
            row_ps_btns,
            text="Successor",
            style="TButton",
            command=self._handle_bst_succ,
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        # Section: Rank & Select
        sec_rs = self._create_section(panel, "Rank & Select")
        row_rank = ttk.Frame(sec_rs, style="Sidebar.TFrame")
        row_rank.pack(fill=tk.X, pady=(0, 4))
        self.bst_rank_entry = ttk.Entry(row_rank)
        self.bst_rank_entry.insert(0, "50")
        self.bst_rank_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_rank,
            text="Rank",
            style="TButton",
            command=self._handle_bst_rank,
        ).pack(side=tk.RIGHT)

        row_sel = ttk.Frame(sec_rs, style="Sidebar.TFrame")
        row_sel.pack(fill=tk.X)
        self.bst_select_entry = ttk.Entry(row_sel)
        self.bst_select_entry.insert(0, "3")
        self.bst_select_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_sel,
            text="Select (k)",
            style="TButton",
            command=self._handle_bst_select,
        ).pack(side=tk.RIGHT)

    # =========================================================================
    # Binary Tree Panel UI
    # =========================================================================

    def _build_binary_panel(self) -> None:
        panel = ttk.Frame(self.scrollable_frame, style="Sidebar.TFrame")
        self.panels["binary"] = panel

        # Section: Create Binary Tree
        sec_create = self._create_section(panel, "Create Binary Tree")
        row_rnd = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_rnd.pack(fill=tk.X, pady=(2, 6))
        ttk.Label(row_rnd, text="Count N:", style="Panel.TLabel").pack(side=tk.LEFT)
        self.bt_count_entry = ttk.Entry(row_rnd, width=5)
        self.bt_count_entry.insert(0, "6")
        self.bt_count_entry.pack(side=tk.LEFT, padx=6)

        ttk.Button(
            row_rnd,
            text="Random",
            style="TButton",
            command=self._handle_binary_random,
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        row_lbl = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_lbl.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row_lbl, text="Labels:", style="Panel.TLabel").pack(side=tk.LEFT)
        self.bt_label_type_var = tk.StringVar(value="numbers")
        ttk.Radiobutton(
            row_lbl,
            text="Numbers",
            variable=self.bt_label_type_var,
            value="numbers",
        ).pack(side=tk.LEFT, padx=(6, 4))
        ttk.Radiobutton(
            row_lbl,
            text="Letters",
            variable=self.bt_label_type_var,
            value="letters",
        ).pack(side=tk.LEFT)

        # Level order load
        ttk.Label(
            sec_create,
            text="Level-order list (e.g. 1, 2, 3, null, 4):",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 2))
        row_load = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_load.pack(fill=tk.X)
        self.bt_level_entry = ttk.Entry(row_load)
        self.bt_level_entry.insert(0, "1, 2, 3, 4, 5, 6")
        self.bt_level_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(
            row_load,
            text="Load",
            style="TButton",
            command=self._handle_binary_load,
        ).pack(side=tk.RIGHT)

        # Section: Traversals
        sec_trav = self._create_section(panel, "Traversals")
        t_row1 = ttk.Frame(sec_trav, style="Sidebar.TFrame")
        t_row1.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(
            t_row1,
            text="Preorder",
            style="TButton",
            command=lambda: self._handle_traversal("pre"),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(
            t_row1,
            text="Inorder",
            style="TButton",
            command=lambda: self._handle_traversal("in"),
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        t_row2 = ttk.Frame(sec_trav, style="Sidebar.TFrame")
        t_row2.pack(fill=tk.X)
        ttk.Button(
            t_row2,
            text="Postorder",
            style="TButton",
            command=lambda: self._handle_traversal("post"),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(
            t_row2,
            text="Level Order",
            style="TButton",
            command=lambda: self._handle_traversal("level"),
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        # Section: Tree Properties
        sec_props = self._create_section(panel, "Tree Properties")
        self.props_labels: Dict[str, ttk.Label] = {}
        props_list = [
            ("size", "Total Nodes:"),
            ("leaves", "Leaf Count:"),
            ("internal", "Internal Nodes:"),
            ("height", "Height:"),
            ("is_full", "Full Tree:"),
            ("is_complete", "Complete:"),
            ("is_perfect", "Perfect:"),
            ("is_balanced", "Height-Balanced:"),
        ]
        for key, text in props_list:
            row = ttk.Frame(sec_props, style="Sidebar.TFrame")
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=text, style="Muted.TLabel").pack(side=tk.LEFT)
            lbl_val = ttk.Label(row, text="-", style="Panel.TLabel", font=get_ui_font(9, bold=True))
            lbl_val.pack(side=tk.RIGHT)
            self.props_labels[key] = lbl_val

    # =========================================================================
    # Build from Traversal Panel UI
    # =========================================================================

    def _build_build_panel(self) -> None:
        panel = ttk.Frame(self.scrollable_frame, style="Sidebar.TFrame")
        self.panels["build"] = panel

        # Section: Mode Selection
        sec_mode = self._create_section(panel, "Reconstruction Mode")
        self.build_mode_cb = ttk.Combobox(
            sec_mode,
            values=[
                "Inorder + Preorder",
                "Inorder + Postorder",
                "Inorder + Level Order",
                "Preorder + Postorder (Full BT only)",
                "BST from Preorder only",
                "BST from Postorder only",
            ],
            state="readonly",
        )
        self.build_mode_cb.current(0)
        self.build_mode_cb.pack(fill=tk.X, pady=(2, 4))
        self.build_mode_cb.bind("<<ComboboxSelected>>", self._handle_build_mode_changed)

        # Ambiguity Warning Banner
        self.ambiguity_banner = tk.Label(
            sec_mode,
            text="⚠️ Note: Preorder + Postorder uniquely reconstructs Full Binary Trees only.",
            bg="#fef08a",
            fg="#854d0e",
            font=get_ui_font(8),
            wraplength=self.PANEL_WIDTH - 40,
            justify=tk.LEFT,
            padx=6,
            pady=4,
        )

        # Section: Sequences
        sec_seq = self._create_section(panel, "Sequences")
        self.lbl_seq1 = ttk.Label(sec_seq, text="Inorder Sequence:", style="Panel.TLabel")
        self.lbl_seq1.pack(anchor="w", pady=(2, 1))
        self.build_seq1_entry = ttk.Entry(sec_seq)
        self.build_seq1_entry.insert(0, "D, B, E, A, F, C")
        self.build_seq1_entry.pack(fill=tk.X, pady=(0, 6))

        self.lbl_seq2 = ttk.Label(sec_seq, text="Preorder Sequence:", style="Panel.TLabel")
        self.lbl_seq2.pack(anchor="w", pady=(2, 1))
        self.build_seq2_entry = ttk.Entry(sec_seq)
        self.build_seq2_entry.insert(0, "A, B, D, E, C, F")
        self.build_seq2_entry.pack(fill=tk.X, pady=(0, 6))

        # Real-time suggestions/validation status
        self.validation_frame = ttk.Frame(sec_seq, style="Card.TFrame", padding=6)
        self.validation_frame.pack(fill=tk.X, pady=(2, 8))
        self.lbl_val_msg = ttk.Label(
            self.validation_frame,
            text="Sequences ready to build.",
            style="Muted.TLabel",
            wraplength=self.PANEL_WIDTH - 50,
        )
        self.lbl_val_msg.pack(fill=tk.X)

        # Action Buttons
        row_actions = ttk.Frame(panel, style="Sidebar.TFrame")
        row_actions.pack(fill=tk.X, pady=(4, 4))

        ttk.Button(
            row_actions,
            text="Build & Animate",
            style="Primary.TButton",
            command=self._handle_build_animate,
        ).pack(fill=tk.X, pady=(0, 4))

        row_sub = ttk.Frame(panel, style="Sidebar.TFrame")
        row_sub.pack(fill=tk.X)
        ttk.Button(
            row_sub,
            text="Random Pair",
            style="TButton",
            command=self._handle_build_random,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.build_label_cb = ttk.Combobox(
            row_sub,
            values=["Letters", "Numbers"],
            state="readonly",
            width=8,
        )
        self.build_label_cb.current(0)
        self.build_label_cb.pack(side=tk.RIGHT, padx=(3, 0))

    # =========================================================================
    # Helpers & Handlers
    # =========================================================================

    def _create_section(self, parent: ttk.Frame, title: str) -> ttk.Frame:
        """Create a styled group section with header."""
        frame = ttk.Frame(parent, style="Sidebar.TFrame", padding=(0, 6))
        frame.pack(fill=tk.X)

        lbl = ttk.Label(
            frame,
            text=title,
            style="Header.TLabel",
            font=get_ui_font(10, bold=True),
        )
        lbl.pack(anchor="w", pady=(0, 4))
        return frame

    def update_properties(self, props: Dict[str, Any]) -> None:
        """Update property values in binary tree properties card."""
        for k, v in props.items():
            if k in self.props_labels:
                if isinstance(v, bool):
                    text = "Yes" if v else "No"
                else:
                    text = str(v)
                self.props_labels[k].configure(text=text)

    def on_theme_updated(self, theme: Dict[str, str]) -> None:
        """Update canvas container background on theme switch."""
        self.canvas_container.configure(bg=theme["bg_panel"])

    # Handler routing to callbacks dict
    def _handle_bst_random(self) -> None:
        cb = self.callbacks.get("bst_random")
        if cb:
            try:
                n = int(self.bst_count_entry.get().strip())
            except ValueError:
                n = 7
            cb(n)

    def _handle_bst_load_array(self) -> None:
        cb = self.callbacks.get("bst_load_array")
        if cb:
            cb(self.bst_array_entry.get().strip())

    def _handle_preset_selected(self, event: tk.Event) -> None:
        idx = self.bst_preset_cb.current()
        preset_ids = ["", "balanced_bst", "skewed_bst", "duplicate_bst", "full_binary_tree"]
        if idx > 0 and idx < len(preset_ids):
            cb = self.callbacks.get("load_preset")
            if cb:
                cb(preset_ids[idx])

    def _handle_bst_insert(self) -> None:
        cb = self.callbacks.get("bst_insert")
        if cb:
            cb(self.bst_insert_entry.get().strip())

    def _handle_bst_search(self) -> None:
        cb = self.callbacks.get("bst_search")
        if cb:
            cb(self.bst_search_entry.get().strip())

    def _handle_bst_remove(self) -> None:
        cb = self.callbacks.get("bst_remove")
        if cb:
            cb(self.bst_remove_entry.get().strip())

    def _handle_bst_min(self) -> None:
        cb = self.callbacks.get("bst_min")
        if cb:
            cb()

    def _handle_bst_max(self) -> None:
        cb = self.callbacks.get("bst_max")
        if cb:
            cb()

    def _handle_bst_pred(self) -> None:
        cb = self.callbacks.get("bst_predecessor")
        if cb:
            cb(self.bst_ps_entry.get().strip())

    def _handle_bst_succ(self) -> None:
        cb = self.callbacks.get("bst_successor")
        if cb:
            cb(self.bst_ps_entry.get().strip())

    def _handle_bst_rank(self) -> None:
        cb = self.callbacks.get("bst_rank")
        if cb:
            cb(self.bst_rank_entry.get().strip())

    def _handle_bst_select(self) -> None:
        cb = self.callbacks.get("bst_select")
        if cb:
            try:
                k = int(self.bst_select_entry.get().strip())
            except ValueError:
                k = 1
            cb(k)

    def _handle_binary_random(self) -> None:
        cb = self.callbacks.get("binary_random")
        if cb:
            try:
                n = int(self.bt_count_entry.get().strip())
            except ValueError:
                n = 6
            cb(n, self.bt_label_type_var.get())

    def _handle_binary_load(self) -> None:
        cb = self.callbacks.get("binary_load_level_order")
        if cb:
            cb(self.bt_level_entry.get().strip())

    def _handle_traversal(self, order: str) -> None:
        cb = self.callbacks.get("run_traversal")
        if cb:
            cb(order)

    def _get_build_mode_key(self) -> str:
        modes = ["in+pre", "in+post", "in+level", "pre+post", "bst-pre", "bst-post"]
        return modes[self.build_mode_cb.current()]

    def _handle_build_mode_changed(self, event: tk.Event) -> None:
        mode = self._get_build_mode_key()
        if mode == "pre+post":
            self.ambiguity_banner.pack(fill=tk.X, pady=(2, 4))
        else:
            self.ambiguity_banner.pack_forget()

        if mode in ("bst-pre", "bst-post"):
            self.lbl_seq1.configure(text="Preorder / Postorder Sequence:")
            self.lbl_seq2.pack_forget()
            self.build_seq2_entry.pack_forget()
        else:
            self.lbl_seq1.configure(text="Inorder Sequence:")
            self.lbl_seq2.pack(anchor="w", pady=(2, 1))
            self.build_seq2_entry.pack(fill=tk.X, pady=(0, 6))

    def _handle_build_animate(self) -> None:
        cb = self.callbacks.get("build_reconstruct")
        if cb:
            mode = self._get_build_mode_key()
            s1 = self.build_seq1_entry.get().strip()
            s2 = self.build_seq2_entry.get().strip() if mode not in ("bst-pre", "bst-post") else None
            cb(mode, s1, s2)

    def _handle_build_random(self) -> None:
        cb = self.callbacks.get("build_random")
        if cb:
            mode = self._get_build_mode_key()
            label_type = "letters" if self.build_label_cb.get() == "Letters" else "numbers"
            cb(mode, label_type)
