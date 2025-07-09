from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import Qt


class TagConfigDialog(QDialog):
    def __init__(self, tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configure Tags')
        self.edits = []
        layout = QVBoxLayout()
        for tag in tags:
            edit = QLineEdit(tag)
            layout.addWidget(edit)
            self.edits.append(edit)
        self.slideshow_duration_edit = QLineEdit(str(parent.slideshow_duration))
        layout.addWidget(QLabel("Slideshow Duration (seconds):"))
        layout.addWidget(self.slideshow_duration_edit)

        btn = QPushButton('OK')
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)

    def get_tags(self):
        return [e.text().strip() for e in self.edits]

    def get_slideshow_duration(self):
        try:
            duration = float(self.slideshow_duration_edit.text())
            if duration <= 0:
                raise ValueError("Duration must be positive.")
            return duration
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Slideshow duration must be a positive number.')
            return None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
