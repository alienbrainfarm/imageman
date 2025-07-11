import os
import pytest
from imageman.main import ImageMan
from PyQt5.QtWidgets import QApplication, QInputDialog
from PyQt5.QtGui import QKeyEvent
import shutil
import sys

from conftest import create_dummy_image


def test_get_images(qtbot):
    viewer = ImageMan("C:/Users/john/repos/imageman/tests")
    qtbot.addWidget(viewer)
    assert set(viewer.images) == {'image1.jpg', 'image2.png', 'image3.jpg', 'woman1.webp'}
    assert viewer.current_index == 0


def test_delete_image(qtbot, tmp_path):
    # Create a temporary directory and copy the test images to it
    for img in ["image1.jpg", "image2.png", "image3.jpg", "woman1.webp"]:
        shutil.copy(f"C:/Users/john/repos/imageman/tests/{img}", tmp_path)

    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)
    assert len(viewer.images) == 4
    # Simulate delete key press
    viewer.delete_current_image()
    # Only one image should remain
    assert len(viewer.images) == 3





def test_zoom_logic(qtbot):
    viewer = ImageMan("C:/Users/john/repos/imageman/tests")
    qtbot.addWidget(viewer)
    orig_zoom = viewer.zoom_factor
    # Simulate pressing 'q' to zoom in
    viewer.zoom_in()
    assert viewer.zoom_factor > orig_zoom
    viewer.zoom_out()
    assert viewer.zoom_factor < orig_zoom * 1.25  # Should be less than after zoom in

def test_create_slideshow_video(qtbot, tmp_path, monkeypatch):
    # Create a temporary directory and copy the test images to it
    for img in ["image1.jpg", "image2.png", "image3.jpg", "woman1.webp"]:
        shutil.copy(f"C:/Users/john/repos/imageman/tests/{img}", tmp_path)

    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)

    # Mock the QInputDialog to avoid GUI interaction
    monkeypatch.setattr(QInputDialog, 'getInt', lambda *args, **kwargs: (1, True))

    viewer._create_slideshow_video()

    assert os.path.exists(os.path.join(tmp_path, "slideshow.mp4"))



