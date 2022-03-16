import sys

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication

from milk.cmm import Cmm
from milk.conf import Settings, ResMap
from .window import Window


class App(object):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        Cmm.create_app_cache_dir()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(Settings.Names.app)
        self.app.setApplicationDisplayName(Settings.Names.app)
        self.app.setWindowIcon(QIcon(ResMap.img_app_icon))
        self.app.setFont(QFont(Settings.UI.DefaultFontName, Settings.UI.DefaultFontSize))
        self.window = Window()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())
