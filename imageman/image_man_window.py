import os
import winreg
import tempfile
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QMenuBar, QAction, QDialog,
    QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QWidget, QFileDialog,
    QListWidget, QListWidgetItem, QScrollArea, QApplication, QInputDialog
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer

from PIL import Image, ImageDraw
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from imageman.widgets import ImageLabel, DragDropListWidget
from imageman.dialogs import TagConfigDialog
from imageman.constants import *


class ImageMan(QMainWindow):
    def __init__(self, image_dir):
        super().__init__()
        self.recent_dirs = self._load_recent_dirs_from_registry()
        self.image_dir = image_dir
        self._add_to_recent_dirs(self.image_dir)
        self.images = self._get_images()
        self.current_index = 0
        self.show_filenames = self._load_show_filenames_from_registry()
        self.filename_label = QLabel(self)
        self.filename_label.setAlignment(Qt.AlignCenter)
        font = self.filename_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.filename_label.setFont(font)
        self.filename_label.setStyleSheet("padding: 2px 0 2px 0; margin: 0px;")
        self.filename_label.setMinimumSize(0, 0)
        self.filename_label.setVisible(self.show_filenames)
        self.label = ImageLabel(self)
        self.label.setMinimumSize(0, 0)

        self.thumbnail_view_active = False
        self._setup_thumbnail_view()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filename_label)
        layout.addWidget(self.label)
        layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(layout)
        container.setMinimumSize(0, 0)
        self.setCentralWidget(container)

        self.setWindowTitle('ImageMan')
        self.tags = self._load_tags_from_registry()
        self.tag_counters = {tag: 1 for tag in self.tags}
        self.slideshow_duration = self._load_slideshow_duration_from_registry()
        self.slideshow_timer = QTimer(self)
        self.slideshow_timer.timeout.connect(self.next_image)
        self.zoom_factor = 1.0
        self._init_menu()
        self._apply_dark_theme()

        if self.images:
            img_path = os.path.join(self.image_dir, self.images[0])
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                img_w, img_h = pixmap.width(), pixmap.height()
                label_h = FILENAME_LABEL_HEIGHT
                self._initial_win_width = img_w + WINDOW_MARGIN
                self._initial_win_height = img_h + label_h + WINDOW_MARGIN
                self.resize(self._initial_win_width, self._initial_win_height)
        else:
            self.resize(800, 600)

        self.setMinimumSize(0, 0)
        # Always start in thumbnail view, and handle rename prompt
        self.thumbnail_view_action.setChecked(True)
        self._toggle_thumbnail_view(True) # This will call _update_thumbnail_view
        self.show()

    def _load_recent_dirs_from_registry(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan", 0, winreg.KEY_READ) as key:
                dirs_str, _ = winreg.QueryValueEx(key, "recent_dirs")
                dirs = dirs_str.split(';')
                return [d for d in dirs if d.strip()]
        except Exception:
            pass
        return []

    def _save_recent_dirs_to_registry(self):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan") as key:
                dirs_str = ';'.join(self.recent_dirs)
                winreg.SetValueEx(key, "recent_dirs", 0, winreg.REG_SZ, dirs_str)
        except Exception:
            pass

    def _add_to_recent_dirs(self, dir_path):
        dir_path = os.path.abspath(dir_path)
        if dir_path in self.recent_dirs:
            self.recent_dirs.remove(dir_path)
        self.recent_dirs.insert(0, dir_path)
        self.recent_dirs = self.recent_dirs[:RECENT_DIRS_LIMIT]
        self._save_recent_dirs_to_registry()
        self._update_recent_dirs_menu()

    def _update_recent_dirs_menu(self):
        if not hasattr(self, 'recent_dirs_menu'):
            return
        self.recent_dirs_menu.clear()
        for d in self.recent_dirs:
            action = QAction(d, self)
            action.triggered.connect(lambda checked, path=d: self._open_recent_dir(path))
            self.recent_dirs_menu.addAction(action)

    def _open_recent_dir(self, dir_path):
        if os.path.isdir(dir_path):
            self.image_dir = dir_path
            self.images = self._get_images()
            self.current_index = 0
            self.zoom_factor = 1.0
            self._initial_win_height = None
            self._initial_win_width = None
            if self.images:
                img_path = os.path.join(self.image_dir, self.images[0])
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    img_w, img_h = pixmap.width(), pixmap.height()
                    label_h = FILENAME_LABEL_HEIGHT
                    self._initial_win_width = img_w + WINDOW_MARGIN
                    self._initial_win_height = img_h + label_h + WINDOW_MARGIN
                    self.resize(self._initial_win_width, self._initial_win_height)
            else:
                self.resize(800, 600)
            self._add_to_recent_dirs(dir_path)
            self._show_image()

    def move_current_image_to_tag(self, idx):
        """
        Move the current image to a subdirectory named after the tag (creating it if needed),
        and rename it to tagname_N.ext where N is the next available sequence number in that subdir.
        """
        if not self.images or idx < 0 or idx >= len(self.tags):
            return
        tag = self.tags[idx]
        old_name = self.images[self.current_index]
        ext = os.path.splitext(old_name)[1]
        tag_dir = os.path.abspath(os.path.join(self.image_dir, tag))
        try:
            if not os.path.isdir(tag_dir):
                os.makedirs(tag_dir)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error creating directory: {e}')
            return
        existing = [f for f in os.listdir(tag_dir) if f.lower().endswith(ext.lower()) and f.startswith(tag + '_')]
        max_seq = 0
        for f in existing:
            try:
                seq_part = f[len(tag)+1:f.rfind('.')] 
                seq = int(seq_part)
                if seq > max_seq:
                    max_seq = seq
            except Exception:
                continue
        seq = max_seq + 1
        new_name = f"{tag}_{seq:04d}{ext}"
        old_path = os.path.join(self.image_dir, old_name)
        new_path = os.path.join(tag_dir, new_name)
        while os.path.exists(new_path):
            seq += 1
            new_name = f"{tag}_{seq:04d}{ext}"
            new_path = os.path.join(tag_dir, new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error moving image: {e}')
            return
        del self.images[self.current_index]
        if self.current_index >= len(self.images):
            self.current_index = 0 if self.images else 0
        self._show_image()

    def resizeEvent(self, event):
        if self.isVisible() and hasattr(self, '_initial_win_height') and self._initial_win_height is not None and self._initial_win_width is not None:
            self._initial_win_width = self.width()
            self._initial_win_height = self.height()
            self._show_image()
        super().resizeEvent(event)

    def _load_tags_from_registry(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan", 0, winreg.KEY_READ) as key:
                tags_str, _ = winreg.QueryValueEx(key, "tags")
                tags = tags_str.split(';')
                if len(tags) == NUM_TAGS:
                    return tags
        except Exception:
            pass
        return ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']

    def _save_tags_to_registry(self):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan") as key:
                tags_str = ';'.join(self.tags)
                winreg.SetValueEx(key, "tags", 0, winreg.REG_SZ, tags_str)
        except Exception:
            pass

    def _load_slideshow_duration_from_registry(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan", 0, winreg.KEY_READ) as key:
                duration, _ = winreg.QueryValueEx(key, "slideshow_duration")
                return float(duration)
        except Exception:
            pass
        return DEFAULT_SLIDESHOW_DURATION # Default duration

    def _save_slideshow_duration_to_registry(self):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan") as key:
                winreg.SetValueEx(key, "slideshow_duration", 0, winreg.REG_SZ, str(self.slideshow_duration))
        except Exception:
            pass

    def _load_show_filenames_from_registry(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan", 0, winreg.KEY_READ) as key:
                show_filenames_str, _ = winreg.QueryValueEx(key, "show_filenames")
                return show_filenames_str == "True"
        except Exception:
            pass
        return True  # Default to showing filenames

    def _save_show_filenames_to_registry(self):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan") as key:
                winreg.SetValueEx(key, "show_filenames", 0, winreg.REG_SZ, str(self.show_filenames))
        except Exception:
            pass

    def _show_image(self):
        if not self.images:
            QMessageBox.information(self, 'No Images', 'No images found in this directory.')
            self.filename_label.setText('')
            self.label.clear() # Clear any previous image
            self.filename_label.setVisible(self.show_filenames)
            return
        img_name = self.images[self.current_index]
        img_path = os.path.join(self.image_dir, img_name)
        self.filename_label.setText(img_name)
        self.filename_label.setVisible(self.show_filenames)
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            QMessageBox.warning(self, 'Image Load Error', f'Cannot load image: {img_name}. It might be corrupted or an unsupported format.')
            self.label.clear() # Clear any previous image
            return
        img_w, img_h = pixmap.width(), pixmap.height()
        scaled_w = int(img_w * self.zoom_factor)
        scaled_h = int(img_h * self.zoom_factor)
        available_w = max(1, self.centralWidget().width() - 20)
        available_h = max(1, self.centralWidget().height() - AVAILABLE_HEIGHT_OFFSET)
        if scaled_w > available_w or scaled_h > available_h:
            ratio = min(available_w / scaled_w, available_h / scaled_h, 1.0)
            scaled_w = int(scaled_w * ratio)
            scaled_h = int(scaled_h * ratio)
        scaled_pixmap = pixmap.scaled(scaled_w, scaled_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)

    def _get_images(self):
        supported = SUPPORTED_IMAGE_FORMATS
        images = sorted([f for f in os.listdir(self.image_dir) if f.lower().endswith(supported)])
        
        return images

    def _delete_current_image(self):
        if not self.images:
            return
        img_path = os.path.join(self.image_dir, self.images[self.current_index])
        try:
            os.remove(img_path)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error deleting image: {e}')
            return
        del self.images[self.current_index]
        if self.current_index >= len(self.images):
            self.current_index = max(0, len(self.images) - 1)
        self._show_image()

    def _rename_current_image(self, tag):
        if not self.images:
            return
        old_name = self.images[self.current_index]
        ext = os.path.splitext(old_name)[1]
        seq = self.tag_counters[tag]
        new_name = f"{tag}_{seq:04d}{ext}"
        old_path = os.path.join(self.image_dir, old_name)
        new_path = os.path.join(self.image_dir, new_name)
        while os.path.exists(new_path):
            seq += 1
            new_name = f"{tag}_{seq:04d}{ext}"
            new_path = os.path.join(self.image_dir, new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error renaming image: {e}')
            return
        self.images[self.current_index] = new_name
        self.tag_counters[tag] = seq + 1
        self._show_image()

    def delete_current_image(self):
        self._delete_current_image()

    def rename_current_image(self, tag):
        self._rename_current_image(tag)

    def zoom_in(self):
        self.zoom_factor = min(self.zoom_factor * 1.25, 10.0)
        self._show_image()

    def zoom_out(self):
        self.zoom_factor = max(self.zoom_factor * 0.8, 0.1)
        self._show_image()

    def next_image(self):
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self._show_image()

    def prev_image(self):
        if self.images:
            self.current_index = (self.current_index - 1 + len(self.images)) % len(self.images)
            self._show_image()

    def _init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_dir_action = QAction('Open Directory...', self)
        open_dir_action.triggered.connect(self._select_directory)
        file_menu.addAction(open_dir_action)

        self.recent_dirs_menu = file_menu.addMenu('Recent Directories')
        self._update_recent_dirs_menu()

        rename_all_action = QAction('Rename All Images...', self)
        rename_all_action.triggered.connect(self._rename_all_images)
        file_menu.addAction(rename_all_action)

        create_video_action = QAction('Create Slideshow Video...', self)
        create_video_action.triggered.connect(self._create_slideshow_video)
        file_menu.addAction(create_video_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('View')
        self.thumbnail_view_action = QAction('Thumbnail View', self)
        self.thumbnail_view_action.setCheckable(True)
        self.thumbnail_view_action.triggered.connect(self._toggle_thumbnail_view)
        view_menu.addAction(self.thumbnail_view_action)

        config_menu = menubar.addMenu('Config')
        tag_action = QAction('Configure Tags', self)
        tag_action.triggered.connect(self._show_tag_dialog)
        config_menu.addAction(tag_action)

        self.show_filenames_action = QAction('Show Filenames', self)
        self.show_filenames_action.setCheckable(True)
        self.show_filenames_action.setChecked(self.show_filenames)
        self.show_filenames_action.triggered.connect(self._toggle_filename_display)
        config_menu.addAction(self.show_filenames_action)

    def _get_rename_map(self):
        rename_map = {}
        if not self.images:
            return rename_map

        dir_name = os.path.basename(os.path.abspath(self.image_dir))
        
        # Get the current order of images
        current_images_order = self._get_images() # This will get the actual files on disk sorted

        # Compare with the desired order (dir_name_0001.ext, dir_name_0002.ext, ...)
        for i, old_name in enumerate(current_images_order):
            ext = os.path.splitext(old_name)[1]
            new_name = f"{dir_name}_{i+1:04d}{ext}"
            old_path = os.path.join(self.image_dir, old_name)
            new_path = os.path.join(self.image_dir, new_name)
            
            if old_path.lower() != new_path.lower():
                rename_map[old_path] = new_path
        return rename_map

    def _perform_rename(self, rename_map):
        try:
            temp_files = {}
            for old_path, new_path in rename_map.items():
                if os.path.exists(new_path):
                    temp_path = new_path + '.tmp'
                    os.rename(old_path, temp_path)
                    temp_files[new_path] = temp_path
                else:
                    os.rename(old_path, new_path)

            for final_path, temp_path in temp_files.items():
                os.rename(temp_path, final_path)

        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {e}')

    def _rename_all_images(self, confirm=True):
        rename_map = self._get_rename_map()
        if not rename_map: # No renaming needed
            return True # Indicate success (no rename was needed)

        dir_name = os.path.basename(os.path.abspath(self.image_dir))
        
        if confirm:
            reply = QMessageBox.question(self, 'Rename All',
                                         f"Rename all images to \"{dir_name}_N.ext\"",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                # User declined rename, switch to single image view
                self.thumbnail_view_action.setChecked(False)
                self._toggle_thumbnail_view(False)
                return False # Indicate rename was declined

        self._perform_rename(rename_map)

        self.images = self._get_images()
        self.current_index = 0
        if not self.thumbnail_view_active:
            self._show_image()
        return True # Indicate rename was performed

    def _select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Image Directory', self.image_dir)
        if dir_path:
            self.image_dir = dir_path
            self._add_to_recent_dirs(dir_path)
            self.images = self._get_images()
            self.current_index = 0
            self.zoom_factor = 1.0
            self._initial_win_height = None
            self._initial_win_width = None
            if self.images:
                img_path = os.path.join(self.image_dir, self.images[0])
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    img_w, img_h = pixmap.width(), pixmap.height()
                    label_h = FILENAME_LABEL_HEIGHT
                    self._initial_win_width = img_w + WINDOW_MARGIN
                    self._initial_win_height = img_h + label_h + WINDOW_MARGIN
                    self.resize(self._initial_win_width, self._initial_win_height)
            else:
                self.resize(800, 600)
            # Always go to thumbnail view after selecting a directory
            self.thumbnail_view_action.setChecked(True)
            self._toggle_thumbnail_view(True)

    def _apply_dark_theme(self):
        dark_stylesheet = """
        QWidget {
            background-color: #232629;
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QMenuBar {
            background-color: #232629;
            color: #e0e0e0;
        }
        QMenuBar::item:selected {
            background: #444;
        }
        QMenu {
            background-color: #232629;
            color: #e0e0e0;
        }
        QMenu::item:selected {
            background: #444;
        }
        QPushButton {
            background-color: #444;
            color: #e0e0e0;
            border: 1px solid #666;
            border-radius: 4px;
            padding: 4px 8px;
        }
        QLineEdit {
            background-color: #2c2f34;
            color: #e0e0e0;
            border: 1px solid #666;
            border-radius: 4px;
        }
        QMessageBox {
            background-color: #232629;
            color: #e0e0e0;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def _show_tag_dialog(self):
        dialog = TagConfigDialog(self.tags, self)
        if dialog.exec_():
            new_tags = dialog.get_tags()
            new_duration = dialog.get_slideshow_duration()
            if new_duration is None:
                # If duration is invalid, the dialog already showed a warning.
                # We should not proceed with saving changes.
                return

            if len(set(new_tags)) != NUM_TAGS or any(not t.strip() for t in new_tags):
                QMessageBox.warning(self, 'Invalid Tags', 'Tags must be 5 unique, non-empty values.')
                return
            self.tags = new_tags
            self.tag_counters = {tag: 1 for tag in self.tags}
            self._save_tags_to_registry()
            self.slideshow_duration = new_duration
            self._save_slideshow_duration_to_registry()

    def _setup_thumbnail_view(self):
        self.thumbnail_list_widget = DragDropListWidget(self)
        self.thumbnail_list_widget.itemDoubleClicked.connect(self._thumbnail_double_clicked)
        self.thumbnail_list_widget.setIconSize(QSize(128, 128))
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.thumbnail_list_widget)
        self.scroll_area.hide()

    def _toggle_thumbnail_view(self, checked):
        self.thumbnail_view_active = checked
        if checked:
            self.label.hide()
            self.filename_label.hide()
            self.scroll_area.show()
            self._update_thumbnail_view()
        else:
            self.scroll_area.hide()
            self.label.show()
            self.filename_label.show()
            self._show_image()
            self.label.setFocus()

    def _update_thumbnail_view(self):
        self.thumbnail_list_widget.clear()
        self.images = self._get_images()
        for image_name in self.images:
            item = QListWidgetItem()
            icon_path = os.path.join(self.image_dir, image_name)
            item.setIcon(QIcon(icon_path))
            item.setData(Qt.UserRole, image_name)
            if self.show_filenames:
                item.setText(image_name)
            else:
                item.setText("")
            self.thumbnail_list_widget.addItem(item)

    def _thumbnail_double_clicked(self, item):
        clicked_image_name = item.data(Qt.UserRole)
        
        if clicked_image_name in self.images:
            self.current_index = self.images.index(clicked_image_name)
            
            
            self.thumbnail_view_action.setChecked(False)
            self._toggle_thumbnail_view(False)
            self._show_image()

    def on_item_dropped(self):
        new_images = [self.thumbnail_list_widget.item(i).data(Qt.UserRole) for i in range(self.thumbnail_list_widget.count())]
        self.images = new_images
        self._rename_all_images(confirm=False)
        self._update_thumbnail_view()

    def delete_thumbnail_image(self, image_name):
        if image_name in self.images:
            idx_to_delete = self.images.index(image_name)
            img_path = os.path.join(self.image_dir, self.images[idx_to_delete])
            try:
                os.remove(img_path)
                del self.images[idx_to_delete] # Update self.images immediately
                
                # Calculate new current_index
                if not self.images: # No images left
                    self.current_index = 0
                elif idx_to_delete >= len(self.images): # Deleted last image
                    self.current_index = len(self.images) - 1
                else: # Deleted an image in the middle or first
                    self.current_index = idx_to_delete # Keep index, it now points to the next image
                
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error deleting image: {e}')
            finally:
                self._update_thumbnail_view() # This will re-read images and update the list widget
                # After _update_thumbnail_view, select the item if in thumbnail view
                if self.thumbnail_view_active and self.images:
                    self.thumbnail_list_widget.setCurrentRow(self.current_index)
                    self.thumbnail_list_widget.scrollToItem(self.thumbnail_list_widget.item(self.current_index))

    def rename_thumbnail_image(self, image_name, tag):
        if image_name in self.images:
            idx = self.images.index(image_name)
            old_name = self.images[idx]
            ext = os.path.splitext(old_name)[1]
            seq = self.tag_counters[tag]
            new_name = f"{tag}_{seq:04d}{ext}"
            old_path = os.path.join(self.image_dir, old_name)
            new_path = os.path.join(self.image_dir, new_name)
            while os.path.exists(new_path):
                seq += 1
                new_name = f"{tag}_{seq:04d}{ext}"
                new_path = os.path.join(self.image_dir, new_name)
            try:
                os.rename(old_path, new_path)
                self.images[idx] = new_name
                self.tag_counters[tag] = seq + 1
                self._update_thumbnail_view()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error renaming image: {e}')

    def move_thumbnail_image_to_tag(self, image_name, idx):
        if image_name in self.images:
            current_idx = self.images.index(image_name)
            tag = self.tags[idx]
            old_name = self.images[current_idx]
            ext = os.path.splitext(old_name)[1]
            tag_dir = os.path.abspath(os.path.join(self.image_dir, tag))
            try:
                if not os.path.isdir(tag_dir):
                    os.makedirs(tag_dir)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error creating directory: {e}')
                return
            existing = [f for f in os.listdir(tag_dir) if f.lower().endswith(ext.lower()) and f.startswith(tag + '_')]
            max_seq = 0
            for f in existing:
                try:
                    seq_part = f[len(tag)+1:f.rfind('.')]
                    seq = int(seq_part)
                    if seq > max_seq:
                        max_seq = seq
                except Exception:
                    continue
            seq = max_seq + 1
            new_name = f"{tag}_{seq:04d}{ext}"
            old_path = os.path.join(self.image_dir, old_name)
            new_path = os.path.join(tag_dir, new_name)
            while os.path.exists(new_path):
                seq += 1
                new_name = f"{tag}_{seq:04d}{ext}"
                new_path = os.path.join(tag_dir, new_name)
            try:
                os.rename(old_path, new_path)
                del self.images[current_idx] # Update self.images immediately

                # Calculate new current_index
                if not self.images: # No images left
                    self.current_index = 0
                elif current_idx >= len(self.images): # Moved last image
                    self.current_index = len(self.images) - 1
                else: # Moved an image in the middle or first
                    self.current_index = current_idx # Keep index, it now points to the next image

                self._update_thumbnail_view()
                # After _update_thumbnail_view, select the item if in thumbnail view
                if self.thumbnail_view_active and self.images:
                    self.thumbnail_list_widget.setCurrentRow(self.current_index)
                    self.thumbnail_list_widget.scrollToItem(self.thumbnail_list_widget.item(self.current_index))
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error moving image: {e}')

    def open_thumbnail_in_single_view(self, image_name):
        
        

        try:
            self.current_index = self.images.index(image_name)
            
            self.thumbnail_view_action.setChecked(False)
            self._toggle_thumbnail_view(False)
            self._show_image()
        except ValueError:
            
            
            QMessageBox.warning(self, 'Error', f'Could not find image {image_name} in the list.')
        except IndexError:
            
            
            
            QMessageBox.warning(self, 'Error', f'An unexpected error occurred while finding image {image_name}.')
        except Exception as e:
            
            QMessageBox.warning(self, 'Error', f'An unexpected error occurred: {e}')

    def start_slideshow(self):
        if self.images:
            self.slideshow_timer.start(int(self.slideshow_duration * 1000))

    def stop_slideshow(self):
        self.slideshow_timer.stop()

    def toggle_slideshow(self):
        if self.slideshow_timer.isActive():
            self.stop_slideshow()
        else:
            self.start_slideshow()

    def _toggle_filename_display(self, checked):
        self.show_filenames = checked
        self._save_show_filenames_to_registry()
        self._refresh_display()

    def _refresh_display(self):
        if self.thumbnail_view_active:
            self._update_thumbnail_view()
        else:
            self._show_image()

    def _create_slideshow_video(self):
        if not self.images:
            QMessageBox.information(self, "No Images", "No images found in the current directory to create a slideshow.")
            return

        # 1. Get minimum video length from user
        min_length_minutes, ok = QInputDialog.getInt(
            self,
            "Slideshow Video Length",
            "Enter minimum video length in minutes:",
            value=1, min=1, max=60
        )
        if not ok:
            return

        min_length_seconds = min_length_minutes * 60

        # 2. Create temporary directory for processed images
        temp_dir = os.path.join(self.image_dir, "_temp_slideshow_images")
        os.makedirs(temp_dir, exist_ok=True)

        processed_image_paths = []
        target_width, target_height = 1920, 1080

        try:
            QMessageBox.information(self, "Processing Images", "Resizing and processing images for video. This may take a moment...")
            for i, image_name in enumerate(self.images):
                original_path = os.path.join(self.image_dir, image_name)
                try:
                    img = Image.open(original_path)
                except Exception as e:
                    QMessageBox.warning(self, "Image Error", f"Could not open image {image_name}: {e}")
                    continue

                # Calculate aspect ratio and resize
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                target_aspect_ratio = target_width / target_height

                if aspect_ratio > target_aspect_ratio:
                    # Image is wider than target, fit to width
                    new_width = target_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    # Image is taller or same aspect ratio, fit to height
                    new_height = target_height
                    new_width = int(new_height * aspect_ratio)

                resized_img = img.resize((new_width, new_height), Image.LANCZOS)

                # Create black background and paste resized image
                new_image = Image.new("RGB", (target_width, target_height), (0, 0, 0)) # Black background
                paste_x = (target_width - new_width) // 2
                paste_y = (target_height - new_height) // 2
                new_image.paste(resized_img, (paste_x, paste_y))

                processed_path = os.path.join(temp_dir, f"processed_{i:04d}.png")
                new_image.save(processed_path)
                processed_image_paths.append(processed_path)

            if not processed_image_paths:
                QMessageBox.warning(self, "No Images Processed", "No valid images were processed for the slideshow.")
                return

            # 3. Calculate video duration and loop count
            single_pass_duration = len(processed_image_paths) * self.slideshow_duration
            loop_count = max(1, int(min_length_seconds / single_pass_duration) + 1)

            final_clip_images = []
            for _ in range(loop_count):
                final_clip_images.extend(processed_image_paths)

            # 4. Create video using moviepy
            QMessageBox.information(self, "Creating Video", "Generating MP4 video. This may take some time...")
            clip = ImageSequenceClip(final_clip_images, fps=1/self.slideshow_duration)
            output_video_path = os.path.join(self.image_dir, "slideshow.mp4")
            clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=24) # Using 24 fps for smooth video

            QMessageBox.information(self, "Video Created", f"Slideshow video created successfully at: {output_video_path}")

        except Exception as e:
            QMessageBox.critical(self, "Video Creation Error", f"An error occurred during video creation: {e}")
        finally:
            # 5. Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
