# ImageMan Project Overview for Gemini CLI

This document provides essential information about the `ImageMan` project to assist the Gemini CLI agent in understanding and interacting with the codebase.

## 1. Project Purpose
ImageMan is a fast, keyboard-driven Windows image viewer designed for efficient image management, including browsing, deletion, renaming, and moving images.

## 2. Key Technologies
- **Frontend/GUI:** PyQt5
- **Language:** Python
- **Build System:** PyInstaller (for creating executables)
- **Testing Framework:** pytest

## 3. Project Structure
- `imageman/`: Contains the core application source code.
- `tests/`: Contains unit tests for the application.
- `docs/`: Contains project documentation, including PRD and development plans.
- `venv/`: Python virtual environment.
- `build_portable.bat`: Script to build the portable executable.
- `start_imageman.bat`: Script to run the application.
- `requirements.txt`: Lists Python dependencies.

## 4. Important Files & Directories
- `imageman/image_man_window.py`: Main application window logic.
- `imageman/widgets.py`: Custom PyQt widgets and key event handling.
- `imageman/dialogs.py`: PyQt dialogs for configuration.
- `imageman/constants.py`: Defines application-wide constants.
- `docs/PRD.md`: Detailed product requirements and implemented features.
- `docs/REVIEW.md`: Code review findings and suggestions for improvement.
- `requirements.txt`: Project dependencies.

## 5. Build & Run Commands
- **Run Application:** `start_imageman.bat`
- **Build Portable Executable:** `build_portable.bat`

## 6. Test Commands
- **Run Tests:** `pytest` (from the project root, after activating the virtual environment: `.\venv\Scripts\activate`)

## 7. Project-Specific Notes & Conventions
- **Configuration Storage:** Application settings (recent directories, tags, slideshow duration) are stored in the Windows Registry under `HKEY_CURRENT_USER\Software\ImageMan`.
- **Keyboard-Driven:** The application is primarily designed for keyboard navigation and actions.
- **Code Quality:** `docs/REVIEW.md` highlights areas for potential refactoring, such as hardcoded values and duplicated logic. Refer to this document for ongoing code improvement efforts.
- **Testing Practices:**
  - Tests include timeouts to prevent indefinite waiting.
  - Real image files are created for testing to avoid UI pop-ups and ensure accurate behavior.
