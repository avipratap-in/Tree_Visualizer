"""Collapsible Operations Sidebar for Tree_Visualizer.

Contains dedicated controls for:
- BST Tab: Random/Array creation, Presets, Insert, Search, Remove, Min/Max, Pred/Succ, Rank/Select.
- Binary Tree Tab: Random generation (numeric/alphabetic remembered), Lenient Level-order loader
  with "Interpreted as: ..." hint, Traversals, Properties card grid.
- Build from Traversal Tab: Mode selection, Sequence inputs, Live validation/diagnostics, Build & Animate.
- Operation button disabling during animation playback.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional
from tree_visualizer.core.parsing import parse_level_order
from tree_visualizer.core.suggestions import diagnose_sequences
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
        initial_bt_label_type: str = "numbers",
        **kwargs,
    ) -> None:
        super().__init__(master, style="Sidebar.TFrame", width=self.PANEL_WIDTH, **kwargs)
        self.theme_manager: ThemeManager = theme_manager
        self.on_collapse_toggled: Optional[Callable[[bool], None]] = on_collapse_toggled
        self.initial_bt_label_type: str = initial_bt_label_type
        self.is_collapsed: bool = False
        self.active_tab: str = "bst"

        # List of all action buttons to enable/disable during animation playback
        self.operation_buttons: List[ttk.Button] = []

        # Callbacks hooked to Controller
        self.callbacks: Dict[str, Callable[..., Any]] = {}

        # Real-time debounce timer ID for reconstruction sequence validation
        self._build_debounce_timer: Optional[str] = None

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

        self.canvas_container.yview_moveto(0)

    set_active_tab = set_tab

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

    def set_operations_enabled(self, enabled: bool) -> None:
        """Disable operation buttons while animation plays; re-enable when stopped."""
        state = "normal" if enabled else "disabled"
        for btn in self.operation_buttons:
            try:
                btn.configure(state=state)
            except Exception:
                pass

    # =========================================================================
    # BST Panel UI
    # =========================================================================

    def _build_bst_panel(self) -> None:
        panel = ttk.Frame(self.scrollable_frame, style="Sidebar.TFrame")
        self.panels["bst"] = panel

        # Section: Create BST
        sec_create = self._create_section(panel, "Create BST")

        # Random BST (Count 1..25, default 7)
        row_rnd = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_rnd.pack(fill=tk.X, pady=(2, 6))
        ttk.Label(row_rnd, text="Count N:", style="Panel.TLabel").pack(side=tk.LEFT)
        self.bst_count_entry = ttk.Entry(row_rnd, width=5)
        self.bst_count_entry.insert(0, "7")
        self.bst_count_entry.pack(side=tk.LEFT, padx=6)

        btn_rnd = ttk.Button(
            row_rnd,
            text="Random",
            style="TButton",
            command=self._handle_bst_random,
        )
        btn_rnd.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.operation_buttons.append(btn_rnd)

        # Custom Array Load
        row_arr = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_arr.pack(fill=tk.X, pady=(2, 6))
        self.bst_array_entry = ttk.Entry(row_arr)
        self.bst_array_entry.insert(0, "50, 30, 70, 20")
        self.bst_array_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_load = ttk.Button(
            row_arr,
            text="Load",
            style="TButton",
            command=self._handle_bst_load_array,
        )
        btn_load.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_load)

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
                "4. Full & Perfect Binary Tree",
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

        btn_ins = ttk.Button(
            row_ins,
            text="Insert",
            style="Primary.TButton",
            command=self._handle_bst_insert,
        )
        btn_ins.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_ins)

        # Section: Search & Remove
        sec_sr = self._create_section(panel, "Search & Remove")
        row_search = ttk.Frame(sec_sr, style="Sidebar.TFrame")
        row_search.pack(fill=tk.X, pady=(0, 4))
        self.bst_search_entry = ttk.Entry(row_search)
        self.bst_search_entry.insert(0, "50")
        self.bst_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_search = ttk.Button(
            row_search,
            text="Search",
            style="TButton",
            command=self._handle_bst_search,
        )
        btn_search.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_search)

        row_remove = ttk.Frame(sec_sr, style="Sidebar.TFrame")
        row_remove.pack(fill=tk.X)
        self.bst_remove_entry = ttk.Entry(row_remove)
        self.bst_remove_entry.insert(0, "50")
        self.bst_remove_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_remove = ttk.Button(
            row_remove,
            text="Remove",
            style="Danger.TButton",
            command=self._handle_bst_remove,
        )
        btn_remove.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_remove)

        # Section: Min & Max
        sec_minmax = self._create_section(panel, "Min & Max")
        row_mm = ttk.Frame(sec_minmax, style="Sidebar.TFrame")
        row_mm.pack(fill=tk.X)

        btn_min = ttk.Button(
            row_mm,
            text="Find Min",
            style="TButton",
            command=self._handle_bst_min,
        )
        btn_min.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.operation_buttons.append(btn_min)

        btn_max = ttk.Button(
            row_mm,
            text="Find Max",
            style="TButton",
            command=self._handle_bst_max,
        )
        btn_max.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        self.operation_buttons.append(btn_max)

        # Section: Predecessor & Successor
        sec_ps = self._create_section(panel, "Predecessor & Successor")
        self.bst_ps_entry = ttk.Entry(sec_ps)
        self.bst_ps_entry.insert(0, "50")
        self.bst_ps_entry.pack(fill=tk.X, pady=(0, 4))
        row_ps_btns = ttk.Frame(sec_ps, style="Sidebar.TFrame")
        row_ps_btns.pack(fill=tk.X)

        btn_pred = ttk.Button(
            row_ps_btns,
            text="Predecessor",
            style="TButton",
            command=self._handle_bst_pred,
        )
        btn_pred.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.operation_buttons.append(btn_pred)

        btn_succ = ttk.Button(
            row_ps_btns,
            text="Successor",
            style="TButton",
            command=self._handle_bst_succ,
        )
        btn_succ.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        self.operation_buttons.append(btn_succ)

        # Section: Rank & Select
        sec_rs = self._create_section(panel, "Rank & Select")
        row_rank = ttk.Frame(sec_rs, style="Sidebar.TFrame")
        row_rank.pack(fill=tk.X, pady=(0, 4))
        self.bst_rank_entry = ttk.Entry(row_rank)
        self.bst_rank_entry.insert(0, "50")
        self.bst_rank_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_rank = ttk.Button(
            row_rank,
            text="Rank",
            style="TButton",
            command=self._handle_bst_rank,
        )
        btn_rank.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_rank)

        row_sel = ttk.Frame(sec_rs, style="Sidebar.TFrame")
        row_sel.pack(fill=tk.X)
        self.bst_select_entry = ttk.Entry(row_sel)
        self.bst_select_entry.insert(0, "3")
        self.bst_select_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_select = ttk.Button(
            row_sel,
            text="Select (k)",
            style="TButton",
            command=self._handle_bst_select,
        )
        btn_select.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_select)

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

        btn_rnd = ttk.Button(
            row_rnd,
            text="Random",
            style="TButton",
            command=self._handle_binary_random,
        )
        btn_rnd.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.operation_buttons.append(btn_rnd)

        row_lbl = ttk.Frame(sec_create, style="Sidebar.TFrame")
        row_lbl.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(row_lbl, text="Labels:", style="Panel.TLabel").pack(side=tk.LEFT)
        self.bt_label_type_var = tk.StringVar(value=self.initial_bt_label_type)
        r_num = ttk.Radiobutton(
            row_lbl,
            text="Numbers",
            variable=self.bt_label_type_var,
            value="numbers",
            command=self._on_label_type_toggle,
        )
        r_num.pack(side=tk.LEFT, padx=(6, 4))
        r_let = ttk.Radiobutton(
            row_lbl,
            text="Letters",
            variable=self.bt_label_type_var,
            value="letters",
            command=self._on_label_type_toggle,
        )
        r_let.pack(side=tk.LEFT)

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
        self.bt_level_entry.bind("<KeyRelease>", lambda e: self._update_binary_hint())

        btn_load = ttk.Button(
            row_load,
            text="Load",
            style="TButton",
            command=self._handle_binary_load,
        )
        btn_load.pack(side=tk.RIGHT)
        self.operation_buttons.append(btn_load)

        # Hint note: "Interpreted as: ..."
        self.bt_hint_label = ttk.Label(
            sec_create,
            text="Interpreted as: 1, 2, 3, 4, 5, 6",
            style="Muted.TLabel",
            font=get_ui_font(8, italic=True),
            wraplength=self.PANEL_WIDTH - 40,
        )
        self.bt_hint_label.pack(anchor="w", pady=(2, 4))

        # Section: Traversals
        sec_trav = self._create_section(panel, "Traversals")
        t_row1 = ttk.Frame(sec_trav, style="Sidebar.TFrame")
        t_row1.pack(fill=tk.X, pady=(0, 4))

        b_pre = ttk.Button(
            t_row1,
            text="Preorder",
            style="TButton",
            command=lambda: self._handle_traversal("pre"),
        )
        b_pre.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.operation_buttons.append(b_pre)

        b_in = ttk.Button(
            t_row1,
            text="Inorder",
            style="TButton",
            command=lambda: self._handle_traversal("in"),
        )
        b_in.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        self.operation_buttons.append(b_in)

        t_row2 = ttk.Frame(sec_trav, style="Sidebar.TFrame")
        t_row2.pack(fill=tk.X)

        b_post = ttk.Button(
            t_row2,
            text="Postorder",
            style="TButton",
            command=lambda: self._handle_traversal("post"),
        )
        b_post.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.operation_buttons.append(b_post)

        b_lvl = ttk.Button(
            t_row2,
            text="Level Order",
            style="TButton",
            command=lambda: self._handle_traversal("level"),
        )
        b_lvl.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        self.operation_buttons.append(b_lvl)

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

    def _on_label_type_toggle(self) -> None:
        """Handle numeric/alphabetic radio toggle and notify listener."""
        val = self.bt_label_type_var.get()
        cb = self.callbacks.get("bt_label_type_changed")
        if cb:
            cb(val)

    def _update_binary_hint(self) -> None:
        """Update the 'Interpreted as: ...' hint dynamically as user types."""
        raw = self.bt_level_entry.get().strip()
        parsed = parse_level_order(raw)
        if parsed.notes:
            self.bt_hint_label.configure(text=parsed.notes[0])
        else:
            self.bt_hint_label.configure(text="")

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

        # Ambiguity Warning Banner (Preorder + Postorder only)
        self.ambiguity_banner = tk.Label(
            sec_mode,
            text="⚠️ Ambiguity Note: Preorder + Postorder only uniquely reconstructs Full Binary Trees (where every node has 0 or 2 children). Any single-child node will trigger an ambiguity error.",
            bg="#fef08a",
            fg="#854d0e",
            font=get_ui_font(8),
            wraplength=self.PANEL_WIDTH - 40,
            justify=tk.LEFT,
            padx=8,
            pady=6,
            bd=1,
            relief="solid",
        )

        # Section: Sequences
        self.sec_seq = self._create_section(panel, "Sequences")

        # Sequence 1
        self.lbl_seq1 = ttk.Label(self.sec_seq, text="Inorder Sequence:", style="Panel.TLabel")
        self.lbl_seq1.pack(anchor="w", pady=(2, 1))

        self.build_seq1_entry = ttk.Entry(self.sec_seq)
        self.build_seq1_entry.insert(0, "D, B, E, A, C")
        self.build_seq1_entry.pack(fill=tk.X, pady=(0, 2))
        self.build_seq1_entry.bind("<KeyRelease>", lambda e: self._trigger_build_validation())

        self.build_seq1_hint = tk.Label(
            self.sec_seq,
            text="",
            font=get_ui_font(8, italic=True),
            wraplength=self.PANEL_WIDTH - 40,
            justify=tk.LEFT,
            anchor="w",
        )
        self.build_seq1_hint.pack(fill=tk.X, pady=(0, 6))

        # Sequence 2 Group
        self.build_seq2_group = ttk.Frame(self.sec_seq, style="Sidebar.TFrame")
        self.build_seq2_group.pack(fill=tk.X)

        self.lbl_seq2 = ttk.Label(self.build_seq2_group, text="Preorder Sequence:", style="Panel.TLabel")
        self.lbl_seq2.pack(anchor="w", pady=(2, 1))

        self.build_seq2_entry = ttk.Entry(self.build_seq2_group)
        self.build_seq2_entry.insert(0, "A, B, D, E, C")
        self.build_seq2_entry.pack(fill=tk.X, pady=(0, 2))
        self.build_seq2_entry.bind("<KeyRelease>", lambda e: self._trigger_build_validation())

        self.build_seq2_hint = tk.Label(
            self.build_seq2_group,
            text="",
            font=get_ui_font(8, italic=True),
            wraplength=self.PANEL_WIDTH - 40,
            justify=tk.LEFT,
            anchor="w",
        )
        self.build_seq2_hint.pack(fill=tk.X, pady=(0, 6))

        # Real-time Validation Card / Box
        self.build_val_box = tk.Frame(
            self.sec_seq,
            bd=1,
            relief="solid",
            padx=8,
            pady=6,
        )
        self.lbl_val_msg = tk.Label(
            self.build_val_box,
            text="",
            font=get_ui_font(8, bold=True),
            wraplength=self.PANEL_WIDTH - 50,
            justify=tk.LEFT,
            anchor="w",
        )
        self.lbl_val_msg.pack(fill=tk.X)

        self.build_suggestions_frame = tk.Frame(self.build_val_box)
        self.build_suggestions_frame.pack(fill=tk.X, pady=(4, 0))

        # Action Buttons
        row_actions = ttk.Frame(panel, style="Sidebar.TFrame")
        row_actions.pack(fill=tk.X, pady=(6, 4))

        self.btn_build_animate = ttk.Button(
            row_actions,
            text="Build & Animate",
            style="Primary.TButton",
            command=self._handle_build_animate,
        )
        self.btn_build_animate.pack(fill=tk.X, pady=(0, 4))
        self.operation_buttons.append(self.btn_build_animate)

        # Row: Random, Labels selector, Auto-run
        row_sub = ttk.Frame(panel, style="Sidebar.TFrame")
        row_sub.pack(fill=tk.X, pady=(2, 2))

        self.btn_build_random = ttk.Button(
            row_sub,
            text="Random",
            style="TButton",
            command=self._handle_build_random,
        )
        self.btn_build_random.pack(side=tk.LEFT, padx=(0, 4))
        self.operation_buttons.append(self.btn_build_random)

        ttk.Label(row_sub, text="Labels:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(2, 2))
        self.build_label_cb = ttk.Combobox(
            row_sub,
            values=["Letters A-Z", "Numbers 1-99"],
            state="readonly",
            width=11,
        )
        self.build_label_cb.current(0)
        self.build_label_cb.pack(side=tk.LEFT, padx=(0, 6))

        self.build_auto_run_var = tk.BooleanVar(value=False)
        self.chk_auto_run = ttk.Checkbutton(
            row_sub,
            text="Auto-run",
            variable=self.build_auto_run_var,
            style="TCheckbutton",
        )
        self.chk_auto_run.pack(side=tk.RIGHT)

        # Run initial mode update and validation
        self._update_build_mode_ui()
        self._perform_build_validation()

    def _trigger_build_validation(self) -> None:
        """Debounce real-time sequence validation by 300 ms."""
        if self._build_debounce_timer:
            try:
                self.after_cancel(self._build_debounce_timer)
            except Exception:
                pass
            self._build_debounce_timer = None
        self._build_debounce_timer = self.after(300, self._perform_build_validation)

    def _perform_build_validation(self) -> None:
        """Execute sequence diagnostics and update hints and validation box."""
        self._build_debounce_timer = None
        mode = self._get_build_mode_key()
        raw1 = self.build_seq1_entry.get().strip()
        is_two = mode in ("in+pre", "in+post", "in+level", "pre+post")
        raw2 = self.build_seq2_entry.get().strip() if is_two else None

        t = self.theme_manager.current
        bg_panel = t.get("bg_panel", "#1e293b")
        text_muted = t.get("text_muted", "#94a3b8")
        success_fg = "#10b981" if self.theme_manager.is_dark() else "#059669"
        error_fg = "#ef4444" if self.theme_manager.is_dark() else "#dc2626"

        # If both fields are empty, clear hints and hide box
        if not raw1 and (not is_two or not raw2):
            self.build_seq1_hint.configure(text="", bg=bg_panel, fg=text_muted)
            self.build_seq2_hint.configure(text="", bg=bg_panel, fg=text_muted)
            self.build_val_box.pack_forget()
            return

        diag = diagnose_sequences(mode, raw1, raw2)

        # 1. Update Sequence 1 Hint
        p1_tokens = diag.seq1.get("tokens", [])
        if p1_tokens:
            note = f" ({diag.seq1.get('notes', [''])[0]})" if diag.seq1.get("notes") else ""
            tok_str = ", ".join(str(x) for x in p1_tokens)
            if diag.valid:
                self.build_seq1_hint.configure(
                    text=f"✓ Interpreted as: {tok_str}{note}",
                    bg=bg_panel,
                    fg=success_fg,
                )
            else:
                self.build_seq1_hint.configure(
                    text=f"Interpreted as: {tok_str}{note}",
                    bg=bg_panel,
                    fg=text_muted,
                )
        elif raw1:
            self.build_seq1_hint.configure(
                text="Empty or unparseable",
                bg=bg_panel,
                fg=error_fg,
            )
        else:
            self.build_seq1_hint.configure(text="", bg=bg_panel, fg=text_muted)

        # 2. Update Sequence 2 Hint (if 2-sequence mode)
        if is_two and diag.seq2 is not None:
            p2_tokens = diag.seq2.get("tokens", [])
            if p2_tokens:
                note = f" ({diag.seq2.get('notes', [''])[0]})" if diag.seq2.get("notes") else ""
                tok_str = ", ".join(str(x) for x in p2_tokens)
                if diag.valid:
                    self.build_seq2_hint.configure(
                        text=f"✓ Interpreted as: {tok_str}{note}",
                        bg=bg_panel,
                        fg=success_fg,
                    )
                else:
                    self.build_seq2_hint.configure(
                        text=f"Interpreted as: {tok_str}{note}",
                        bg=bg_panel,
                        fg=text_muted,
                    )
            elif raw2:
                self.build_seq2_hint.configure(
                    text="Empty or unparseable",
                    bg=bg_panel,
                    fg=error_fg,
                )
            else:
                self.build_seq2_hint.configure(text="", bg=bg_panel, fg=text_muted)
        else:
            self.build_seq2_hint.configure(text="", bg=bg_panel, fg=text_muted)

        # 3. Update Validation Box
        if diag.severity == "neutral" or not diag.message:
            self.build_val_box.pack_forget()
            return

        self.build_val_box.pack(fill=tk.X, pady=(2, 6))

        # Status card color styling
        is_dark = self.theme_manager.is_dark()
        if diag.severity == "success":
            card_bg = "#064e3b" if is_dark else "#f0fdf4"
            card_fg = "#6ee7b7" if is_dark else "#166534"
            card_bd = "#059669" if is_dark else "#86efac"
            icon = "✓"
        elif diag.severity == "warning":
            card_bg = "#422006" if is_dark else "#fef9c3"
            card_fg = "#fef08a" if is_dark else "#854d0e"
            card_bd = "#ca8a04" if is_dark else "#fde047"
            icon = "⚠️"
        elif diag.severity == "error":
            card_bg = "#450a0a" if is_dark else "#fee2e2"
            card_fg = "#fca5a5" if is_dark else "#991b1b"
            card_bd = "#dc2626" if is_dark else "#fca5a5"
            icon = "✕"
        else:
            card_bg = t.get("bg_panel_alt", "#334155")
            card_fg = t.get("text_main", "#f8fafc")
            card_bd = t.get("border_color", "#334155")
            icon = "ℹ"

        self.build_val_box.configure(bg=card_bg, highlightbackground=card_bd, highlightcolor=card_bd)
        self.lbl_val_msg.configure(text=f"{icon} {diag.message}", bg=card_bg, fg=card_fg)
        self.build_suggestions_frame.configure(bg=card_bg)

        # Re-render suggestion buttons
        for w in self.build_suggestions_frame.winfo_children():
            w.destroy()

        for s in diag.suggestions:
            stype = s.get("type")
            if stype == "replace":
                row = tk.Frame(self.build_suggestions_frame, bg=card_bg)
                row.pack(fill=tk.X, pady=2)
                f_name = "Sequence 1" if s.get("field") == "seq1" else "Sequence 2"
                lbl = tk.Label(
                    row,
                    text=f"Did you mean {f_name}: {s.get('value')}?",
                    bg=card_bg,
                    fg=card_fg,
                    font=get_ui_font(8),
                    wraplength=self.PANEL_WIDTH - 120,
                    justify=tk.LEFT,
                )
                lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

                btn = ttk.Button(
                    row,
                    text="Use this",
                    style="TButton",
                    command=lambda fld=s.get("field"), val=s.get("value"): self._apply_replace_suggestion(fld, val),
                )
                btn.pack(side=tk.RIGHT)
                self.operation_buttons.append(btn)

            elif stype == "swap_fields":
                btn = ttk.Button(
                    self.build_suggestions_frame,
                    text="⇄ Swap Sequences",
                    style="TButton",
                    command=self._apply_swap_suggestion,
                )
                btn.pack(fill=tk.X, pady=2)
                self.operation_buttons.append(btn)

            elif stype == "switch_mode":
                target_mode = s.get("mode")
                lbl_mode = s.get("label", target_mode)
                btn = ttk.Button(
                    self.build_suggestions_frame,
                    text=f"Switch mode to {lbl_mode}",
                    style="TButton",
                    command=lambda m=target_mode: self._apply_mode_suggestion(m),
                )
                btn.pack(fill=tk.X, pady=2)
                self.operation_buttons.append(btn)

    def _apply_replace_suggestion(self, field: Optional[str], value: Optional[str]) -> None:
        """Apply one-click replacement suggestion to specified sequence entry."""
        if not value:
            return
        if field == "seq1":
            self.build_seq1_entry.delete(0, tk.END)
            self.build_seq1_entry.insert(0, value)
        elif field == "seq2":
            self.build_seq2_entry.delete(0, tk.END)
            self.build_seq2_entry.insert(0, value)
        self._perform_build_validation()

    def _apply_swap_suggestion(self) -> None:
        """Swap contents of sequence 1 and sequence 2."""
        s1 = self.build_seq1_entry.get()
        s2 = self.build_seq2_entry.get()
        self.build_seq1_entry.delete(0, tk.END)
        self.build_seq1_entry.insert(0, s2)
        self.build_seq2_entry.delete(0, tk.END)
        self.build_seq2_entry.insert(0, s1)
        self._perform_build_validation()

    def _apply_mode_suggestion(self, mode_key: str) -> None:
        """Switch mode combobox to target mode key and update UI."""
        modes = ["in+pre", "in+post", "in+level", "pre+post", "bst-pre", "bst-post"]
        if mode_key in modes:
            self.build_mode_cb.current(modes.index(mode_key))
            self._update_build_mode_ui()
            self._perform_build_validation()

    # =========================================================================
    # Helpers & Handlers
    # =========================================================================

    def _create_section(self, parent: ttk.Frame, title: str) -> ttk.Frame:
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
                n = max(1, min(25, n))
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
        # Reset combobox to prompt title
        self.bst_preset_cb.current(0)

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
            label_type = self.bt_label_type_var.get()
            try:
                n = int(self.bt_count_entry.get().strip())
                max_n = 26 if label_type == "letters" else 30
                n = max(1, min(max_n, n))
            except ValueError:
                n = 6
            cb(n, label_type)

    def _handle_binary_load(self) -> None:
        cb = self.callbacks.get("binary_load_level_order")
        if cb:
            raw = self.bt_level_entry.get().strip()
            self._update_binary_hint()
            cb(raw)

    def _handle_traversal(self, order: str) -> None:
        cb = self.callbacks.get("run_traversal")
        if cb:
            cb(order)

    def _get_build_mode_key(self) -> str:
        modes = ["in+pre", "in+post", "in+level", "pre+post", "bst-pre", "bst-post"]
        return modes[self.build_mode_cb.current()]

    def _update_build_mode_ui(self) -> None:
        """Update sequence labels, visibility, and ambiguity banner based on mode."""
        mode = self._get_build_mode_key()
        if mode == "pre+post":
            self.ambiguity_banner.pack(fill=tk.X, pady=(2, 4))
        else:
            self.ambiguity_banner.pack_forget()

        if mode == "in+pre":
            self.lbl_seq1.configure(text="Inorder Sequence:")
            self.lbl_seq2.configure(text="Preorder Sequence:")
            self.build_seq2_group.pack(fill=tk.X)
        elif mode == "in+post":
            self.lbl_seq1.configure(text="Inorder Sequence:")
            self.lbl_seq2.configure(text="Postorder Sequence:")
            self.build_seq2_group.pack(fill=tk.X)
        elif mode == "in+level":
            self.lbl_seq1.configure(text="Inorder Sequence:")
            self.lbl_seq2.configure(text="Level Order Sequence:")
            self.build_seq2_group.pack(fill=tk.X)
        elif mode == "pre+post":
            self.lbl_seq1.configure(text="Preorder Sequence:")
            self.lbl_seq2.configure(text="Postorder Sequence:")
            self.build_seq2_group.pack(fill=tk.X)
        elif mode == "bst-pre":
            self.lbl_seq1.configure(text="Preorder Sequence (numbers or case-sensitive letters):")
            self.build_seq2_group.pack_forget()
        elif mode == "bst-post":
            self.lbl_seq1.configure(text="Postorder Sequence (numbers or case-sensitive letters):")
            self.build_seq2_group.pack_forget()

    def _handle_build_mode_changed(self, event: tk.Event) -> None:
        self._update_build_mode_ui()
        self._perform_build_validation()

    def _handle_build_animate(self) -> None:
        mode = self._get_build_mode_key()
        s1 = self.build_seq1_entry.get().strip()
        is_two = mode in ("in+pre", "in+post", "in+level", "pre+post")
        s2 = self.build_seq2_entry.get().strip() if is_two else None

        if not s1 or (is_two and not s2):
            cb_status = self.callbacks.get("show_status")
            if cb_status:
                cb_status("Please provide the required traversal sequence(s).", "warning")
            return

        cb = self.callbacks.get("build_reconstruct")
        if cb:
            cb(mode, s1, s2)

    def _handle_build_random(self) -> None:
        cb = self.callbacks.get("build_random")
        if cb:
            mode = self._get_build_mode_key()
            label_choice = self.build_label_cb.get()
            label_type = "letters" if "Letters" in label_choice else "numbers"
            s1, s2 = cb(mode, label_type)
            self.build_seq1_entry.delete(0, tk.END)
            self.build_seq1_entry.insert(0, s1)
            if s2 is not None:
                self.build_seq2_entry.delete(0, tk.END)
                self.build_seq2_entry.insert(0, s2)
            else:
                self.build_seq2_entry.delete(0, tk.END)
            self._perform_build_validation()

            if self.build_auto_run_var.get():
                self._handle_build_animate()
