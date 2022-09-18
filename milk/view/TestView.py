from PyQt5.QtWidgets import QWidget

from milk.view.ui_base import UIBase


class TestView(UIBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
