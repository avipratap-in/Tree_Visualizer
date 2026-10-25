# Tree_Visualizer: Algorithm Catalog & Capstone Reference

This document provides a comprehensive, plain-English conceptual guide and complexity analysis for all algorithms implemented in **Tree_Visualizer**. It is formatted as an academic reference suitable for capstone presentations, technical reports, and viva voce examinations.

---

## 1. Complexity Summary Table

Below is the consolidated time and space complexity table for every tree operation and construction algorithm. In all expressions:
- $n$ is the total number of nodes in the tree.
- $h$ is the height of the tree ($O(\log n)$ for balanced trees, $O(n)$ for degenerate/skewed trees).
- $w$ is the maximum width (maximum nodes on any single level, $w \le \lceil n/2 \rceil$).

| Category | Operation / Algorithm | Average Time | Worst Time | Auxiliary Space | Key Mechanics / Notes |
|---|---|---|---|---|---|
| **BST Query** | Search($v$) | $O(\log n)$ | $O(n)$ | $O(h)$ | Follows left if $v < \text{node}$, right if $v > \text{node}$. |
| **BST Mutation** | Insert($v$) | $O(\log n)$ | $O(n)$ | $O(h)$ | Traverses to leaf position or increments frequency if duplicate. |
| **BST Mutation** | Remove($v$) | $O(\log n)$ | $O(n)$ | $O(h)$ | Handles 3 cases: leaf (prune), 1 child (bypass), 2 children (replace with successor). |
| **BST Query** | Find Min / Find Max | $O(\log n)$ | $O(n)$ | $O(h)$ | Follows leftmost / rightmost edge chain to termination. |
| **BST Query** | Inorder Predecessor | $O(\log n)$ | $O(n)$ | $O(h)$ | Max of left subtree, or lowest ancestor whose right child contains $v$. |
| **BST Query** | Inorder Successor | $O(\log n)$ | $O(n)$ | $O(h)$ | Min of right subtree, or lowest ancestor whose left child contains $v$. |
| **BST Query** | Rank($v$) (1-based) | $O(\log n)$ | $O(n)$ | $O(h)$ | Number of strictly smaller keys $+ 1$. Uses subtree sizes when augmented. |
| **BST Query** | Select($k$) ($k$-th smallest) | $O(\log n)$ | $O(n)$ | $O(h)$ | Locates the node with sorted index $k$ in order-statistic tree. |
| **Traversal** | Preorder Traversal | $O(n)$ | $O(n)$ | $O(h)$ | Root $\rightarrow$ Left Subtree $\rightarrow$ Right Subtree (DFS). |
| **Traversal** | Inorder Traversal | $O(n)$ | $O(n)$ | $O(h)$ | Left Subtree $\rightarrow$ Root $\rightarrow$ Right Subtree (yields sorted keys in BST). |
| **Traversal** | Postorder Traversal | $O(n)$ | $O(n)$ | $O(h)$ | Left Subtree $\rightarrow$ Right Subtree $\rightarrow$ Root (bottom-up DFS). |
| **Traversal** | Level-Order (BFS) | $O(n)$ | $O(n)$ | $O(w)$ | Level-by-level breadth-first search using a FIFO queue. |
| **Properties** | Height & Depth Calculation | $O(n)$ | $O(n)$ | $O(h)$ | Postorder tree reduction: $1 + \max(h_L, h_R)$. |
| **Properties** | Diameter (Longest Path) | $O(n)$ | $O(n)$ | $O(h)$ | Computes $\max(\text{diameter}_L, \text{diameter}_R, h_L + h_R + 2)$. |
| **Properties** | AVL Balance Check | $O(n)$ | $O(n)$ | $O(h)$ | Verifies $|h_L - h_R| \le 1$ recursively for every node. |
| **Reconstruction** | Preorder + Inorder | $O(n)$ | $O(n)$ | $O(n)$ | Hash-indexed root lookup in inorder sequence. |
| **Reconstruction** | Inorder + Postorder | $O(n)$ | $O(n)$ | $O(n)$ | Root is postorder end; recursive partition of inorder. |
| **Reconstruction** | Level-Order + Inorder | $O(n^2)$ | $O(n^2)$ | $O(n)$ | Root from level-order, filter partitions by member set. |
| **Reconstruction** | Preorder + Postorder | $O(n)$ | $O(n)$ | $O(n)$ | Guaranteed unique for Full Binary Trees; flags ambiguity otherwise. |
| **Reconstruction** | BST from Preorder | $O(n)$ | $O(n)$ | $O(n)$ | Uses upper/lower value boundaries ($-\infty, +\infty$). |
| **Reconstruction** | BST from Postorder | $O(n)$ | $O(n)$ | $O(n)$ | Reverse-scan postorder with value bounding. |

---

## 2. Binary Search Tree (BST) Algorithms

A **Binary Search Tree** is a rooted binary tree in which each node maintains an ordered key and satisfies the **BST Invariant**:
$$\forall x \in \text{LeftSubtree}(\text{node}),\ \text{key}(x) < \text{key}(\text{node})$$
$$\forall y \in \text{RightSubtree}(\text{node}),\ \text{key}(y) > \text{key}(\text{node})$$

In this application, duplicates are supported via **frequency counters** (`freq >= 1`) attached to each unique node, preserving strict structural invariants while allowing multiset representation.

### 2.1 Search
- **Intuition**: Think of guessing a number between 1 and 100 where after every guess you are told "higher" or "lower". At each node, we compare target value $v$ with current node key. If equal, search succeeds. If $v$ is smaller, we know the target can only exist in the left branch; if larger, only in the right branch.
- **Algorithm**:
  1. If current node is `None`, return `Not Found`.
  2. If $v == \text{node.val}$, return the node and its frequency.
  3. If $v < \text{node.val}$, recurse on $\text{node.left}$.
  4. If $v > \text{node.val}$, recurse on $\text{node.right}$.
- **Complexity**: $O(h)$ time, where $h$ is height. On balanced trees, $h \approx \log_2 n$. On a skewed tree (like inserting 1, 2, 3, 4, 5 in order), $h = n$, resulting in $O(n)$ worst-case time.

### 2.2 Insert
- **Intuition**: Similar to search, but when we hit a duplicate node we simply increment its frequency counter. If we reach an empty spot (`None`), we insert a new node there.
- **Algorithm**:
  1. Follow search logic down the tree.
  2. If a node with value $v$ already exists, increment its frequency: $\text{freq} \leftarrow \text{freq} + 1$.
  3. If an empty child link is reached where $v$ belongs, create a new `TreeNode(val=v, freq=1)`.
  4. Recalculate subtree sizes and heights on the return path.
- **Complexity**: $O(h)$ comparisons and $O(h)$ stack frames.

### 2.3 Remove
- **Intuition**: Deletion must preserve the BST ordering invariant. Removing a leaf is simple; removing an internal node requires selecting an appropriate replacement that satisfies both left and right subtree properties.
- **Algorithm (The Three Classic Cases)**:
  1. **Search**: Locate the target value $v$. If absent, report not found.
  2. **Frequency Check**: If $\text{node.freq} > 1$, decrement frequency ($\text{freq} \leftarrow \text{freq} - 1$) and stop. The tree structure is unchanged.
  3. **Case 1 (Leaf Node)**: If the node has no children ($\text{left} = \text{None}$ and $\text{right} = \text{None}$), detach it from its parent.
  4. **Case 2 (Single Child)**: If the node has only one child (either left or right), bypass the node by linking the parent directly to the existing child.
  5. **Case 3 (Two Children)**:
     - Find the **Inorder Successor** (the smallest value in the right subtree: start at $\text{node.right}$ and follow $\text{left}$ links to the bottom).
     - Copy the successor's value and frequency into the current node.
     - Recursively delete the successor node from the right subtree (the successor is guaranteed to have at most one child, falling into Case 1 or Case 2).
- **Complexity**: $O(h)$ time. Finding the successor takes $O(h)$ steps down the right subtree, and recursive deletion is $O(h)$.

### 2.4 Minimum and Maximum
- **Intuition**: Because all smaller keys lie to the left and larger keys to the right, the minimum must be as far left as possible, and the maximum as far right as possible.
- **Algorithm**:
  - `FindMin(node)`: Start at root, repeatedly follow `node.left` until `node.left == None`.
  - `FindMax(node)`: Start at root, repeatedly follow `node.right` until `node.right == None`.
- **Complexity**: $O(h)$ time, requiring zero backtracking.

### 2.5 Inorder Predecessor and Successor
- **Predecessor**: The largest key strictly less than $v$.
  - *If left child exists*: Take the maximum of the left subtree (`FindMax(node.left)`).
  - *If no left child exists*: Walk down from the root searching for $v$. The predecessor is the deepest ancestor from which we turned right.
- **Successor**: The smallest key strictly greater than $v$.
  - *If right child exists*: Take the minimum of the right subtree (`FindMin(node.right)`).
  - *If no right child exists*: Walk down from the root searching for $v$. The successor is the deepest ancestor from which we turned left.
- **Complexity**: $O(h)$ time and $O(1)$ auxiliary space iteratively.

### 2.6 Order-Statistic Operations: Rank and Select
- **Rank($v$)**: Computes the 1-based index of value $v$ if all tree elements were sorted.
  - Count how many elements in the tree are strictly smaller than $v$, then add 1.
  - Efficiently computed in $O(h)$ time using subtree `size` fields:
    - If $v == \text{curr.val}$: $\text{rank} = \text{size}(\text{curr.left}) + 1$.
    - If $v < \text{curr.val}$: recurse into left subtree.
    - If $v > \text{curr.val}$: $\text{rank} = \text{size}(\text{curr.left}) + 1 + \text{Rank}(v, \text{curr.right})$.
- **Select($k$)**: Finds the $k$-th smallest value in the BST.
  - Compare $k$ against $L = \text{size}(\text{curr.left}) + 1$:
    - If $k == L$: Current node is the $k$-th element!
    - If $k < L$: Recurse into left subtree looking for $k$-th.
    - If $k > L$: Recurse into right subtree looking for $(k - L)$-th.
- **Complexity**: $O(h)$ time.

---

## 3. Tree Traversals

Tree traversal systematically visits every node in the hierarchy exactly once.

```
       A
      / \
     B   C
    / \
   D   E
```

### 3.1 Preorder Traversal (Root $\rightarrow$ Left $\rightarrow$ Right)
- **Order for above tree**: `A -> B -> D -> E -> C`
- **Concept**: The parent is inspected before its subtrees. Ideal for serializing/saving trees, copying tree structures, and evaluating prefix expressions.
- **Implementation**: Depth-first recursion or explicit LIFO stack.
- **Complexity**: $O(n)$ time, $O(h)$ space.

### 3.2 Inorder Traversal (Left $\rightarrow$ Root $\rightarrow$ Right)
- **Order for above tree**: `D -> B -> E -> A -> C`
- **Concept**: Visits the left subtree, processes the root, and visits the right subtree. **Fundamental Property**: In a Binary Search Tree, inorder traversal visits elements in strictly ascending sorted order.
- **Complexity**: $O(n)$ time, $O(h)$ space.

### 3.3 Postorder Traversal (Left $\rightarrow$ Right $\rightarrow$ Root)
- **Order for above tree**: `D -> E -> B -> C -> A`
- **Concept**: Processes children before parents (bottom-up). Essential for memory deallocation, calculating directory sizes, post-fix expression evaluation, and computing tree height/diameter.
- **Complexity**: $O(n)$ time, $O(h)$ space.

### 3.4 Level-Order Traversal (Breadth-First Search)
- **Order for above tree**: `A -> B -> C -> D -> E`
- **Concept**: Visits nodes level-by-level from top to bottom, left to right within each level.
- **Implementation**: Uses a FIFO (First-In, First-Out) queue:
  1. Enqueue `root`.
  2. While queue is not empty: dequeue node, record its value, and enqueue non-null left and right children.
- **Complexity**: $O(n)$ time, $O(w)$ space where $w$ is the tree's maximum width.

---

## 4. Tree Reconstruction Algorithms

Reconstructing a binary tree from traversal sequences is a classic problem in data structures. Two traversals are typically required because a single traversal lacks 2D structural branching information.

### 4.1 Preorder + Inorder
1. **Root Identification**: The first element of `preorder` is always the root of the tree/subtree.
2. **Subtree Partitioning**: Find this root's index $i$ in `inorder`. All items to the left of $i$ belong to the left subtree; all items to the right belong to the right subtree.
3. **Sequence Slicing**:
   - Left subtree size $k = i - \text{in\_start}$.
   - Left preorder slice: `preorder[1 : 1 + k]`.
   - Right preorder slice: `preorder[1 + k :]`.
4. **Recurse**: Build `left` and `right` subtrees recursively.
- **Optimization**: Building a hash map from value to index in `inorder` achieves $O(n)$ overall runtime instead of $O(n^2)$.

### 4.2 Inorder + Postorder
1. **Root Identification**: The last element of `postorder` is always the root of the current subtree.
2. **Subtree Partitioning**: Locate the root in `inorder`. Elements to the left form the left subtree; elements to the right form the right subtree.
3. **Recurse**: Subtrees are reconstructed recursively in $O(n)$ time.

### 4.3 Level-Order + Inorder
1. **Root Identification**: The first element in `level-order` is the root.
2. **Subtree Partitioning**: Split `inorder` into `left_inorder` and `right_inorder` around the root.
3. **Level Order Filtering**: Filter the remaining `level-order` sequence into two subsequences: one containing elements present in `left_inorder` (preserving their relative level-order), and another for `right_inorder`.
4. **Recurse**: Reconstruct left and right subtrees.
- **Complexity**: $O(n^2)$ time with hash sets for filtering.

### 4.4 Preorder + Postorder (Full Binary Trees)
- **Ambiguity**: A tree with single-child nodes cannot be uniquely reconstructed from pre+post traversals alone (e.g., root with only a left child yields the same pre and post sequences as root with only a right child).
- **Full Binary Tree Property**: If every internal node has exactly two children, the tree is unique:
  - Root is `pre[0]`.
  - Left child is `pre[1]`.
  - Find `pre[1]` in `postorder` to determine the left subtree's boundary.
- **Implementation**: The application reconstructs under the Full Binary Tree assumption and presents an explicit ambiguity warning banner whenever alternate interpretations exist.

### 4.5 BST from Single Traversal (Preorder or Postorder)
- Unlike arbitrary binary trees, a **BST** can be uniquely reconstructed from a single traversal sequence because the BST ordering invariant replaces the need for an inorder sequence.
- **Algorithm (Upper/Lower Range Bounding)**:
  - Maintain valid value bounds $(\min, \max)$, initially $(-\infty, +\infty)$.
  - For preorder: if the next token falls within $(\min, \max)$, create node, recurse left with $(\min, \text{val})$, and recurse right with $(\text{val}, \max)$.
- **Complexity**: $O(n)$ time and $O(h)$ space.

---

## 5. Tree Properties & Geometric Layout

### 5.1 Height and Diameter
- **Height**: The length of the longest downward path from root to leaf. Empty tree is $-1$ (or $0$ nodes).
- **Diameter**: The longest path between any two arbitrary nodes in the tree (which may or may not pass through the root). Calculated in $O(n)$ bottom-up postorder pass:
  $$\text{diameter}(\text{node}) = \max(\text{diam}_L,\ \text{diam}_R,\ h_L + h_R + 2)$$

### 5.2 Deterministic Canvas Layout Mathematics
To eliminate edge crossings and produce textbook-quality diagrams, `Tree_Visualizer` uses an **Inorder X-Coordinate Projection**:
1. Perform an inorder traversal of the tree, numbering nodes from left to right: $0, 1, 2, \dots, n-1$.
2. Node $X$ position:
   $$X = \text{inorder\_index} \times \Delta X + \text{margin}$$
3. Node $Y$ position:
   $$Y = \text{depth} \times \Delta Y + \text{margin}$$
This mathematical guarantee ensures that every left child is strictly to the left of its parent, every right child is strictly to the right, and no tree edges ever cross.
