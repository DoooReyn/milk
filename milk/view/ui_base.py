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

    @property
    def default_font(self):
        font = QFont()
        font.setPointSize(10)
        return font

    @property
    def default_height(self):
        return 36

    @property
    def default_layout_spacing(self):
        return 8

    @property
    def default_button_size(self):
        return QSize(84, 36)

    @property
    def default_minimum_width(self):
        return 400

    # noinspection PyMethodMayBeStatic
    def add_widget(self, parent: QWidget):
        child = QWidget()
        parent.layout().addWidget(child)
        return child

    def add_child(self, child: QWidget):
        self.layout().addWidget(child)
        return child

    def add_grid_layout(self, parent: QWidget):
        layout = QGridLayout()
        layout.setSpacing(self.default_layout_spacing)
        parent.setLayout(layout)
        return layout

    def add_horizontal_layout(self, parent: QWidget):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setSpacing(self.default_layout_spacing)
        parent.setLayout(layout)
        return layout

    def add_vertical_layout(self, parent: QWidget):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setSpacing(self.default_layout_spacing)
        parent.setLayout(layout)
        return layout

    def add_label(self, text: str, parent: QWidget):
        child = QLabel(text)
        child.setAlignment(Qt.AlignCenter)
        child.setFixedHeight(self.default_height)
        parent.layout().addWidget(child)
        return child

    def add_line_edit(self, placeholder: str, parent: QWidget):
        child = QLineEdit()
        child.setMinimumWidth(self.default_minimum_width)
        child.setFont(self.default_font)
        child.setFixedHeight(self.default_height)
        child.setPlaceholderText(placeholder)
        parent.layout().addWidget(child)
        return child

    def add_push_button(self, text, parent: QWidget):
        child = QPushButton(text)
        child.setFixedSize(self.default_button_size)
        parent.layout().addWidget(child)
        return child

    def add_check_button(self, text: str, parent: QWidget, checked: bool = True):
        child = QPushButton(text)
        child.setFixedSize(self.default_button_size)
        child.setCheckable(True)
        child.setChecked(checked)
        parent.layout().addWidget(child)
        return child

    def add_text_browser(self, parent: QWidget):
        child = QTextBrowser()
        child.setFont(self.default_font)
        child.setReadOnly(True)
        child.setAcceptRichText(True)
        child.setMinimumHeight(self.default_minimum_width)
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
