from PyQt5.QtWidgets import QLabel, QListWidget
from PyQt5.QtCore import Qt

from imageman.constants import NUM_TAGS


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

        key_actions = {
            Qt.Key_Right: parent.next_image,
            Qt.Key_Left: parent.prev_image,
            Qt.Key_D: parent.delete_current_image,
            Qt.Key_W: parent.zoom_in,
            Qt.Key_Up: parent.zoom_in,
            Qt.Key_Q: parent.zoom_out,
            Qt.Key_A: parent.zoom_out,
            Qt.Key_Down: parent.zoom_out,
            Qt.Key_Escape: parent.close,
            Qt.Key_Space: parent.toggle_slideshow,
            Qt.Key_T: parent.toggle_thumbnail_view_and_refresh,
            Qt.Key_N: parent.toggle_filename_display,
        }

        if event.key() in key_actions:
            key_actions[event.key()]()
        elif Qt.Key_1 <= event.key() <= (Qt.Key_1 + NUM_TAGS - 1):
            idx = event.key() - Qt.Key_1
            parent.move_current_image_to_tag(idx)
        else:
            super().keyPressEvent(event)


class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(self.InternalMove)
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        self.setMovement(self.Snap)

    def dropEvent(self, event):
        super().dropEvent(event)
        # Use self.window() to get the top-level ImageMan window
        if hasattr(self.window(), 'on_item_dropped'):
            self.window().on_item_dropped()

    def keyPressEvent(self, event):
        # Use self.window() to get the top-level ImageMan window
        parent_window = self.window()
        selected_items = self.selectedItems()
        if not parent_window or not selected_items:
            super().keyPressEvent(event)
            return

        selected_item = selected_items[0]
        selected_image_name = selected_item.data(Qt.UserRole)

        if event.key() == Qt.Key_D:
            parent_window.delete_thumbnail_image(selected_image_name)
        elif Qt.Key_1 <= event.key() <= (Qt.Key_1 + NUM_TAGS - 1):
            idx = event.key() - Qt.Key_1
            parent_window.move_thumbnail_image_to_tag(selected_image_name, idx)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            parent_window.open_thumbnail_in_single_view(selected_image_name)
        elif event.key() == Qt.Key_T:
            parent_window.toggle_thumbnail_view_and_refresh()
        elif event.key() == Qt.Key_N:
            parent_window.toggle_filename_display()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            selected_image_name = item.data(Qt.UserRole)
            
            # Use self.window() to get the top-level ImageMan window
            parent_window = self.window()
            
            parent_window.open_thumbnail_in_single_view(selected_image_name)
        super().mouseDoubleClickEvent(event)