import sys
from traceback import format_exception

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from milk.cmm import Cmm
from milk.conf import ResMap, Settings, signals
from milk.view.window import Window


class App(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.old_hook = sys.excepthook
        sys.excepthook = self.catch_error

        Cmm.create_app_cache_dir()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(Settings.Names.app)
        self.app.setApplicationDisplayName(Settings.Names.app)
        self.app.setWindowIcon(QIcon(ResMap.img_app_icon))
        self.app.setFont(QFont(Settings.UI.DefaultFontName, Settings.UI.DefaultFontSize))
        self.window = Window()

    def catch_error(self, error_type, error_target, error_stack):
        traceback_format = format_exception(error_type, error_target, error_stack)
        traceback_msg = "".join(traceback_format)
        signals.logger_error.emit(traceback_msg)
        self.old_hook(error_type, error_target, error_stack)

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())
