# Product Requirements Document (PRD)

## Overview
A fast, keyboard-driven Windows image viewer for efficiently managing images in a directory.

## Features
- View images in a directory, scroll with left/right arrow keys.
- Delete image with `d` key.
- Rename image to a tag+sequence number with keys 1–5 (5 preprogrammed tags).
- Move images into sub-dir using tagname for subdir and renaming with seq number within directory when key 1-5 + OPT is pressed
- Enlarge/shrink image view with the cursor up/down keys or mouse wheel.
- Close with window X or ESC
- admin option to set tags
- remembers last 5 directories opened
- remembers tag settings

## To Refine
- Tag configuration and sequence management
- Supported image formats
- UI/UX details
- Error handling and confirmations

## Implemented Features
- **Thumbnail View:** Integrated into the main window, allowing drag-and-drop reordering of images. Renaming occurs immediately upon reordering, using the `directory-name_sequence-number.extension` format. Thumbnails do not display filenames, and the view includes a scrollbar.
- **Rename All Images:** Added an option to rename all images in the current directory to `directory-name_sequence-number.extension`.
- **Remember Last Directory:** The application now automatically opens the last used directory on startup if no directory is specified.

## Further Refinements
- In the thumbnails view ~I would like to be able to use the keys 1-5 and opt-1-5 and 'd' to act on the 'selected' image in the same way as they work for the main view. Pressing "Enter" or clicking with the mouse should open the selected image in the single image view.
- **Slideshow Option:** Implemented. Duration configurable via settings. Spacebar toggles start/stop/resume. Image manipulation keys (e.g., 'd') function during slideshow.
  
---
*Refine this document as requirements evolve.*
