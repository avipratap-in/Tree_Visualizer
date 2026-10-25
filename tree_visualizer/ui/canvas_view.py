"""Central interactive canvas viewport.

Renders:
- Deterministic, collision-free binary tree visualization with pan and zoom.
- Definition cards in cursive Rouge Script when the active tree is empty.
- Overlaid floating controls:
  - Top-left stats badge: [N=.., h=..]
  - Top-right zoom controls: [+ | 100% | - | ⟲]
  - Top-center visited sequence banner: Visited: [ ... ]
  - Bottom-right VisuAlgo status card and pseudocode panel
  - Left edge toggle button: [☰ Operations] when sidebar is collapsed
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.properties import height as compute_height, size as compute_size
from tree_visualizer.recorder.steps import Step
from tree_visualizer.ui.fonts import (
    get_definition_body_font,
    get_definition_title_font,
    get_ui_font,
)
from tree_visualizer.ui.overlays import PseudocodePanel, StatusBox
from tree_visualizer.ui.theme import ThemeManager


class CanvasView(tk.Frame):
    """Central canvas container with pan/zoom math and floating overlay panels."""

    LOGICAL_WIDTH: float = 900.0
    LOGICAL_HEIGHT: float = 500.0
    MARGIN_X: float = 60.0
    MARGIN_Y: float = 60.0
    NODE_RADIUS: float = 20.0

    BUTTON_STEP: float = 1.1
    MIN_SCALE: float = 0.3
    MAX_SCALE: float = 3.0

    DEFINITION_TEXTS: Dict[str, Dict[str, str]] = {
        "binary": {
            "title": "Binary Tree",
            "body": (
                "A binary tree is a hierarchical data structure in which every node "
                "has at most two children, called the left child and the right child. "
                "Formally, it is either empty or consists of a root node together with "
                "a left subtree and a right subtree, each of which is itself a binary tree."
            ),
            "hint": "Use the panel on the left to create a tree.",
        },
        "bst": {
            "title": "Binary Search Tree (BST)",
            "body": (
                "A binary search tree is a binary tree in which, for every node, all values "
                "in its left subtree are smaller than the node's value and all values in its "
                "right subtree are greater. Because of this ordering, an inorder traversal "
                "visits the values in sorted order, and search, insert and remove take O(h) "
                "time, where h is the height of the tree."
            ),
            "hint": "Use the panel on the left to create a tree.",
        },
        "build": {
            "title": "Build from Traversal",
            "body": (
                "A binary tree can be reconstructed from two of its traversal sequences. "
                "The inorder sequence together with the preorder, postorder or level-order "
                "sequence identifies the tree uniquely, as long as all values are distinct. "
                "Preorder with postorder alone is unique only for full binary trees."
            ),
            "hint": "Use the panel on the left to create a tree.",
        },
    }

    def __init__(
        self,
        master: tk.Widget,
        theme_manager: ThemeManager,
        on_expand_sidebar: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.theme_manager: ThemeManager = theme_manager
        self.on_expand_sidebar: Optional[Callable[[], None]] = on_expand_sidebar

        # Pan and Zoom state
        self.scale: float = 1.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self._drag_start_x: float = 0.0
        self._drag_start_y: float = 0.0

        # Current view data
        self.active_tab: str = "bst"
        self.current_step: Optional[Step] = None
        self.current_tree: Optional[TreeNode] = None

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_updated)

    def _build_ui(self) -> None:
        t = self.theme_manager.current

        # Main Tkinter Canvas
        self.canvas = tk.Canvas(
            self,
            bg=t["canvas_bg"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Pan & Zoom bindings
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # -------------------------------------------------------------
        # Floating Overlays
        # -------------------------------------------------------------

        # 1. Left Edge Collapsed Toggle Button (☰ Operations)
        self.btn_open_sidebar = ttk.Button(
            self.canvas,
            text="☰ Operations",
            style="Action.TButton",
            command=self._handle_expand_sidebar,
        )

        # 2. Top-Left Stats Badge [N=0, h=0]
        self.stats_frame = tk.Frame(
            self.canvas,
            bg=t["bg_panel"],
            bd=1,
            relief="solid",
            padx=8,
            pady=4,
        )
        self.lbl_stats = tk.Label(
            self.stats_frame,
            text="N=0, h=0",
            bg=t["bg_panel"],
            fg=t["text_main"],
            font=get_ui_font(9, bold=True),
        )
        self.lbl_stats.pack()

        # 3. Top-Right Zoom Controls [+ | 100% | - | ⟲]
        self.zoom_frame = tk.Frame(
            self.canvas,
            bg=t["bg_panel"],
            bd=1,
            relief="solid",
            padx=4,
            pady=3,
        )
        self.btn_zoom_in = ttk.Button(
            self.zoom_frame,
            text="+",
            width=2,
            style="Action.TButton",
            command=self.zoom_in,
        )
        self.btn_zoom_in.pack(side=tk.LEFT, padx=1)

        self.lbl_zoom = tk.Label(
            self.zoom_frame,
            text="100%",
            bg=t["bg_panel"],
            fg=t["text_main"],
            font=get_ui_font(8, bold=True),
            width=5,
        )
        self.lbl_zoom.pack(side=tk.LEFT, padx=2)

        self.btn_zoom_out = ttk.Button(
            self.zoom_frame,
            text="−",
            width=2,
            style="Action.TButton",
            command=self.zoom_out,
        )
        self.btn_zoom_out.pack(side=tk.LEFT, padx=1)

        self.btn_zoom_reset = ttk.Button(
            self.zoom_frame,
            text="⟲",
            width=2,
            style="Action.TButton",
            command=self.reset_view,
        )
        self.btn_zoom_reset.pack(side=tk.LEFT, padx=1)

        # 4. Top-Center Visited Sequence Banner
        self.visited_banner = tk.Frame(
            self.canvas,
            bg=t["bg_panel"],
            bd=1,
            relief="solid",
            padx=12,
            pady=4,
        )
        self.lbl_visited = tk.Label(
            self.visited_banner,
            text="Visited: []",
            bg=t["bg_panel"],
            fg=t["accent"],
            font=get_ui_font(10, bold=True),
        )
        self.lbl_visited.pack()

        # 5. Bottom-Right VisuAlgo Status Box & Pseudocode Panel
        self.overlay_container = tk.Frame(self.canvas, bg=t["canvas_bg"])
        self.status_box = StatusBox(self.overlay_container, self.theme_manager)
        self.status_box.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))

        self.pseudocode_panel = PseudocodePanel(self.overlay_container, self.theme_manager)
        self.pseudocode_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.redraw()

    # =========================================================================
    # Pan & Zoom Logic
    # =========================================================================

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event: tk.Event) -> None:
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self.pan_x += dx
        self.pan_y += dy
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.redraw()

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        factor = self.BUTTON_STEP if event.delta > 0 else (1.0 / self.BUTTON_STEP)
        self._apply_zoom(factor, event.x, event.y)

    def zoom_in(self) -> None:
        cx = self.canvas.winfo_width() / 2.0
        cy = self.canvas.winfo_height() / 2.0
        self._apply_zoom(self.BUTTON_STEP, cx, cy)

    def zoom_out(self) -> None:
        cx = self.canvas.winfo_width() / 2.0
        cy = self.canvas.winfo_height() / 2.0
        self._apply_zoom(1.0 / self.BUTTON_STEP, cx, cy)

    def _apply_zoom(self, factor: float, cx: float, cy: float) -> None:
        new_scale = max(self.MIN_SCALE, min(self.scale * factor, self.MAX_SCALE))
        if new_scale == self.scale:
            return

        # Zoom centered on cursor position (cx, cy)
        ratio = new_scale / self.scale
        self.pan_x = cx - ratio * (cx - self.pan_x)
        self.pan_y = cy - ratio * (cy - self.pan_y)
        self.scale = new_scale
        self.lbl_zoom.configure(text=f"{int(round(self.scale * 100))}%")
        self.redraw()

    def reset_view(self) -> None:
        """Reset pan and zoom to default scale 1.0 and origin."""
        self.scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.lbl_zoom.configure(text="100%")
        self.redraw()

    def set_sidebar_collapsed(self, is_collapsed: bool) -> None:
        """Show or hide the ☰ Operations button based on sidebar collapse state."""
        if is_collapsed:
            self.canvas.create_window(12, 12, window=self.btn_open_sidebar, anchor="nw", tags="overlay")
        else:
            self.btn_open_sidebar.place_forget()
        self.redraw()

    def _handle_expand_sidebar(self) -> None:
        if self.on_expand_sidebar:
            self.on_expand_sidebar()

    # =========================================================================
    # Drawing Pipeline
    # =========================================================================

    def set_tab(self, tab: str) -> None:
        """Update active tab and refresh canvas."""
        self.active_tab = tab
        self.redraw()

    def set_tree(self, tree: Optional[TreeNode]) -> None:
        """Set current tree model directly."""
        self.current_tree = tree
        self.current_step = None
        self.redraw()

    def set_step(self, step: Optional[Step]) -> None:
        """Render an algorithm animation Step."""
        self.current_step = step
        if step is not None:
            self.current_tree = step.tree_root
            if step.message:
                self.status_box.set_message(step.message)
            if step.pseudo_line is not None:
                self.pseudocode_panel.highlight_line(step.pseudo_line)
        self.redraw()

    def set_pseudocode(self, lines: List[str], active_idx: Optional[int] = None) -> None:
        """Update pseudocode lines on the overlay."""
        self.pseudocode_panel.set_pseudocode(lines, active_idx)
        if not lines:
            self.pseudocode_panel.pack_forget()
        else:
            self.pseudocode_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def redraw(self) -> None:
        """Redraw all canvas elements, trees, and floating overlays."""
        self.canvas.delete("all")
        t = self.theme_manager.current

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        # Position Floating Overlays
        # 1. Stats Badge (Top Left, or offset if sidebar toggle is present)
        stats_x = 120 if self.btn_open_sidebar.winfo_ismapped() else 12
        self.canvas.create_window(stats_x, 12, window=self.stats_frame, anchor="nw", tags="overlay")

        # 2. Zoom Controls (Top Right)
        self.canvas.create_window(w - 12, 12, window=self.zoom_frame, anchor="ne", tags="overlay")

        # 3. Visited Banner (Top Center)
        visited = self.current_step.visited if (self.current_step and self.current_step.visited) else []
        if visited:
            vis_str = ", ".join(str(v) for v in visited)
            self.lbl_visited.configure(text=f"Visited: [ {vis_str} ]")
            self.canvas.create_window(w / 2, 16, window=self.visited_banner, anchor="n", tags="overlay")
        else:
            self.visited_banner.place_forget()

        # 4. Status & Pseudocode Overlays (Bottom Right)
        self.canvas.create_window(w - 16, h - 16, window=self.overlay_container, anchor="se", tags="overlay")

        # Update stats badge
        tree_root = self.current_tree
        n = compute_size(tree_root)
        tree_h = compute_height(tree_root)
        self.lbl_stats.configure(text=f"N={n}, h={tree_h}")

        # Render Tree or Empty Definition Card
        if tree_root is None:
            self._draw_definition_card(w, h)
        else:
            self._draw_tree(tree_root, w, h)

    def _draw_definition_card(self, w: float, h: float) -> None:
        """Render empty-state academic definition card in cursive Rouge Script."""
        t = self.theme_manager.current
        card_info = self.DEFINITION_TEXTS.get(self.active_tab, self.DEFINITION_TEXTS["bst"])

        cx = w / 2.0 + self.pan_x
        cy = h / 2.0 + self.pan_y - 30

        # Title in Rouge Script
        title_font = get_definition_title_font(int(28 * self.scale))
        self.canvas.create_text(
            cx,
            cy - 50 * self.scale,
            text=card_info["title"],
            font=title_font,
            fill=t["accent"],
            justify=tk.CENTER,
        )

        # Body in Rouge Script
        body_font = get_definition_body_font(int(17 * self.scale))
        max_width = min(680 * self.scale, w * 0.85)
        self.canvas.create_text(
            cx,
            cy + 20 * self.scale,
            text=card_info["body"],
            font=body_font,
            fill=t["text_muted"],
            width=max_width,
            justify=tk.CENTER,
        )

        # Actionable hint
        hint_font = get_ui_font(max(8, int(10 * self.scale)), italic=True)
        self.canvas.create_text(
            cx,
            cy + 95 * self.scale,
            text=card_info["hint"],
            font=hint_font,
            fill=t["text_muted"],
            justify=tk.CENTER,
        )

    def _draw_tree(self, root: TreeNode, w: float, h: float) -> None:
        """Calculate coordinates and render tree nodes and edges."""
        t = self.theme_manager.current

        # 1. Inorder sequence indexing
        inorder_nodes: List[TreeNode] = []
        depths: Dict[str, int] = {}

        def _traverse(node: Optional[TreeNode], depth: int) -> None:
            if node is None:
                return
            depths[node.node_id] = depth
            _traverse(node.left, depth + 1)
            inorder_nodes.append(node)
            _traverse(node.right, depth + 1)

        _traverse(root, depth=0)
        n = len(inorder_nodes)
        d_max = max(depths.values()) if depths else 0

        # 2. Coordinate calculations matching SPEC section 4
        usable_w = self.LOGICAL_WIDTH - 2 * self.MARGIN_X
        if d_max == 0:
            level_h = 0.0
        else:
            level_h = min(85.0, (self.LOGICAL_HEIGHT - 2 * self.MARGIN_Y) / d_max)

        coords: Dict[str, Tuple[float, float]] = {}
        for idx, node in enumerate(inorder_nodes):
            if n == 1:
                lx = self.LOGICAL_WIDTH / 2.0
            else:
                lx = self.MARGIN_X + (idx / float(n - 1)) * usable_w
            ly = self.MARGIN_Y + depths[node.node_id] * level_h
            coords[node.node_id] = (lx, ly)

        # Highlight sets from current step
        highlight_nodes: Set[str] = set()
        visited_nodes: Set[str] = set()
        highlight_edges: Set[Tuple[str, str]] = set()

        if self.current_step is not None:
            highlight_nodes = set(self.current_step.highlight_nodes)
            visited_nodes = {str(v) for v in self.current_step.visited}
            highlight_edges = set(self.current_step.highlight_edges)

        # Transform logical coords to canvas view coords
        def _to_view(lx: float, ly: float) -> Tuple[float, float]:
            vx = lx * self.scale + self.pan_x
            vy = ly * self.scale + self.pan_y
            return vx, vy

        # 3. Draw Edges first (underneath nodes)
        def _draw_edges(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            p_id = node.node_id
            px, py = _to_view(*coords[p_id])

            for child in (node.left, node.right):
                if child is not None:
                    c_id = child.node_id
                    cx, cy = _to_view(*coords[c_id])
                    is_edge_hl = (p_id, c_id) in highlight_edges or (c_id, p_id) in highlight_edges
                    edge_color = t["edge_highlight"] if is_edge_hl else t["edge_default"]
                    edge_width = max(1, int(3 * self.scale if is_edge_hl else 2 * self.scale))

                    self.canvas.create_line(
                        px, py, cx, cy,
                        fill=edge_color,
                        width=edge_width,
                    )
                    _draw_edges(child)

        _draw_edges(root)

        # 4. Draw Nodes
        r = self.NODE_RADIUS * self.scale
        for node in inorder_nodes:
            vx, vy = _to_view(*coords[node.node_id])

            is_hl = node.node_id in highlight_nodes or str(node.val) in highlight_nodes
            is_vis = str(node.val) in visited_nodes

            if is_hl:
                fill_col = t["node_highlight"]
            elif is_vis:
                fill_col = t["node_visited"]
            else:
                fill_col = t["node_default"]

            stroke_w = max(1, int(2 * self.scale))
            self.canvas.create_oval(
                vx - r, vy - r, vx + r, vy + r,
                fill=fill_col,
                outline=t["node_stroke"],
                width=stroke_w,
            )

            # Node label text: "val" or "val-freq"
            label_text = f"{node.val}-{node.freq}" if node.freq > 1 else f"{node.val}"
            font_size = max(7, int(10 * self.scale))
            font = get_ui_font(font_size, bold=True)
            self.canvas.create_text(
                vx, vy,
                text=label_text,
                fill=t["node_text"],
                font=font,
            )

    def on_theme_updated(self, theme: Dict[str, str]) -> None:
        """Update canvas and floating overlay backgrounds on theme change."""
        self.canvas.configure(bg=theme["canvas_bg"])
        self.stats_frame.configure(bg=theme["bg_panel"], highlightbackground=theme["border_color"])
        self.lbl_stats.configure(bg=theme["bg_panel"], fg=theme["text_main"])
        self.zoom_frame.configure(bg=theme["bg_panel"], highlightbackground=theme["border_color"])
        self.lbl_zoom.configure(bg=theme["bg_panel"], fg=theme["text_main"])
        self.visited_banner.configure(bg=theme["bg_panel"], highlightbackground=theme["border_color"])
        self.lbl_visited.configure(bg=theme["bg_panel"], fg=theme["accent"])
        self.overlay_container.configure(bg=theme["canvas_bg"])
        self.redraw()
