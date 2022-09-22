from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMenu, QMenuBar, QShortcut, QWidget

from milk.conf import UIDef


class WeRead(QWebEngineView):
    def __init__(self, parent: QWidget = None):
        super(WeRead, self).__init__(parent)

        self.setup_window_code(UIDef.ToolsWeRead.value)

        self.setWindowTitle("微读自动阅读器")
        self.load(QUrl('https://weread.qq.com/'))
        self.showNormal()

        self.fullscreen_shortcut = QShortcut(QKeySequence('F11'), self)
        self.fullscreen_shortcut.activated.connect(self.on_full_screen_changed)

        menu_bar = QMenuBar(self)
        menu_bar.setFixedHeight(28)
        menu_bar.setMinimumWidth(self.minimumWidth())
        menu_bar.setMaximumWidth(self.maximumWidth())

        menu_setting = QMenu('Settings', menu_bar)
        menu_about = QMenu('About', menu_bar)
        menu_bar.addMenu(menu_setting)
        menu_bar.addMenu(menu_about)

    def on_full_screen_changed(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def auto_scroll_down(self):
        # self.isEnabled()
        pass
