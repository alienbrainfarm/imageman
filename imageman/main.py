import sys
import os
import winreg
from PyQt5.QtWidgets import QApplication
from imageman.image_man_window import ImageMan


if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_dir = None
    if len(sys.argv) > 1:
        image_dir = sys.argv[1]
    else:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\ImageMan", 0, winreg.KEY_READ) as key:
                dirs_str, _ = winreg.QueryValueEx(key, "recent_dirs")
                if dirs_str:
                    image_dir = dirs_str.split(';')[0]
        except Exception:
            pass

    if not image_dir or not os.path.isdir(image_dir):
        image_dir = '.'

    viewer = ImageMan(image_dir)
    sys.exit(app.exec_())