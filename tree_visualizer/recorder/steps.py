"""Step recorder data definitions and serialization contracts.

Schema conforms to the animation player JSON contract:
{
  "operation": "<op_name>",
  "pseudocode": ["line 0", "line 1", ...],
  "steps": [
    {
      "tree": <nested node dict>,
      "highlight_nodes": [ids],
      "highlight_edges": [[parent_id, child_id]],
      "visited": [values collected so far],
      "message": "status text",
      "pseudo_line": <active index>,
      "stats": {"n": <node count>, "h": <height>}
    }
  ]
}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.properties import height, size


@dataclass
class Step:
    """Discrete animation step capturing an immutable tree snapshot and UI visual state."""

    tree: Optional[Dict[str, Any]] = None
    highlight_nodes: List[str] = field(default_factory=list)
    highlight_edges: List[Tuple[str, str]] = field(default_factory=list)
    visited: List[Any] = field(default_factory=list)
    message: str = ""
    pseudo_line: int = -1
    stats: Dict[str, int] = field(default_factory=lambda: {"n": 0, "h": 0})

    @property
    def tree_root(self) -> Optional[TreeNode]:
        """Reconstruct the TreeNode object from the snapshot dictionary."""
        return TreeNode.from_dict(self.tree)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Step to JSON-compatible dictionary."""
        return {
            "tree": self.tree,
            "highlight_nodes": list(self.highlight_nodes),
            "highlight_edges": [list(edge) for edge in self.highlight_edges],
            "visited": list(self.visited),
            "message": self.message,
            "pseudo_line": self.pseudo_line,
            "stats": dict(self.stats),
        }


class StepRecorder:
    """Collects animation frames during tree algorithm executions."""

    def __init__(self, operation: str, pseudocode: Optional[List[str]] = None) -> None:
        self.operation: str = operation
        self.pseudocode: List[str] = pseudocode if pseudocode is not None else []
        self.steps: List[Step] = []

    def record_step(
        self,
        tree_root: Optional[TreeNode],
        highlight_nodes: Optional[List[str]] = None,
        highlight_edges: Optional[List[Tuple[str, str]]] = None,
        visited: Optional[List[Any]] = None,
        message: str = "",
        pseudo_line: int = -1,
    ) -> Step:
        """Capture a discrete animation frame with an immutable tree snapshot."""
        tree_dict = tree_root.to_dict() if tree_root is not None else None
        h_nodes = list(highlight_nodes) if highlight_nodes is not None else []
        h_edges = list(highlight_edges) if highlight_edges is not None else []
        vis = list(visited) if visited is not None else []
        stats = {
            "n": size(tree_root),
            "h": height(tree_root),
        }

        step = Step(
            tree=tree_dict,
            highlight_nodes=h_nodes,
            highlight_edges=h_edges,
            visited=vis,
            message=message,
            pseudo_line=pseudo_line,
            stats=stats,
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> Dict[str, Any]:
        """Convert recorded timeline to JSON-serializable dictionary."""
        return {
            "operation": self.operation,
            "pseudocode": self.pseudocode,
            "steps": [s.to_dict() for s in self.steps],
        }
