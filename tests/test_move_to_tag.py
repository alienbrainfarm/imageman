import os
import shutil
import tempfile
import pytest
from imageman.main import ImageMan
from PyQt5.QtWidgets import QApplication

from conftest import create_dummy_image


@pytest.fixture
def temp_image_dir(tmp_path):
    # Create a temp dir with 3 images
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    for i in range(1, 4):
        create_dummy_image(img_dir / f"img{i}.jpg")
    return str(img_dir)


def test_move_to_tag_creates_dir_and_moves_file(qtbot, temp_image_dir):
    man = ImageMan(temp_image_dir)
    qtbot.addWidget(man)
    # Set tags to known values
    man.tags = ["cat", "dog", "bird", "fish", "horse"]
    man.images = man._get_images()
    man.current_index = 0
    img_name = man.images[0]
    # Move first image to tag 0 ("cat")
    man.move_current_image_to_tag(0)
    tag_dir = os.path.join(temp_image_dir, "cat")
    assert os.path.isdir(tag_dir), "Tag directory was not created"
    files = os.listdir(tag_dir)
    assert len(files) == 1, "Image was not moved into tag directory"
    assert files[0].startswith("cat_"), "Image was not renamed correctly"
    # The image should be gone from the main dir
    assert img_name not in os.listdir(temp_image_dir)


def test_move_to_tag_sequence_increment(qtbot, temp_image_dir):
    man = ImageMan(temp_image_dir)
    qtbot.addWidget(man)
    man.tags = ["cat", "dog", "bird", "fish", "horse"]
    man.images = man._get_images()
    # Move all images to tag 1 ("dog")
    for _ in range(len(man.images)):
        man.current_index = 0
        man.move_current_image_to_tag(1)
    tag_dir = os.path.join(temp_image_dir, "dog")
    files = sorted(os.listdir(tag_dir))
    assert len(files) == 3
    # Should be dog_1.jpg, dog_2.jpg, dog_3.jpg
    assert all(f.startswith("dog_") for f in files)
    nums = sorted(int(f[4:f.rfind('.')]) for f in files)
    assert nums == [1, 2, 3]
