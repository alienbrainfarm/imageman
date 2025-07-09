# Development Plan: ImageMan

## 1. Project Setup
- Initialize Python project structure
- Add requirements.txt for dependencies (PyQt5 or PySide6, pytest)
- Add initial test structure

## 2. Core Functionality (MVP)
- Implement main window with image display
- Load images from a directory
- Navigate images with left/right arrow keys
- Unit tests: image loading, navigation

## 3. File Operations
- Delete image with `d` key
- Rename image with keys 1–5 (preprogrammed tags)
- Unit tests: file deletion, renaming logic

## 4. View Controls
- Enlarge/shrink image view with cursor up and down keys or mouse wheel
- Unit tests: zoom logic

## 5. Application Controls
- Close with window X or ESC
- Unit tests: application exit

## 6. Configuration & Tag Management
- Allow configuration of tags
- Sequence number management
- Unit tests: tag/sequence logic

## 7. Polish & Documentation
- Error handling, confirmations
- Supported image formats
- Update README and PRD



## 9. Code Refactoring
- Separated UI components (widgets, dialogs) into dedicated files (`widgets.py`, `dialogs.py`).
- Centralized main application logic in `image_man_window.py`.
- Simplified `main.py` to act as a minimal entry point.
---

*After each step, run and extend unit tests to ensure stability.*
