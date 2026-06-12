"""后台任务线程：所有耗时操作（git、文件扫描）都在这里跑，通过信号回传结果。"""
from PyQt5.QtCore import QThread, pyqtSignal


class Worker(QThread):
    """通用后台线程：执行传入的函数，结果通过 finished_ok / failed 信号回传。"""
    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn, *args, parent=None, **kwargs):
        super().__init__(parent)
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished_ok.emit(result)
        except Exception as e:  # noqa: BLE001
            self.failed.emit(f"{type(e).__name__}: {e}")
