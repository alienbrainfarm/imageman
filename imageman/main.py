import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QMenuBar, QAction, QDialog,
    QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QWidget, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import winreg

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAlignment(Qt.AlignCenter)

    def keyPressEvent(self, event):
        parent = self.window()
        if not parent:
            super().keyPressEvent(event)
            return
        if event.key() == Qt.Key_Right:
            parent.next_image()
        elif event.key() == Qt.Key_Left:
            parent.prev_image()
        elif event.key() == Qt.Key_D:
            parent.delete_current_image()
        elif event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]:
            idx = event.key() - Qt.Key_1
            # Use Ctrl+number or Alt+number for move-to-tag (for maximum compatibility)
            if (event.modifiers() & Qt.ControlModifier) or (event.modifiers() & Qt.AltModifier):
                parent.move_current_image_to_tag(idx)
            else:
                parent.rename_current_image(parent.tags[idx])
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
            parent.zoom_in()
        elif event.key() in [Qt.Key_Q, Qt.Key_A, Qt.Key_Down]:
            parent.zoom_out()
        elif event.key() == Qt.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)

class ImageMan(QMainWindow):
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
        self.recent_dirs = self.recent_dirs[:5]
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
                    label_h = 32
                    self._initial_win_width = img_w + 20
                    self._initial_win_height = img_h + label_h + 20
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
            self.label.setText(f'Error creating directory: {e}')
            return
        # Find next available sequence number in the tag directory
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
        new_name = f"{tag}_{seq}{ext}"
        old_path = os.path.join(self.image_dir, old_name)
        new_path = os.path.join(tag_dir, new_name)
        # Avoid overwriting (shouldn't happen, but just in case)
        while os.path.exists(new_path):
            seq += 1
            new_name = f"{tag}_{seq}{ext}"
            new_path = os.path.join(tag_dir, new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            self.label.setText(f'Error moving image: {e}')
            return
        # Remove from current list and move to next image
        del self.images[self.current_index]
        if self.current_index >= len(self.images):
            self.current_index = 0 if self.images else 0
        self._show_image()
    def resizeEvent(self, event):
        # When the window is resized by the user, update the initial window size and rescale the image
        if self.isVisible() and self._initial_win_height is not None and self._initial_win_width is not None:
            self._initial_win_width = self.width()
            self._initial_win_height = self.height()
            self._show_image()
        super().resizeEvent(event)
    def __init__(self, image_dir):
        super().__init__()
        self.recent_dirs = self._load_recent_dirs_from_registry()
        self.image_dir = image_dir
        self._add_to_recent_dirs(self.image_dir)
        self.images = self._get_images()
        self.current_index = 0
        self.filename_label = QLabel(self)
        self.filename_label.setAlignment(Qt.AlignCenter)
        font = self.filename_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.filename_label.setFont(font)
        self.filename_label.setStyleSheet("padding: 2px 0 2px 0; margin: 0px;")
        self.filename_label.setMinimumSize(0, 0)
        self.label = ImageLabel(self)
        self.label.setMinimumSize(0, 0)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filename_label)
        layout.addWidget(self.label)
        container = QWidget()
        container.setLayout(layout)
        container.setMinimumSize(0, 0)
        self.setCentralWidget(container)
        self.setWindowTitle('ImageMan')
        self.tags = self._load_tags_from_registry()
        self.tag_counters = {tag: 1 for tag in self.tags}
        self.zoom_factor = 1.0
        self._init_menu()
        self._apply_dark_theme()
        # Set window size to fit the first image at natural size (plus label)
        self._initial_win_height = None
        self._initial_win_width = None
        if self.images:
            img_path = os.path.join(self.image_dir, self.images[0])
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                img_w, img_h = pixmap.width(), pixmap.height()
                label_h = 32  # space for filename label
                self._initial_win_width = img_w + 20
                self._initial_win_height = img_h + label_h + 20
                self.resize(self._initial_win_width, self._initial_win_height)
        else:
            self.resize(800, 600)
        # Allow the window to be made very small
        self.setMinimumSize(0, 0)
        self._show_image()
        self.show()
        # No auto-fit to contents; show at image's natural size

    def _load_tags_from_registry(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\ImageMan", 0, winreg.KEY_READ) as key:
                tags_str, _ = winreg.QueryValueEx(key, "tags")
                tags = tags_str.split(';')
                if len(tags) == 5:
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

    def _show_image(self):
        if not self.images:
            self.label.setText('No images found.')
            self.filename_label.setText('')
            return
        img_name = self.images[self.current_index]
        img_path = os.path.join(self.image_dir, img_name)
        self.filename_label.setText(img_name)
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            self.label.setText('Cannot load image.')
            return
        # Always scale by zoom_factor from natural size, but never larger than window area
        img_w, img_h = pixmap.width(), pixmap.height()
        scaled_w = int(img_w * self.zoom_factor)
        scaled_h = int(img_h * self.zoom_factor)
        # Fit to available area if too large for window
        available_w = max(1, self.centralWidget().width() - 20)
        available_h = max(1, self.centralWidget().height() - 52)  # 32 for label, 20 for margins
        if scaled_w > available_w or scaled_h > available_h:
            # Scale down to fit, but keep zoom_factor for next time
            ratio = min(available_w / scaled_w, available_h / scaled_h, 1.0)
            scaled_w = int(scaled_w * ratio)
            scaled_h = int(scaled_h * ratio)
        scaled_pixmap = pixmap.scaled(scaled_w, scaled_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)

    def _get_images(self):
        supported = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff')
        return [f for f in os.listdir(self.image_dir) if f.lower().endswith(supported)]

    def _delete_current_image(self):
        if not self.images:
            return
        img_path = os.path.join(self.image_dir, self.images[self.current_index])
        try:
            os.remove(img_path)
        except Exception as e:
            self.label.setText(f'Error deleting image: {e}')
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
        new_name = f"{tag}_{seq}{ext}"
        old_path = os.path.join(self.image_dir, old_name)
        new_path = os.path.join(self.image_dir, new_name)
        # Avoid overwriting existing files
        while os.path.exists(new_path):
            seq += 1
            new_name = f"{tag}_{seq}{ext}"
            new_path = os.path.join(self.image_dir, new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            self.label.setText(f'Error renaming image: {e}')
            return
        self.images[self.current_index] = new_name
        self.tag_counters[tag] = seq + 1
        self._show_image()

    # Public methods for testability
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
        # File menu
        file_menu = menubar.addMenu('File')
        open_dir_action = QAction('Open Directory...', self)
        open_dir_action.triggered.connect(self._select_directory)
        file_menu.addAction(open_dir_action)

        # Recent Directories submenu
        self.recent_dirs_menu = file_menu.addMenu('Recent Directories')
        self._update_recent_dirs_menu()

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)

        # Config menu
        config_menu = menubar.addMenu('Config')
        tag_action = QAction('Configure Tags', self)
        tag_action.triggered.connect(self._show_tag_dialog)
        config_menu.addAction(tag_action)

    def _select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Image Directory', self.image_dir)
        if dir_path:
            self.image_dir = dir_path
            self._add_to_recent_dirs(dir_path)
            self.images = self._get_images()
            self.current_index = 0
            self.zoom_factor = 1.0
            # Recompute initial window size for new directory
            self._initial_win_height = None
            self._initial_win_width = None
            if self.images:
                img_path = os.path.join(self.image_dir, self.images[0])
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    img_w, img_h = pixmap.width(), pixmap.height()
                    label_h = 32
                    self._initial_win_width = img_w + 20
                    self._initial_win_height = img_h + label_h + 20
                    self.resize(self._initial_win_width, self._initial_win_height)
            else:
                self.resize(800, 600)
            self._show_image()

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
            if len(set(new_tags)) != 5 or any(not t.strip() for t in new_tags):
                QMessageBox.warning(self, 'Invalid Tags', 'Tags must be 5 unique, non-empty values.')
                return
            self.tags = new_tags
            self.tag_counters = {tag: 1 for tag in self.tags}
            self._save_tags_to_registry()

class TagConfigDialog(QDialog):
    def resizeEvent(self, event):
        # Prevent accidental call to main window's resizeEvent logic
        pass
    def __init__(self, tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configure Tags')
        self.edits = []
        layout = QVBoxLayout()
        for tag in tags:
            edit = QLineEdit(tag)
            layout.addWidget(edit)
            self.edits.append(edit)
        btn = QPushButton('OK')
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)

    def get_tags(self):
        return [e.text().strip() for e in self.edits]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.prev_image()
        elif event.key() == Qt.Key_D:
            self.delete_current_image()
        elif event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]:
            idx = event.key() - Qt.Key_1
            self.rename_current_image(self.tags[idx])
        elif event.key() == Qt.Key_Q:
            self.zoom_in()
        elif event.key() == Qt.Key_A:
            self.zoom_out()

    def next_image(self):
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self._show_image()

    def prev_image(self):
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)
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
    def _rename_current_image(self, tag):
        if not self.images:
            return
        old_name = self.images[self.current_index]
        ext = os.path.splitext(old_name)[1]
        seq = self.tag_counters[tag]
        new_name = f"{tag}_{seq}{ext}"
        old_path = os.path.join(self.image_dir, old_name)
        new_path = os.path.join(self.image_dir, new_name)
        # Avoid overwriting existing files
        while os.path.exists(new_path):
            seq += 1
            new_name = f"{tag}_{seq}{ext}"
            new_path = os.path.join(self.image_dir, new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            self.label.setText(f'Error renaming image: {e}')
            return
        self.images[self.current_index] = new_name
        self.tag_counters[tag] = seq + 1
        self._show_image()

    def _delete_current_image(self):
        if not self.images:
            return
        img_path = os.path.join(self.image_dir, self.images[self.current_index])
        try:
            os.remove(img_path)
        except Exception as e:
            self.label.setText(f'Error deleting image: {e}')
            return
        del self.images[self.current_index]
        if self.current_index >= len(self.images):
            self.current_index = max(0, len(self.images) - 1)
        self._show_image()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    viewer = ImageMan(image_dir)
    sys.exit(app.exec_())
