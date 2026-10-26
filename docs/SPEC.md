# Tree_Visualizer - Specification Document (`docs/SPEC.md`)

This document is the exact visual, algorithmic, architectural, and behavioral specification for **Tree_Visualizer**, a 100% Python desktop application (`tkinter`/`ttk`) built from scratch. It directly reflects the reference implementation from `https://github.com/avipratap-in/binary-tree-bst-visualizer` and `https://avipratap-in.github.io/binary-tree-bst-visualizer/`.

---

## 1. Official Identity & Constraints
- **Application Name (`APP_NAME`)**: `Tree_Visualizer` (exact casing and underscore).
- **Python Package**: `tree_visualizer`.
- **Target Runtime**: Python 3.11+, standard library `tkinter` + `ttk`.
- **Allowed Third-Party Packages**:
  - `Pillow` (for PNG image export and window icon).
  - `tkextrafont` (optional TrueType font loader on non-Windows platforms).
  - `pytest` (development and automated testing).
  - `PyInstaller` (development and executable bundling).
- **Core Rule**: Pure Python only. No HTML, CSS, or JavaScript files in this repository.
- **Layered Architecture**:
  - `core/`: Pure Data Structures & Algorithms (Node model, BST, traversals, builders, properties, parsing, validator). **No tkinter imports.**
  - `recorder/`: Animation step capture (nodes/edges highlighting, visited lists, pseudocode indices, status messages). **No tkinter imports.**
  - `state/`: Application state controller, undo/history stack, playback engine, settings. **No tkinter imports.**
  - `ui/`: Tkinter/ttk presentation layer (main window, canvas, control panels, top bar, player bar, dialogs).

---

## 2. Color Palettes & Theme System

Tree_Visualizer supports both **Dark Theme** (default) and **Light Theme**. The colors follow the curated VisuAlgo aesthetic.

| Token Key | Dark Theme (`[data-theme="dark"]`) | Light Theme (`[data-theme="light"]`) | Usage / Component |
| :--- | :--- | :--- | :--- |
| `--bg-app` | `#0f172a` (Slate 900) | `#f8fafc` (Slate 50) | Main application background |
| `--bg-panel` | `#1e293b` (Slate 800) | `#ffffff` (Pure White) | Sidebar panels, top-bar, player bar |
| `--bg-panel-alt` | `#334155` (Slate 700) | `#f1f5f9` (Slate 100) | Secondary panels, inputs, cards |
| `--border-color` | `#334155` (Slate 700) | `#e2e8f0` (Slate 200) | Borders, dividers, frame outlines |
| `--text-main` | `#f8fafc` (Slate 50) | `#0f172a` (Slate 900) | Primary text labels and values |
| `--text-muted` | `#94a3b8` (Slate 400) | `#64748b` (Slate 500) | Captions, placeholders, subtext |
| `--accent` | `#38bdf8` (Sky 400) | `#0284c7` (Sky 600) | Primary buttons, active tabs, focus ring |
| `--accent-hover` | `#0284c7` (Sky 600) | `#0369a1` (Sky 700) | Button hover state |
| `--canvas-bg` | `#0b0f19` (Deep Obsidian) | `#ffffff` (Pure White) | Canvas drawing surface |
| `--node-default` | `#3b82f6` (Blue 500) | `#2563eb` (Blue 600) | Standard unvisited node fill |
| `--node-visited` | `#10b981` (Emerald 500) | `#059669` (Emerald 600) | Traversed / visited node fill |
| `--node-highlight`| `#ea580c` (Orange 600) | `#ea580c` (Orange 600) | Current focus / active node fill |
| `--node-stroke` | `#1e293b` (Slate 800) | `#ffffff` (White outline) | Node border stroke |
| `--node-text` | `#ffffff` (Pure White) | `#ffffff` (Pure White) | Node label text fill |
| `--edge-default` | `#64748b` (Slate 500) | `#94a3b8` (Slate 400) | Tree edge connecting line |
| `--edge-highlight`| `#ea580c` (Orange 600) | `#ea580c` (Orange 600) | Traversed active edge line |
| `--status-bg` | `#fef08a` (Yellow 200) | `#fef9c3` (Yellow 100) | VisuAlgo status card background |
| `--status-text` | `#854d0e` (Yellow 800) | `#713f12` (Yellow 900) | VisuAlgo status card text |
| `--status-border`| `#facc15` (Yellow 400) | `#fde047` (Yellow 300) | VisuAlgo status card border |
| `--pseudo-bg` | `#fce7f3` (Pink 100) | `#fdf2f8` (Pink 50) | VisuAlgo pseudocode panel background |
| `--pseudo-text` | `#831843` (Pink 900) | `#701a75` (Fuchsia 900) | VisuAlgo pseudocode text |
| `--pseudo-border`| `#f472b6` (Pink 400) | `#f9a8d4` (Pink 300) | VisuAlgo pseudocode panel border |
| `--pseudo-act-bg`| `#fbcfe8` (Pink 200) | `#fce7f3` (Pink 100) | Active pseudocode line background |
| `--pseudo-act-bd`| `#db2777` (Pink 600) | `#ec4899` (Pink 500) | Active pseudocode line border |

---

## 3. UI Layout & Component Specifications

The application layout consists of:
```
+---------------------------------------------------------------------------------------+
| TOP BAR: [🌲 Tree_Visualizer]  [Tabs: Binary Tree | BST | Build]  [Undo, Clear, JSON...] |
+-----------------------+---------------------------------------------------------------+
| OPERATIONS SIDEBAR    | CANVAS VIEWPORT (with Pan & Zoom)                             |
| (Collapsible: ☰ / ✕)  |                                                               |
|                       |  [N=.., h=..]                         [+ | 100% | - | ⟲]      |
| Current Tab Controls: |                                                               |
| - BST Controls        |  [Visited: A, B, C, ...]                                      |
| - Binary Tree Ctrl    |                                                               |
| - Build Traversal     |  (Tree Nodes & Edges / Empty Definition Card)                 |
|                       |                                                               |
|                       |  [Yellow Status Box: "Searching for 42..."]                   |
|                       |  [Pink Pseudocode Panel: active step highlighted]             |
+-----------------------+---------------------------------------------------------------+
| PLAYER BAR: [⏮] [◀] [▶/⏸] [▶] [⏭]  [==== Scrubber ====]  (i / n)  [Speed: 1.0x v]    |
+---------------------------------------------------------------------------------------+
```

### 3.1 Top Bar
- **Brand Title**: `🌲 Tree_Visualizer` (bold font).
- **Navigation Tabs**:
  - `Binary Tree`
  - `BST` (default active tab)
  - `Build from Traversal`
- **Utility Actions (Top-Right)**:
  - `↩ Undo`: Reverts the last state modification (keyboard shortcut: `Ctrl+Z`). Disabled when history is empty.
  - `✕ Clear`: Resets the current tree to an empty canvas.
  - `💾 JSON`: Opens file save dialog to export tree structure as formatted JSON.
  - `📷 PNG`: Exports high-resolution image of current canvas.
  - `🔗 Share`: Copies serialized tree JSON or state string to clipboard.
  - `Theme Toggle`: `☾ Dark` / `☼ Light` toggle button.

### 3.2 Operations Sidebar (Collapsible)
- Toggle button on canvas: `☰ Operations` when collapsed; `✕` button inside sidebar header when opened.
- Title dynamically reflects current tab:
  - `Binary Tree Operations`
  - `BST Operations`
  - `Build from Traversal`
- Width: `320px` (min `280px`, max `360px`).

### 3.3 Canvas Area & Floating Overlays
- **Logical Canvas Coordinates**: `900px` width by `500px` height.
- **Top-Left Stats Badge**: `N=0, h=0` (updates automatically with node count and tree height).
- **Top-Right Zoom Controls**:
  - `+`: Zoom in by 10% (`BUTTON_STEP = 1.1`).
  - `100%`: Current zoom badge label.
  - `−`: Zoom out by 10% (`1 / 1.1`).
  - `⟲`: Reset pan and zoom to default origin (scale `1.0`, pan `(0, 0)`).
- **Visited Sequence Banner**:
  - Located at top-center of canvas when an operation produces visits:
  - Label: `Visited Sequence: [ A, B, C, ... ]`
  - Concealed when empty.
- **Empty Canvas Definition Card**:
  - Displayed prominently in the center of the canvas when the current tree is `null`.
  - Rendered in **Cinzel Decorative** Bold (`CinzelDecorative-Bold.ttf`, 34pt title) and **Agbalumo** (`Agbalumo-Regular.ttf`, 20pt body, 12pt hint).
  - Contains title, academic definition, and actionable hint.
- **VisuAlgo Yellow Status Box**:
  - Positioned bottom-left or overlaid above player bar.
  - Displays current operational progress, element comparisons, or completion messages.
- **VisuAlgo Pink Pseudocode Panel**:
  - Positioned bottom-right of canvas.
  - Displays numbered algorithmic pseudocode lines.
  - Highlights the current active line in darker pink with accent border.

### 3.4 Player Bar
- Controls:
  - `⏮` (Skip to Start / Index 0)
  - `◀` (Step Back / Index - 1)
  - `▶` / `⏸` (Play / Pause toggle)
  - `▶` (Step Forward / Index + 1)
  - `⏭` (Skip to End / Last Index)
- Progress Scrubber Slider: from `0` to `n - 1`.
- Step Counter Label: `i / n` (e.g. `3 / 12`).
- Speed Dropdown: `0.25x`, `0.5x`, `1.0x` (default), `2.0x`, `4.0x`. Base step duration = `1000ms`.

---

## 4. Tree Layout Mathematics & Drawing Pipeline

The visualizer uses a deterministic, collision-free coordinate assignment algorithm based on Inorder traversal:

### Coordinate Assignment
For a tree with $n$ nodes:
1. Perform an **inorder traversal** of the tree to assign each node an integer sequence index $i \in [0, n - 1]$.
2. Track the depth $d$ of each node (where root depth $d = 0$). Compute maximum depth $d_{max}$.
3. Coordinate calculation:
   - Margins: $margin_X = 60$, $margin_Y = 60$.
   - Usable Width: $usable\_width = CanvasWidth - 2 \times margin_X = 900 - 120 = 780$.
   - Horizontal Position $x$:
     $$\text{If } n = 1: \quad x = \frac{CanvasWidth}{2} = 450$$
     $$\text{If } n > 1: \quad x = margin_X + \left(\frac{i}{n - 1}\right) \times usable\_width$$
   - Level Height:
     $$level\_height = \begin{cases} 0 & \text{if } d_{max} = 0 \\ \min\left(85, \frac{CanvasHeight - 2 \times margin_Y}{d_{max}}\right) & \text{if } d_{max} > 0 \end{cases}$$
   - Vertical Position $y$:
     $$y = margin_Y + d \times level\_height$$
4. **Node Radius**: $r = 20\text{px}$.
5. **Node Text Format**:
   - If node frequency $freq == 1$: display string value `val` (e.g. `50`).
   - If node frequency $freq > 1$: display `val-freq` (e.g. `50-2`).
6. **Drawing Order**:
   - Step 1: Draw all edges (`x1, y1` to `x2, y2`) so edges sit underneath node circles.
   - Step 2: Draw node outer circles (border stroke and fill).
   - Step 3: Draw node text centered within the circle.

---

## 5. Zoom & Pan Constants
- `WHEEL_SENSITIVITY = 0.00064`: Gentle mouse wheel zooming centered on cursor (reduced 20% sensitivity).
- `BUTTON_STEP = 1.079`: Zoom step factor for `+` and `−` buttons (reduced 20% sensitivity).
- `MIN_SCALE = 0.3` (30% minimum zoom).
- `MAX_SCALE = 3.0` (300% maximum zoom).
- Canvas click-and-drag to pan coordinates $(pan_X, pan_Y)$.

---

## 6. Definition Card Texts (Cinzel Decorative & Agbalumo)

Whenever a tab's tree is empty (`currentTree == null`), display the corresponding definition card:

### Binary Tree Tab
- **Title**: `Binary Tree`
- **Body**: "A binary tree is a hierarchical data structure in which every node has at most two children, called the left child and the right child. Formally, it is either empty or consists of a root node together with a left subtree and a right subtree, each of which is itself a binary tree."
- **Hint**: "Use the panel on the left to create a tree."

### BST Tab
- **Title**: `Binary Search Tree (BST)`
- **Body**: "A binary search tree is a binary tree in which, for every node, all values in its left subtree are smaller than the node's value and all values in its right subtree are greater. Because of this ordering, an inorder traversal visits the values in sorted order, and search, insert and remove take O(h) time, where h is the height of the tree."
- **Hint**: "Use the panel on the left to create a tree."

### Build from Traversal Tab
- **Title**: `Build from Traversal`
- **Body**: "A binary tree can be reconstructed from two of its traversal sequences. The inorder sequence together with the preorder, postorder or level-order sequence identifies the tree uniquely, as long as all values are distinct. Preorder with postorder alone is unique only for full binary trees."
- **Hint**: "Use the panel on the left to create a tree."

---

## 7. Operations & Features by Tab

### 7.1 BST Tab
1. **Create BST**:
   - Input: Count $n$ (`1` to `25`, default `7`), button `Random`.
   - Input: Custom array text input (`e.g. 50, 30, 70, 20`), button `Load`.
   - Dropdown: `Select a Preset BST...`:
     1. Balanced BST: `[50, 25, 75, 12, 37, 62, 87]` ("A well-balanced BST with 7 nodes (height = 3).")
     2. Right-Skewed BST: `[10, 20, 30, 40, 50]` ("A completely skewed BST demonstrating O(n) degeneration.")
     3. BST with Duplicates: `[50, 30, 70, 30, 50, 80, 20]` ("A BST demonstrating frequency counts for repeated values.")
     4. Full & Perfect Binary Tree: `[1, 2, 3, 4, 5, 6, 7]` level-order ("A perfect binary tree of height 3.")
2. **Insert**:
   - Input: `Value(s) e.g. 45 or 12, 85`, button `Insert`.
   - Supports single value or comma-separated batch insertion.
   - Duplicates increment `freq` counter on existing node.
3. **Search & Remove**:
   - Search: Input `Search value`, button `Search`.
   - Remove: Input `Remove value`, button `Remove` (red accent). Decrements `freq`; physically deletes node only if `freq == 1`. Handles 3 cases: leaf, 1 child, 2 children (inorder successor).
4. **Min & Max**:
   - Buttons: `Find Min` (follows left child to leftmost leaf) and `Find Max` (follows right child to rightmost leaf).
5. **Predecessor & Successor**:
   - Input: `Target value`.
   - Buttons: `Predecessor` (largest value smaller than target) and `Successor` (smallest value greater than target).
6. **Rank & Select**:
   - Rank: Input `Value for Rank`, button `Rank` (number of elements strictly smaller than target).
   - Select: Input `k (1-indexed)` min `1`, button `Select` (finds the $k$-th smallest element).

### 7.2 Binary Tree Tab
1. **Create Binary Tree**:
   - Input: Count $n$ (`1` to `30`, default `6`), button `Random`.
   - Toggle control: `Labels: Numbers | Letters` (segmented button).
   - Input: Level-order sequence text (`e.g. 1, 2, 3, null, 4 or A, B, C, -, D`), button `Load`. Tolerates `null`, `None`, `-`, `.` for empty child slots.
2. **Traversals**:
   - Buttons: `Preorder`, `Inorder`, `Postorder`, `Level Order`.
   - Visited array accumulates sequentially in Visited banner and yellow status box.
3. **Tree Properties Card Grid**:
   - Displays real-time tree analytics:
     - `Leaf Count`: Count of nodes with 0 children.
     - `Internal Nodes`: Count of nodes with at least 1 child.
     - `Height`: Maximum path depth from root to leaf (1-based; empty tree = 0).
     - `Full Tree`: `Yes` / `No` (every node has 0 or 2 children).
     - `Complete`: `Yes` / `No` (all levels full except possibly last, filled left-to-right).
     - `Perfect`: `Yes` / `No` (all leaf nodes at same depth, all internal nodes have 2 children: $N = 2^h - 1$).
     - `Height-Balanced (AVL)`: `Yes` / `No` ($|\text{height}(left) - \text{height}(right)| \le 1$ for every node).

### 7.3 Build from Traversal Tab
1. **Reconstruction Modes (`buildModeSelect`)**:
   - `in+pre`: `Inorder + Preorder`
   - `in+post`: `Inorder + Postorder`
   - `in+level`: `Inorder + Level Order`
   - `pre+post`: `Preorder + Postorder (Full BT only)`
   - `bst-pre`: `BST from Preorder only`
   - `bst-post`: `BST from Postorder only`
2. **Ambiguity Warning Banner**:
   - Displayed when `pre+post` mode is selected:
   - "⚠️ **Ambiguity Note:** Preorder + Postorder only uniquely reconstructs *Full Binary Trees* (where every node has 0 or 2 children). Any single-child node will trigger an ambiguity error."
3. **Inputs**:
   - Field 1: `Inorder Sequence` (or Preorder for BST modes). Placeholder: `e.g. D, B, E, A, C or 4, 2, 5, 1, 6`.
   - Field 2: `Preorder / Postorder / Level Order Sequence` (hidden in single-sequence BST modes).
4. **Smart Suggestions & Diagnostics**:
   - Real-time debounced validation box (`buildValidationBox`).
   - Detects:
     - Element set differences: "Missing in Sequence 2: [...]"
     - Length mismatches: "Length mismatch: Sequence 1 has N items, while Sequence 2 has M items."
     - Duplicate values with one-click `Rename duplicates in Seq` suggestion pill button.
     - Ambiguity or structural mismatch with `⇄ Swap Sequences` or `Switch mode to ...` buttons.
5. **Actions**:
   - `Build & Animate`: Generates tree and plays step-by-step reconstruction timeline.
   - `Random`: Populates inputs with a valid random tree sequence pair.
   - `Labels` dropdown: `Letters A-Z` or `Numbers 1-99`.
   - `Auto-run` checkbox: When checked, automatically triggers `Build & Animate` upon clicking Random.

---

## 8. Pseudocode Specifications

Every animated operation highlights an active line index (`pseudo_line`) corresponding to this table:

### 8.1 BST Operations
- **Search (`record_search`)**:
  - `0`: `if root is null: return not found`
  - `1`: `if v == curr.val: return found`
  - `2`: `if v < curr.val: search left subtree`
  - `3`: `else: search right subtree`
- **Insert (`record_insert`)**:
  - `0`: `if tree is empty: create root node`
  - `1`: `if v == curr.val: increment curr.freq`
  - `2`: `if v < curr.val: go left (insert if null)`
  - `3`: `else: go right (insert if null)`
- **Remove (`record_remove`)**:
  - `0`: `search for v`
  - `1`: `if v's freq > 1, decrement by 1`
  - `2`: `else if v is a leaf, remove leaf v`
  - `3`: `else if v has 1 child, bypass v`
  - `4`: `else replace v with successor`
- **Find Min (`record_min`)**:
  - `0`: `if tree is empty: return null`
  - `1`: `while curr.left exists: go left`
  - `2`: `return curr.val (minimum)`
- **Find Max (`record_max`)**:
  - `0`: `if tree is empty: return null`
  - `1`: `while curr.right exists: go right`
  - `2`: `return curr.val (maximum)`
- **Predecessor (`record_predecessor`)**:
  - `0`: `start at root, pred = null`
  - `1`: `if v <= curr.val: go left`
  - `2`: `else: pred = curr, go right`
  - `3`: `return pred`
- **Successor (`record_successor`)**:
  - `0`: `start at root, succ = null`
  - `1`: `if v >= curr.val: go right`
  - `2`: `else: succ = curr, go left`
  - `3`: `return succ`
- **Rank (`record_rank`)**:
  - `0`: `rank = 0, curr = root`
  - `1`: `if v < curr.val: search left subtree`
  - `2`: `if v > curr.val: rank += left_size + freq, search right subtree`
  - `3`: `if v == curr.val: rank += left_size, return rank`
- **Select (`record_select`)**:
  - `0`: `if k < 1 or k > total_size: return null`
  - `1`: `if k <= left_size: search left subtree`
  - `2`: `else if k <= left_size + freq: return curr.val`
  - `3`: `else: k -= left_size + freq, search right subtree`
- **Create From Array (`record_create_from_array`)**:
  - `0`: `tree = empty BST`
  - `1`: `for each val in array: insert(val)`
  - `2`: `BST creation complete`

### 8.2 Traversals
- **Preorder (`record_preorder`)**:
  - `0`: `if curr is null: return`
  - `1`: `visit curr node (append to visited)`
  - `2`: `traverse left subtree`
  - `3`: `traverse right subtree`
- **Inorder (`record_inorder`)**:
  - `0`: `if curr is null: return`
  - `1`: `traverse left subtree`
  - `2`: `visit curr node (append to visited)`
  - `3`: `traverse right subtree`
- **Postorder (`record_postorder`)**:
  - `0`: `if curr is null: return`
  - `1`: `traverse left subtree`
  - `2`: `traverse right subtree`
  - `3`: `visit curr node (append to visited)`
- **Level Order (`record_level_order`)**:
  - `0`: `if root is null: return`
  - `1`: `queue = [root]`
  - `2`: `while queue is not empty:`
  - `3`: `  curr = queue.popleft(), visit curr`
  - `4`: `  enqueue curr.left, enqueue curr.right`

### 8.3 Tree Reconstructions
- **Inorder + Preorder (`record_build_inorder_preorder`)**:
  - `0`: `pick root value from preorder sequence`
  - `1`: `find root position in inorder sequence`
  - `2`: `split inorder into left & right subtrees`
  - `3`: `recursively construct left subtree`
  - `4`: `recursively construct right subtree`
- **Inorder + Postorder (`record_build_inorder_postorder`)**:
  - `0`: `pick root value from end of postorder sequence`
  - `1`: `find root position in inorder sequence`
  - `2`: `split inorder into left & right subtrees`
  - `3`: `recursively construct right subtree`
  - `4`: `recursively construct left subtree`
- **Inorder + Level Order (`record_build_inorder_level_order`)**:
  - `0`: `pick root from head of level-order sequence`
  - `1`: `find root position in inorder sequence`
  - `2`: `filter remaining level-order into left & right sets`
  - `3`: `recursively construct left subtree`
  - `4`: `recursively construct right subtree`
- **Preorder + Postorder (`record_build_preorder_postorder`)**:
  - `0`: `pick root value from preorder sequence`
  - `1`: `if leaf (length == 1): return node`
  - `2`: `check for ambiguity: preorder[1] == postorder[-2]`
  - `3`: `split subtrees using left child index in postorder`
  - `4`: `recursively construct left & right subtrees`
- **BST from Preorder (`record_build_bst_from_preorder`)**:
  - `0`: `pick root value from preorder`
  - `1`: `elements within (min, max) bounds become children`
  - `2`: `recursively construct left subtree with upper bound = root.val`
  - `3`: `recursively construct right subtree with lower bound = root.val`
- **BST from Postorder (`record_build_bst_from_postorder`)**:
  - `0`: `pick root value from end of postorder`
  - `1`: `elements within (min, max) bounds become children`
  - `2`: `recursively construct right subtree with lower bound = root.val`
  - `3`: `recursively construct left subtree with upper bound = root.val`

---

## 9. Keyboard Shortcuts & User Controls
- `Space`: Play / Pause animation toggle.
- `Left Arrow`: Step backward by 1 frame.
- `Right Arrow`: Step forward by 1 frame.
- `Ctrl + Z`: Trigger Undo action.
- *Guard*: When an `Entry` or `Text` field has focus, keyboard shortcuts are suppressed so user typing is unobstructed.

---

## 10. Undo & Clear Semantics
- **History Stack**: Stores up to `30` past tree snapshot states.
- **Save Trigger**: Pushed immediately before any mutating operation (BST insert, remove, clear, load custom, load preset, rebuild).
- **Undo Action**: Pops previous tree snapshot and animates reversion:
  - Pseudocode: `['reverted to previous tree state']`
  - Message: `"Undid last operation. Reverted tree state."`
- **Clear Action**: Pushes snapshot to history stack, resets current tree to `null`, and renders empty definition card:
  - Pseudocode: `['tree cleared']`
  - Message: `"Tree cleared."`

---

## 11. Serialization & Export Formats
- **JSON Serialization**:
  Nodes serialize recursively with:
  ```json
  {
    "id": "uuid4_or_stable_id",
    "val": 50,
    "freq": 1,
    "left": null,
    "right": null
  }
  ```
- **PNG Export**:
  Uses `Pillow` to capture the Canvas bounding box into a clean, antialiased image file (`tree.png`).
