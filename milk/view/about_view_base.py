from PyQt5.QtWidgets import QWidget, QDialog

from milk.gui import GUI
from milk.view.ui_base import UIBase


class AboutBaseView(QDialog):
    def __init__(self, parent: QWidget = None, text: str = ''):
        super(AboutBaseView, self).__init__(parent)

        # create widgets
        self.ui_text_browser = GUI.create_text_browser(text)

        # layout
        self.ui_layout = GUI.create_vertical_layout(self)
        self.ui_layout.addWidget(self.ui_text_browser)
