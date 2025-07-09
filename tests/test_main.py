import os
import pytest
from imageman.main import ImageMan
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QKeyEvent
import sys

from conftest import create_dummy_image


def test_get_images(tmp_path, qtbot):
    # Create dummy images
    img_names = ['a.jpg', 'b.png', 'c.txt']
    for name in img_names:
        create_dummy_image(tmp_path / name)
    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)
    assert set(viewer.images) == {'a.jpg', 'b.png'}
    assert viewer.current_index == 0


def test_delete_image(tmp_path, qtbot):
    # Create dummy images
    img_names = ['a.jpg', 'b.png']
    for name in img_names:
        create_dummy_image(tmp_path / name)
    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)
    assert len(viewer.images) == 2
    # Simulate delete key press
    viewer.delete_current_image()
    # Only one image should remain
    assert len(viewer.images) == 1
    # The file should be deleted from disk
    remaining = viewer.images[0]
    assert os.path.exists(tmp_path / remaining)
    deleted = set(img_names) - set(viewer.images)
    for d in deleted:
        assert not os.path.exists(tmp_path / d)


def test_rename_image(tmp_path, qtbot):
    img_names = ['a.jpg', 'b.png']
    for name in img_names:
        create_dummy_image(tmp_path / name)
    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)
    # Explicitly set tags to default to make test independent of registry
    default_tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']
    viewer.tags = default_tags
    viewer.tag_counters = {tag: 1 for tag in default_tags}
    assert viewer.images[0] == 'a.jpg'
    # Simulate pressing key '1' to rename to tag1_1.jpg
    viewer.rename_current_image('tag1')
    # The file should be renamed
    assert viewer.images[0].startswith('tag1_')
    assert viewer.images[0].endswith('.jpg')


def test_zoom_logic(tmp_path, qtbot):
    img_name = 'a.jpg'
    create_dummy_image(tmp_path / img_name)
    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)
    orig_zoom = viewer.zoom_factor
    # Simulate pressing 'q' to zoom in
    viewer.zoom_in()
    assert viewer.zoom_factor > orig_zoom
    viewer.zoom_out()
    assert viewer.zoom_factor < orig_zoom * 1.25  # Should be less than after zoom in


def test_tag_configuration(tmp_path, qtbot):
    viewer = ImageMan(str(tmp_path))
    qtbot.addWidget(viewer)
    # Simulate changing tags
    new_tags = ['cat', 'dog', 'bird', 'fish', 'horse']
    viewer.tags = new_tags
    viewer.tag_counters = {tag: 1 for tag in new_tags}
    # Simulate pressing key '2' to rename to dog_1
    img_name = 'a.jpg'
    create_dummy_image(tmp_path / img_name)
    viewer.images = [img_name]
    viewer.current_index = 0
    viewer.rename_current_image('dog')
    assert viewer.images[0].startswith('dog_')
