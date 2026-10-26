# Changelog

All notable changes to the Tree_Visualizer application are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-10-26

### Added
- Pure algorithmic layout computation module (`tree_visualizer.ui.card_layout`) for canvas empty-state definition cards with zero Tkinter dependencies and support for pluggable text measurers.
- Bundled official Google Fonts under SIL Open Font License:
  - **Agbalumo** (Regular 400) for definition card narrative body and hint text.
  - **Cinzel Decorative** (Regular 400 & Bold 700) for academic definition card headings.
- Comprehensive unit test suite (`tests/test_card_layout.py`) verifying non-overlapping vertical flow across multiple canvas resolutions (from 500x350 to 1920x1080) and all tabs (`bst`, `binary`, `build`).

### Changed
- **Fixed definition card overlap**: Replaced unmeasured, hard-coded Y-coordinate positioning and center-anchor text rendering with dynamic, font-line-spaced vertical stacking. Heading, narrative body, and actionable hint blocks are guaranteed never to overlap.
- **Typography update**: Fully removed obsolete Rouge Script and Special Elite fonts and license references; bundled Agbalumo and Cinzel Decorative fonts directly with Windows GDI (`AddFontResourceExW`) process loading and `tkextrafont` support.
- **Definition font sizes increased by 20%**:
  - Heading font size scaled from 28pt to 34pt.
  - Body narrative font size scaled from 17pt to 20pt.
  - Actionable hint font size scaled from 10pt to 12pt.
  - Proportional line spacing and gaps scaled accordingly with responsive viewport constraints.
- **Reduced zoom sensitivity by 20%**:
  - Mouse wheel / trackpad zoom coefficient decreased from 0.0008 to 0.00064 (`coeff * 0.8`).
  - Zoom in/out button logarithmic step reduced by 20% from 1.10x to ~1.079x (`exp(0.8 * ln(1.10))`).
- **Window Title**: Displays application name and version as `Tree_Visualizer v1.0.1`.
- **Documentation**: Audited and updated `README.md` to accurately document speed multipliers (`0.25x`, `0.5x`, `1.0x`, `2.0x`, `4.0x`), theme palettes, typography credits, and direct release download URLs.

## [1.0.0] - 2026-10-25

### Added
- Initial release of Tree_Visualizer desktop application.
- Interactive Binary Search Tree (BST) operations (Search, Insert, Remove, Min/Max, Predecessor/Successor, Rank/Select).
- Binary tree random generation and 4 tree traversals (Preorder, Inorder, Postorder, Level-Order).
- 6 tree reconstruction modes with live diagnostic validation and repair suggestions.
- Step-by-step playback engine with scrubber, speed controls, status narrative, and synchronized pseudocode.
- Multi-format structural and image exports (JSON, PNG, SVG, Base64 share codes).
- Standalone Windows executable build packaging via PyInstaller.
