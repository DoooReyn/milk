from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QTextBrowser, \
    QVBoxLayout, QWidget

from milk.conf import signals
from milk.gui import GUI


class UIBase(QWidget):
    window_code: int = 0

    def __init__(self, parent: QWidget = None):
        super(UIBase, self).__init__(parent)
        self.setup_ui()
        self.setup_signals()

    def closeEvent(self, event):
        if self.window_code > 0:
            signals.window_closed.emit(self.window_code)
        event.accept()
        super().closeEvent(event)

    def setup_window_code(self, code: int):
        self.window_code = code

    def setup_ui(self):
        pass

    def setup_signals(self):
        pass

    # noinspection PyMethodMayBeStatic
    def add_widget(self, parent: QWidget):
        child = QWidget()
        parent.layout().addWidget(child)
        return child

    def add_child(self, child: QWidget):
        self.layout().addWidget(child)
        return child

    @staticmethod
    def add_grid_layout(parent: QWidget):
        layout = QGridLayout()
        layout.setSpacing(GUI.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def add_horizontal_layout(parent: QWidget):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setSpacing(GUI.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def add_vertical_layout(parent: QWidget):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setSpacing(GUI.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def add_label(text: str, parent: QWidget):
        child = QLabel(text)
        child.setAlignment(Qt.AlignCenter)
        parent.layout().addWidget(child)
        return child

    @staticmethod
    def add_line_edit(placeholder: str, parent: QWidget):
        child = QLineEdit()
        child.setMinimumWidth(GUI.minimum_line_width)
        child.setFont(GUI.font())
        child.setPlaceholderText(placeholder)
        parent.layout().addWidget(child)
        return child

    @staticmethod
    def add_push_button(text, parent: QWidget):
        child = QPushButton(text)
        child.setFixedSize(GUI.button_size)
        parent.layout().addWidget(child)
        return child

    @staticmethod
    def add_check_button(text: str, parent: QWidget, checked: bool = True):
        child = QPushButton(text)
        child.setFixedSize(GUI.button_size)
        child.setCheckable(True)
        child.setChecked(checked)
        parent.layout().addWidget(child)
        return child

    @staticmethod
    def add_text_browser(parent: QWidget):
        child = QTextBrowser()
        child.setFont(GUI.font())
        child.setReadOnly(True)
        child.setAcceptRichText(True)
        child.setMinimumHeight(GUI.minimum_line_width)
        parent.layout().addWidget(child)
        return child

    # noinspection PyMethodMayBeStatic
    def add_progress_bar(self, parent: QWidget):
        child = QProgressBar()
        parent.layout().addWidget(child)
        return child

    def add_menu_bar(self, menus):
        menu_bar = GUI.create_menu_bar(menus, self)
        self.layout().setMenuBar(menu_bar)
        return menu_bar
