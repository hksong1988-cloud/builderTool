"""界面主题：基于 PyQtDarkTheme，支持 dark/light 切换，带回退。"""

THEMES = ("dark", "light")


def apply_theme(app, theme: str = "dark") -> bool:
    """应用 PyQtDarkTheme 主题。成功返回 True，失败回退 Fusion 并返回 False。"""
    if theme not in THEMES:
        theme = "dark"
    try:
        import qdarktheme
        app.setStyleSheet(qdarktheme.load_stylesheet(theme))
        return True
    except Exception:
        try:
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))
            return True
        except Exception:
            app.setStyleSheet("")
            app.setStyle("Fusion")
            return False
