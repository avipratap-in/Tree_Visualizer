"""Pure tree layout mathematics and collision-free coordinate computation.

Implements deterministic tree layout based on Inorder sequence and depth:
- x: assigned proportionally from Inorder traversal sequence index [0, n - 1]
- y: calculated from node depth and clamped level height
- Zero Tkinter dependencies: purely algorithmic geometry.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from tree_visualizer.core.node import TreeNode

CANVAS_WIDTH: float = 900.0
CANVAS_HEIGHT: float = 500.0
MARGIN_X: float = 60.0
MARGIN_Y: float = 60.0
MAX_LEVEL_HEIGHT: float = 85.0
NODE_RADIUS: float = 20.0


@dataclass
class NodeLayout:
    """Computed 2D layout coordinates and display attributes for a single node."""

    node_id: str
    val: Any
    freq: int
    x: float
    y: float
    radius: float = NODE_RADIUS
    depth: int = 0
    inorder_index: int = 0
    label_text: str = ""

    def __post_init__(self) -> None:
        if not self.label_text:
            self.label_text = f"{self.val}-{self.freq}" if self.freq > 1 else str(self.val)


@dataclass
class EdgeLayout:
    """Computed connecting line between parent and child nodes."""

    parent_id: str
    child_id: str
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class TreeLayoutResult:
    """Complete computed layout for a binary tree."""

    nodes: Dict[str, NodeLayout] = field(default_factory=dict)
    edges: List[EdgeLayout] = field(default_factory=list)
    node_count: int = 0
    max_depth: int = 0
    canvas_width: float = CANVAS_WIDTH
    canvas_height: float = CANVAS_HEIGHT

    def get_node(self, node_id: str) -> Optional[NodeLayout]:
        """Lookup node layout by unique node identifier."""
        return self.nodes.get(node_id)


def compute_tree_layout(
    root: Optional[TreeNode],
    canvas_width: float = CANVAS_WIDTH,
    canvas_height: float = CANVAS_HEIGHT,
    margin_x: float = MARGIN_X,
    margin_y: float = MARGIN_Y,
    max_level_height: float = MAX_LEVEL_HEIGHT,
    node_radius: float = NODE_RADIUS,
) -> TreeLayoutResult:
    """Compute deterministic 2D coordinates for all nodes and edges in a binary tree.

    Algorithm:
    1. Perform inorder traversal to order nodes left-to-right (index i in [0, n - 1]).
    2. Track node depth d where root depth d = 0, and determine maximum depth d_max.
    3. Calculate horizontal position:
       - If n == 1: x = canvas_width / 2
       - If n > 1: x = margin_x + (i / (n - 1)) * (canvas_width - 2 * margin_x)
    4. Calculate level height and vertical position:
       - level_height = 0 if d_max == 0 else min(max_level_height, (canvas_height - 2 * margin_y) / d_max)
       - y = margin_y + d * level_height

    Complexity:
    - Time: O(n) where n is number of nodes in tree.
    - Space: O(n) for layout dictionaries and edge lists.
    """
    if root is None:
        return TreeLayoutResult(
            nodes={},
            edges=[],
            node_count=0,
            max_depth=0,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        )

    # 1. Inorder traversal to gather nodes and track depths
    inorder_nodes: List[TreeNode] = []
    depths: Dict[str, int] = {}

    def _traverse(node: Optional[TreeNode], current_depth: int) -> None:
        if node is None:
            return
        depths[node.node_id] = current_depth
        _traverse(node.left, current_depth + 1)
        inorder_nodes.append(node)
        _traverse(node.right, current_depth + 1)

    _traverse(root, current_depth=0)

    n = len(inorder_nodes)
    d_max = max(depths.values()) if depths else 0
    usable_width = canvas_width - 2 * margin_x

    # 2. Level height calculation
    if d_max == 0:
        level_height = 0.0
    else:
        usable_height = canvas_height - 2 * margin_y
        level_height = min(max_level_height, usable_height / float(d_max))

    # 3. Position calculation
    nodes_map: Dict[str, NodeLayout] = {}
    for idx, node in enumerate(inorder_nodes):
        if n == 1:
            x = canvas_width / 2.0
        else:
            x = margin_x + (idx / float(n - 1)) * usable_width

        y = margin_y + depths[node.node_id] * level_height
        label = f"{node.val}-{node.freq}" if node.freq > 1 else str(node.val)

        nodes_map[node.node_id] = NodeLayout(
            node_id=node.node_id,
            val=node.val,
            freq=node.freq,
            x=x,
            y=y,
            radius=node_radius,
            depth=depths[node.node_id],
            inorder_index=idx,
            label_text=label,
        )

    # 4. Edge list generation
    edges_list: List[EdgeLayout] = []

    def _collect_edges(curr: Optional[TreeNode]) -> None:
        if curr is None:
            return
        p_layout = nodes_map[curr.node_id]
        for child in (curr.left, curr.right):
            if child is not None:
                c_layout = nodes_map[child.node_id]
                edges_list.append(
                    EdgeLayout(
                        parent_id=curr.node_id,
                        child_id=child.node_id,
                        x1=p_layout.x,
                        y1=p_layout.y,
                        x2=c_layout.x,
                        y2=c_layout.y,
                    )
                )
                _collect_edges(child)

    _collect_edges(root)

    return TreeLayoutResult(
        nodes=nodes_map,
        edges=edges_list,
        node_count=n,
        max_depth=d_max,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
    )
