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
- **Thumbnail View:**
  - Integrated thumbnail view directly into the main window.
  - Implemented drag-and-drop reordering with immediate renaming of affected files.
  - Thumbnails no longer display filenames.
  - Added a scrollbar for navigation.
  - **Double-Click to View:** Double-clicking an image in the thumbnail view now opens it in the single-image view.
  - **Keyboard Actions:**
      - Press `d` to delete the selected image.
      - Press `1-5` to rename the selected image with a pre-programmed tag.
      - Press `Ctrl/Alt + 1-5` to move and rename the selected image into a subdirectory named after the tag.
  - **Automatic Selection:** After deleting or moving an image in thumbnail view, the next available image is automatically selected.
- **Immediate Directory Rename:**
  - Implemented menu option to rename all images in the current directory to `directory-name_sequence-number.extension`.
- **Remember Last Directory:**
  - Application now saves and loads the last used directory.
- **Slideshow Functionality:**
  - Implemented slideshow functionality with configurable duration.
  - Spacebar toggles start/stop/resume.
  - Image manipulation keys (delete, rename, move to tag) work during slideshow.
  - **Toggle Slideshow:** Press the `Spacebar` to start, pause, or resume the slideshow.
- **Single Image View Navigation:**
  - **Arrow Key Navigation:** Use the left and right arrow keys to navigate between images.
- **Configuration:**
  - **Configure Tags:** Access the "Configure Tags" dialog from the "Config" menu to customize your tags and slideshow duration.
  
---
*Refine this document as requirements evolve.*
