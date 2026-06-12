"""入口：python main.py"""
import sys

from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow
from app.theme import apply_theme


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    # 应用启动主题（默认深色，记忆上次选择）
    theme = win.cfg.get("theme", "dark")
    apply_theme(app, theme)
    win.current_theme = theme
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
