"""Application state controller and operation coordinator.

Maintains per-tab tree states and undo histories, routes user requests through
the pure DSA core and recorder layers, maps exceptions into user-facing status messages,
and notifies UI observers without any tkinter imports.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from tree_visualizer.core.binary_tree import BinaryTree
from tree_visualizer.core.bst import BinarySearchTree
from tree_visualizer.core.comparison import is_numeric_value
from tree_visualizer.core.exceptions import (
    AmbiguousTreeError,
    MixedTypesError,
    TreeBuildError,
    TreeError,
)
from tree_visualizer.core.generators import (
    generate_random_binary_tree,
    generate_random_bst,
    generate_traversal_pair,
)
from tree_visualizer.core.node import TreeNode
from tree_visualizer.core.parsing import parse_level_order, parse_sequence
from tree_visualizer.core.properties import compute_properties
from tree_visualizer.core.suggestions import diagnose_sequences
from tree_visualizer.recorder.bst_recorder import (
    record_create_from_array,
    record_insert,
    record_max,
    record_min,
    record_predecessor,
    record_rank,
    record_remove,
    record_search,
    record_select,
    record_successor,
)
from tree_visualizer.recorder.build_recorder import (
    record_build_bst_from_postorder,
    record_build_bst_from_preorder,
    record_build_inorder_level_order,
    record_build_inorder_postorder,
    record_build_inorder_preorder,
    record_build_preorder_postorder,
)
from tree_visualizer.recorder.steps import Step
from tree_visualizer.recorder.traversal_recorder import (
    record_inorder,
    record_level_order,
    record_postorder,
    record_preorder,
)
from tree_visualizer.state.player import Player
from tree_visualizer.state.settings import Settings
from tree_visualizer.state.share import decode_share_code, encode_share_code


class Controller:
    """Central state manager coordinating core algorithms, animation recordings, and UI state."""

    MAX_HISTORY: int = 30

    PRESETS: Dict[str, Dict[str, Any]] = {
        "balanced_bst": {
            "name": "Balanced BST",
            "type": "bst",
            "values": [50, 25, 75, 12, 37, 62, 87],
            "description": "A well-balanced BST with 7 nodes (height = 3).",
        },
        "skewed_bst": {
            "name": "Right-Skewed BST",
            "type": "bst",
            "values": [10, 20, 30, 40, 50],
            "description": "A completely skewed BST demonstrating O(n) degeneration.",
        },
        "duplicate_bst": {
            "name": "BST with Duplicates",
            "type": "bst",
            "values": [50, 30, 70, 30, 50, 80, 20],
            "description": "A BST demonstrating frequency counts for repeated values.",
        },
        "full_binary_tree": {
            "name": "Full & Perfect Binary Tree",
            "type": "binary",
            "values": [1, 2, 3, 4, 5, 6, 7],
            "description": "A perfect binary tree of height 3.",
        },
    }

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings: Settings = settings if settings is not None else Settings.load()
        self.player: Player = Player()
        self.active_tab: str = "bst"

        # Per-tab trees and undo history stacks
        self.trees: Dict[str, Optional[TreeNode]] = {
            "binary": None,
            "bst": None,
            "build": None,
        }
        self.history_stacks: Dict[str, List[Optional[TreeNode]]] = {
            "binary": [],
            "bst": [],
            "build": [],
        }

        # UI observer callbacks
        self.on_tree_changed: Optional[Callable[[str, Optional[TreeNode]], None]] = None
        self.on_status_message: Optional[Callable[[str, str], None]] = None
        self.on_properties_changed: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_tab_changed: Optional[Callable[[str], None]] = None
        self.on_empty_state_changed: Optional[Callable[[str, bool], None]] = None
        self.on_undo_state_changed: Optional[Callable[[bool], None]] = None

    @property
    def current_tree(self) -> Optional[TreeNode]:
        """Return the root TreeNode of the currently active tab."""
        return self.trees.get(self.active_tab)

    @current_tree.setter
    def current_tree(self, node: Optional[TreeNode]) -> None:
        self.trees[self.active_tab] = node
        self._notify_tree_changed()

    def is_empty_tab(self, tab: str) -> bool:
        """Return True if tree in specified tab is empty."""
        return self.trees.get(tab) is None

    @property
    def is_current_empty(self) -> bool:
        """Return True if active tab's tree is currently None."""
        return self.current_tree is None

    @property
    def can_undo(self) -> bool:
        """Return True if active tab has undo snapshots available."""
        stack = self.history_stacks.get(self.active_tab, [])
        return len(stack) > 0

    def set_active_tab(self, tab: str) -> None:
        """Switch active tab ('bst', 'binary', or 'build')."""
        if tab in ("binary", "bst", "build") and tab != self.active_tab:
            self.active_tab = tab
            if self.on_tab_changed is not None:
                self.on_tab_changed(tab)
            self._notify_tree_changed()
            self._notify_undo_state()

    # =========================================================================
    # History & Undo / Clear Semantics
    # =========================================================================

    def save_history(self) -> None:
        """Snapshot current tree into active tab's history stack."""
        stack = self.history_stacks[self.active_tab]
        snapshot = self.current_tree.clone() if self.current_tree is not None else None
        stack.append(snapshot)
        if len(stack) > self.MAX_HISTORY:
            stack.pop(0)
        self._notify_undo_state()

    def undo(self) -> bool:
        """Revert active tab to previous tree state. Returns True if reverted."""
        stack = self.history_stacks[self.active_tab]
        if not stack:
            self.set_status("Nothing to undo.", severity="info")
            return False

        previous_tree = stack.pop()
        self.current_tree = previous_tree
        self._notify_undo_state()

        step = Step(
            tree=previous_tree.to_dict() if previous_tree is not None else None,
            highlight_nodes=[],
            highlight_edges=[],
            visited=[],
            message="Undid last operation. Reverted tree state.",
            pseudo_line=0,
            stats={"n": previous_tree.size() if previous_tree else 0, "h": previous_tree.height() if previous_tree else 0},
        )
        self.player.load_timeline(
            pseudocode=["reverted to previous tree state"],
            steps=[step],
            auto_play=False,
        )
        self.set_status("Undid last operation. Reverted tree state.", severity="info")
        return True

    def clear(self) -> None:
        """Clear the current tree and display definition card."""
        self.save_history()
        self.current_tree = None

        step = Step(
            tree=None,
            highlight_nodes=[],
            highlight_edges=[],
            visited=[],
            message="Tree cleared.",
            pseudo_line=0,
            stats={"n": 0, "h": 0},
        )
        self.player.load_timeline(
            pseudocode=["tree cleared"],
            steps=[step],
            auto_play=False,
        )
        self.set_status("Tree cleared.", severity="info")

    # =========================================================================
    # Status & Observers
    # =========================================================================

    def set_status(self, message: str, severity: str = "info") -> None:
        """Publish a message to the status box observer."""
        if self.on_status_message is not None:
            self.on_status_message(message, severity)

    def _notify_tree_changed(self) -> None:
        is_empty = self.is_current_empty
        if self.on_empty_state_changed is not None:
            self.on_empty_state_changed(self.active_tab, is_empty)

        if self.on_tree_changed is not None:
            self.on_tree_changed(self.active_tab, self.current_tree)

        props = compute_properties(self.current_tree)
        if self.on_properties_changed is not None:
            self.on_properties_changed(props)

    def _notify_undo_state(self) -> None:
        if self.on_undo_state_changed is not None:
            self.on_undo_state_changed(self.can_undo)

    def _apply_recorded_result(
        self,
        pseudocode: List[str],
        steps: List[Step],
        auto_play: bool = True,
    ) -> None:
        """Apply recorded steps to the player and update active tree from final step."""
        if not steps:
            return

        final_step = steps[-1]
        self.current_tree = final_step.tree_root
        self.player.load_timeline(pseudocode, steps, auto_play=auto_play)
        if final_step.message:
            self.set_status(final_step.message, severity="info")

    # =========================================================================
    # BST Operations
    # =========================================================================

    def bst_insert(self, val_str: str) -> None:
        """Insert single or batch values into the BST."""
        p = parse_sequence(val_str)
        if not p.tokens:
            self.set_status("Please enter one or more values to insert.", severity="warning")
            return

        self.save_history()
        try:
            tree_root = self.current_tree
            all_steps: List[Step] = []
            pseudo_lines: List[str] = []

            for val in p.tokens:
                pseudo_lines, steps = record_insert(tree_root, val)
                all_steps.extend(steps)
                tree_root = steps[-1].tree_root

            self._apply_recorded_result(pseudo_lines, all_steps, auto_play=True)
        except (MixedTypesError, TreeError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_search(self, val: Any) -> None:
        """Search for a value in the BST."""
        p = parse_sequence(str(val))
        if not p.tokens:
            self.set_status("Please enter a search value.", severity="warning")
            return
        target = p.tokens[0]
        try:
            pseudo, steps = record_search(self.current_tree, target)
            self.player.load_timeline(pseudo, steps, auto_play=True)
            self.set_status(steps[-1].message, severity="info")
        except (MixedTypesError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_remove(self, val: Any) -> None:
        """Remove a value from the BST."""
        p = parse_sequence(str(val))
        if not p.tokens:
            self.set_status("Please enter a value to remove.", severity="warning")
            return
        target = p.tokens[0]
        self.save_history()
        try:
            pseudo, steps = record_remove(self.current_tree, target)
            self._apply_recorded_result(pseudo, steps, auto_play=True)
        except (MixedTypesError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_min(self) -> None:
        """Find minimum value in the BST."""
        if self.current_tree is None:
            self.set_status("Tree is empty. Cannot find min.", severity="warning")
            return
        pseudo, steps = record_min(self.current_tree)
        self.player.load_timeline(pseudo, steps, auto_play=True)
        self.set_status(steps[-1].message, severity="info")

    def bst_max(self) -> None:
        """Find maximum value in the BST."""
        if self.current_tree is None:
            self.set_status("Tree is empty. Cannot find max.", severity="warning")
            return
        pseudo, steps = record_max(self.current_tree)
        self.player.load_timeline(pseudo, steps, auto_play=True)
        self.set_status(steps[-1].message, severity="info")

    def bst_predecessor(self, val: Any) -> None:
        """Find inorder predecessor in the BST."""
        p = parse_sequence(str(val))
        if not p.tokens:
            self.set_status("Please enter a target value.", severity="warning")
            return
        target = p.tokens[0]
        try:
            pseudo, steps = record_predecessor(self.current_tree, target)
            self.player.load_timeline(pseudo, steps, auto_play=True)
            self.set_status(steps[-1].message, severity="info")
        except (MixedTypesError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_successor(self, val: Any) -> None:
        """Find inorder successor in the BST."""
        p = parse_sequence(str(val))
        if not p.tokens:
            self.set_status("Please enter a target value.", severity="warning")
            return
        target = p.tokens[0]
        try:
            pseudo, steps = record_successor(self.current_tree, target)
            self.player.load_timeline(pseudo, steps, auto_play=True)
            self.set_status(steps[-1].message, severity="info")
        except (MixedTypesError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_rank(self, val: Any) -> None:
        """Compute rank of value in the BST."""
        p = parse_sequence(str(val))
        if not p.tokens:
            self.set_status("Please enter a value for rank.", severity="warning")
            return
        target = p.tokens[0]
        try:
            pseudo, steps = record_rank(self.current_tree, target)
            self.player.load_timeline(pseudo, steps, auto_play=True)
            self.set_status(steps[-1].message, severity="info")
        except (MixedTypesError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_select(self, k: int) -> None:
        """Select k-th smallest element in the BST."""
        if k < 1:
            self.set_status("Please enter a valid rank k (1-indexed).", severity="warning")
            return
        if self.current_tree is None:
            self.set_status("Tree is empty. Cannot select k-th element.", severity="warning")
            return
        pseudo, steps = record_select(self.current_tree, k)
        self.player.load_timeline(pseudo, steps, auto_play=True)
        self.set_status(steps[-1].message, severity="info")

    def bst_load_array(self, arr_str: str) -> None:
        """Create BST from array of values."""
        p = parse_sequence(arr_str)
        if not p.tokens:
            self.set_status("Please provide values to load into BST.", severity="warning")
            return

        self.save_history()
        try:
            pseudo, steps = record_create_from_array(p.tokens)
            self._apply_recorded_result(pseudo, steps, auto_play=True)
        except (MixedTypesError, TreeError, ValueError) as e:
            self.set_status(str(e), severity="error")

    def bst_random(self, n: int = 7) -> None:
        """Generate random BST with n values."""
        self.save_history()
        bst = generate_random_bst(n, label_type="numbers")
        if bst.root is None:
            self.clear()
            return
        from tree_visualizer.core.traversals import level_order
        lvl = level_order(bst.root)
        pseudo, steps = record_create_from_array(lvl)
        self._apply_recorded_result(pseudo, steps, auto_play=True)

    def load_preset(self, preset_id: str) -> None:
        """Load a predefined example tree."""
        preset = self.PRESETS.get(preset_id)
        if not preset:
            self.set_status(f"Unknown preset '{preset_id}'.", severity="error")
            return

        self.save_history()
        target_tab = preset.get("type", "bst")
        self.set_active_tab(target_tab)

        if target_tab == "bst":
            values = preset["values"]
            pseudo, steps = record_create_from_array(values)
            self._apply_recorded_result(pseudo, steps, auto_play=True)
        else:
            values = preset["values"]
            tree = BinaryTree.from_level_order(values)
            self.current_tree = tree.root
            pseudo, steps = record_level_order(self.current_tree)
            self.player.load_timeline(pseudo, steps, auto_play=False)
            self.set_status(f"Loaded preset: {preset['name']}", severity="info")

    # =========================================================================
    # Binary Tree Operations
    # =========================================================================

    def binary_random(self, n: int = 6, label_type: str = "numbers") -> None:
        """Create random Binary Tree."""
        self.save_history()
        root = generate_random_binary_tree(n, label_type=label_type)
        self.current_tree = root
        pseudo, steps = record_level_order(root)
        self.player.load_timeline(pseudo, steps, auto_play=False)
        self.set_status(f"Generated random binary tree with {n} nodes ({label_type}).", severity="info")

    def binary_load_level_order(self, raw_str: str) -> None:
        """Build Binary Tree from level-order list."""
        p = parse_level_order(raw_str)
        if not p.tokens or p.tokens[0] is None:
            self.set_status("Root node cannot be null. Please provide valid level-order values.", severity="warning")
            return

        self.save_history()
        tree = BinaryTree.from_level_order(p.tokens)
        self.current_tree = tree.root
        pseudo, steps = record_level_order(self.current_tree)
        self.player.load_timeline(pseudo, steps, auto_play=False)
        self.set_status("Binary tree constructed from level-order list.", severity="info")

    def run_traversal(self, order: str) -> None:
        """Run traversal on the current tree ('pre', 'in', 'post', 'level')."""
        if self.current_tree is None:
            self.set_status("Tree is empty. Cannot run traversal.", severity="warning")
            return

        if order == "pre":
            pseudo, steps = record_preorder(self.current_tree)
        elif order == "in":
            pseudo, steps = record_inorder(self.current_tree)
        elif order == "post":
            pseudo, steps = record_postorder(self.current_tree)
        elif order == "level":
            pseudo, steps = record_level_order(self.current_tree)
        else:
            self.set_status(f"Unknown traversal order: '{order}'", severity="error")
            return

        self.player.load_timeline(pseudo, steps, auto_play=True)
        self.set_status(steps[-1].message, severity="info")

    # =========================================================================
    # Build from Traversal Operations
    # =========================================================================

    def build_random(
        self,
        mode: str,
        label_type: str = "letters",
        n: Optional[int] = None,
    ) -> Tuple[str, Optional[str]]:
        """Generate a random valid traversal sequence pair for mode."""
        import random

        if n is None:
            n = random.randint(3, 7)
        if mode == "pre+post" and n % 2 == 0:
            n += 1
        tokens1, tokens2 = generate_traversal_pair(mode=mode, n=n, labels=label_type)
        s1 = ", ".join(str(x) for x in tokens1)
        s2 = ", ".join(str(x) for x in tokens2) if tokens2 is not None else None
        return s1, s2

    def build_reconstruct(self, mode: str, raw_seq1: str, raw_seq2: Optional[str] = None) -> None:
        """Reconstruct tree from traversal sequences."""
        diag = diagnose_sequences(mode, raw_seq1, raw_seq2)
        if not diag.valid:
            # Failed build must clear tree and never leave a stale tree looking like the result
            self.current_tree = None
            step = Step(
                tree=None,
                highlight_nodes=[],
                highlight_edges=[],
                visited=[],
                message=f"Reconstruction Error: {diag.message}",
                pseudo_line=0,
                stats={"n": 0, "h": 0},
            )
            self.player.load_timeline(
                ["Tree reconstruction failed: invalid traversal sequence(s)."],
                [step],
                auto_play=False,
            )
            sev = diag.severity if diag.severity in ("warning", "error") else "error"
            msg = diag.message if sev == "warning" else f"Reconstruction Error: {diag.message}"
            self.set_status(msg, severity=sev)
            return

        self.save_history()
        p1 = parse_sequence(raw_seq1)
        p2 = parse_sequence(raw_seq2) if raw_seq2 else None

        try:
            if mode == "in+pre":
                assert p2 is not None
                pseudo, steps = record_build_inorder_preorder(p1.tokens, p2.tokens)
            elif mode == "in+post":
                assert p2 is not None
                pseudo, steps = record_build_inorder_postorder(p1.tokens, p2.tokens)
            elif mode == "in+level":
                assert p2 is not None
                pseudo, steps = record_build_inorder_level_order(p1.tokens, p2.tokens)
            elif mode == "pre+post":
                assert p2 is not None
                pseudo, steps = record_build_preorder_postorder(p1.tokens, p2.tokens)
            elif mode == "bst-pre":
                pseudo, steps = record_build_bst_from_preorder(p1.tokens)
            elif mode == "bst-post":
                pseudo, steps = record_build_bst_from_postorder(p1.tokens)
            else:
                self.current_tree = None
                self.set_status(f"Unknown reconstruction mode: '{mode}'", severity="error")
                return

            self._apply_recorded_result(pseudo, steps, auto_play=True)
            self.set_status(steps[-1].message, severity="info")
        except AmbiguousTreeError as e:
            self.current_tree = None
            step = Step(
                tree=None,
                highlight_nodes=[],
                highlight_edges=[],
                visited=[],
                message=f"Reconstruction Error: {e}",
                pseudo_line=0,
                stats={"n": 0, "h": 0},
            )
            self.player.load_timeline(
                ["Tree reconstruction failed: ambiguous reconstruction."],
                [step],
                auto_play=False,
            )
            self.set_status(f"⚠️ Ambiguity Warning: {e}", severity="warning")
        except (TreeBuildError, TreeError, ValueError, Exception) as e:
            self.current_tree = None
            step = Step(
                tree=None,
                highlight_nodes=[],
                highlight_edges=[],
                visited=[],
                message=f"Reconstruction Error: {e}",
                pseudo_line=0,
                stats={"n": 0, "h": 0},
            )
            self.player.load_timeline(
                ["Tree reconstruction failed: sequences could not form a valid binary tree."],
                [step],
                auto_play=False,
            )
            self.set_status(f"Reconstruction Error: {e}", severity="error")

    # =========================================================================
    # Share & Export
    # =========================================================================

    def get_share_code(self) -> str:
        """Return base64 share code for the current tree and active tab."""
        return encode_share_code(self.current_tree, tab=self.active_tab)

    def load_share_code(self, code: str) -> bool:
        """Load tree and active tab from a share code."""
        try:
            tree_dict, tab = decode_share_code(code)
            self.set_active_tab(tab)
            self.save_history()
            self.current_tree = TreeNode.from_dict(tree_dict)
            self.set_status(f"Loaded shared tree for {tab} tab.", severity="info")
            return True
        except ValueError as e:
            self.set_status(f"Failed to load share code: {e}", severity="error")
            return False
