# ImageMan

A fast, keyboard-driven Windows image viewer for efficient image management.
The intention was to create something lightweight and fast.
There are no questions asked here ESC will kill the program immediatly and "d" will delete the current image and move to viewing the next.

## Features
- Browse images in a directory
- Scroll through the images with the arrow keys
- Delete images with `d`
- Rename images with preprogrammed TAGS (keys 1–5)   $TAG-SEQUENCENR automatically finds seq nr
- Move and rename images into sub dir named/auto-created with ( keys opt 1-5 )
- Resize view with the arrow keys
- Close the app with top right corner X or ESC
- remembers last 5 directories
- remembers 5 TAGS for renaming or creating subdirs and moving images to them

## Installation

Download and run the installer: [ImageManSetup.exe](ImageManSetup.exe)

The installer will:
- Install ImageMan to your Program Files.
- Add a Start Menu and optional Desktop shortcut.
- Add an 'Open with ImageMan' option to the right-click menu for folders.

Once installed, you can launch ImageMan from the Start Menu, Desktop, or by right-clicking any folder and choosing 'Open with ImageMan'.

## New Features & Fixes

### Thumbnail View Enhancements
- **Double-Click to View:** Double-clicking an image in the thumbnail view now opens it in the single-image view.
- **Keyboard Actions:**
    - Press `d` to delete the selected image.
    - Press `1-5` to rename the selected image with a pre-programmed tag.
    - Press `Ctrl/Alt + 1-5` to move and rename the selected image into a subdirectory named after the tag.
- **Automatic Selection:** After deleting or moving an image in thumbnail view, the next available image is automatically selected.

### Single Image View Navigation
- **Arrow Key Navigation:** Use the left and right arrow keys to navigate between images.

### Slideshow Functionality
- **Toggle Slideshow:** Press the `Spacebar` to start, pause, or resume the slideshow.

### Configuration
- **Configure Tags:** Access the "Configure Tags" dialog from the "Config" menu to customize your tags and slideshow duration.

## Documentation
See `docs/PRD.md` for the evolving product requirements.
