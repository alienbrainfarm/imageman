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

First run build_portable.bat to build a portable executable.

You can build an installer yourself by running NSIS with the provided imageman_installer.nsi file.

 see: https://nsis.sourceforge.io/Main_Page

The installer will:
- Install ImageMan to your Program Files.
- Add a Start Menu and optional Desktop shortcut.
- Add an 'Open with ImageMan' option to the right-click menu for folders.

Once installed, you can launch ImageMan from the Start Menu, Desktop, or by right-clicking any folder and choosing 'Open with ImageMan'.

## Documentation
See `docs/PRD.md` for the evolving product requirements.
