from os.path import exists, isdir, isfile

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QButtonGroup, QComboBox, QFileDialog, QGridLayout, QGroupBox, \
    QHBoxLayout, QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QRadioButton, QTextBrowser, QTextEdit, QVBoxLayout, \
    QWidget

from milk.cmm import Cmm
from milk.conf import Lang, LangUI, signals, StyleSheet

try:
    from collections import Iterable
except (AttributeError, ImportError):
    from collections.abc import Iterable


class GUI:
    # region start - class

    class GridItem:
        def __init__(self, widget: QWidget, start: int, col_span: int):
            self.widget = widget
            self.start = start
            self.col_span = col_span

    # region end - class

    # region start - property

    layout_spacing = 8

    font_size = 11

    line_height = 36

    button_size = QSize(84, 36)

    minimum_line_width = 400

    font_name = 'Microsoft YaHei'

    # region end - property

    # region start - staticmethod

    @staticmethod
    def font():
        font = QFont()
        font.setPointSize(GUI.font_size)
        font.setFamily(GUI.font_name)
        return font

    @staticmethod
    def icon(path: str):
        return QIcon(path)

    @staticmethod
    def create_menu_bar(menus, parent: QWidget, target=None):
        target = target if target is not None else parent
        menu_bar = QMenuBar(parent)
        for menu_class in menus.all:
            menu_name = Lang.get(menu_class.Name) or menu_class.Name
            menu = QMenu(menu_name, parent)
            for action in menu_class.Actions:
                name = action.get("name")
                name = Lang.get(name) or name
                hotkey = action.get("hotkey")
                icon = action.get("icon")
                trigger = action.get("trigger")
                act = QAction(name, menu)
                if trigger is not None:
                    if hasattr(target, trigger):
                        act.triggered.connect(lambda *args, t=target, g=trigger: getattr(t, g)())
                    else:
                        act.triggered.connect(lambda *args, m=menu_name, n=name: GUI.on_bind_not_implemented(m, n))
                else:
                    act.triggered.connect(lambda *args, m=menu_name, n=name: GUI.on_bind_not_implemented(m, n))
                if hotkey is not None:
                    act.setShortcut(hotkey)
                if icon is not None:
                    act.setIcon(QIcon(icon))
                menu.addAction(act)
            menu_bar.addMenu(menu)
        return menu_bar

    @staticmethod
    def on_bind_not_implemented(menu, name):
        signals.logger_warn.emit(LangUI.msg_not_implemented.format(menu, name))

    @staticmethod
    def create_combo_box(items: tuple[str], default_index: int = 0):
        combo = QComboBox()

        combo.setEditable(False)
        line_edit = GUI.create_line_edit('', True)
        line_edit.selectionChanged.connect(lambda: line_edit.deselect())
        line_edit.setAlignment(Qt.AlignCenter)
        combo.setLineEdit(line_edit)
        combo.setMinimumWidth(120)

        combo.addItems(items)
        for i, _ in enumerate(items):
            combo.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

        combo.setCurrentIndex(default_index)

        return combo

    @staticmethod
    def init_combo_box(combo: QComboBox):
        combo.setEditable(False)
        line_edit = GUI.create_line_edit('', True)
        line_edit.selectionChanged.connect(lambda: line_edit.deselect())
        line_edit.setAlignment(Qt.AlignCenter)
        combo.setLineEdit(line_edit)
        for i in range(combo.count()):
            combo.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

    @staticmethod
    def create_grid_layout(parent: QWidget):
        layout = QGridLayout()
        layout.setSpacing(GUI.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def create_horizontal_layout(parent: QWidget):
        layout = QHBoxLayout()
        layout.setSpacing(GUI.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def create_vertical_layout(parent: QWidget):
        layout = QVBoxLayout()
        layout.setSpacing(GUI.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def create_label(text: str):
        lab = QLabel(text)
        lab.setFont(GUI.font())
        return lab

    @staticmethod
    def create_line_edit(text: str, readonly: bool = False):
        edit = QLineEdit(text)
        edit.setFont(GUI.font())
        edit.setReadOnly(readonly)
        edit.setCursorPosition(0)
        return edit

    @staticmethod
    def create_icon_btn(path: str, checkable: bool = False):
        ico = QPushButton(QIcon(path), '')
        ico.setCheckable(checkable)
        ico.setStyleSheet('QPushButton { border: none; }')
        return ico

    @staticmethod
    def create_radio_btn(text: str):
        radio = QRadioButton(text)
        radio.setFont(GUI.font())
        return radio

    @staticmethod
    def create_radio_group(title: str, items: tuple[str], ids: tuple[int], default_id: int):
        box = QGroupBox()

        group = QButtonGroup(box)
        group.setExclusive(True)

        layout = GUI.create_horizontal_layout(box)
        layout.addWidget(GUI.create_label(title))
        for i, item in enumerate(items):
            rid = ids[i]
            btn = GUI.create_radio_btn(item)
            layout.addWidget(btn)
            group.addButton(btn, rid)

        default_btn = group.button(default_id)
        if default_btn is not None:
            default_btn.setChecked(True)

        return box, group

    @staticmethod
    def create_text_edit(placeholder: str, accept_rich: bool = True, font_size: int = 10):
        edit = QTextEdit()
        edit.setFont(GUI.font())
        edit.setFontPointSize(font_size)
        edit.setAcceptRichText(accept_rich)
        edit.setPlaceholderText(placeholder)
        return edit

    @staticmethod
    def create_push_btn(text: str):
        btn = QPushButton(text)
        btn.setFont(GUI.font())
        return btn

    @staticmethod
    def create_check_button(text: str, checked: bool = True):
        child = GUI.create_push_btn(text)
        child.setFixedSize(GUI.button_size)
        child.setCheckable(True)
        child.setChecked(checked)
        child.setStyleSheet(StyleSheet.CheckButton)
        return child

    @staticmethod
    def create_text_browser(markdown: str = ''):
        browser = QTextBrowser()
        browser.setReadOnly(True)
        browser.setAcceptRichText(True)
        browser.setOpenExternalLinks(True)
        browser.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        browser.setMarkdown(markdown)
        return browser

    @staticmethod
    def add_grid_in_row(layout: QGridLayout, row: int, items: Iterable[GridItem]):
        for item in items:
            layout.addWidget(item.widget, row, item.start, 1, item.col_span)

    @staticmethod
    def add_grid_in_rows(layout: QGridLayout, rows: Iterable[(int, Iterable[GridItem])]):
        for row, items in rows:
            GUI.add_grid_in_row(layout, row, items)

    @staticmethod
    def set_grid_span(layout: QGridLayout, rows: Iterable[int], cols: Iterable[int]):
        for row in rows:
            layout.setRowStretch(row, 1)
        for col in cols:
            layout.setColumnStretch(col, 1)

    @staticmethod
    def application():
        return QApplication.instance()

    @staticmethod
    def dialog_for_file_selection(parent: QWidget, title: str, start: str, file_filter: str = 'Any Files(*.*)'):
        start = start if len(start) > 0 else Cmm.user_document_dir()
        chosen = QFileDialog.getOpenFileName(parent, title, start, file_filter)
        if isinstance(chosen, tuple):
            chosen = chosen[0]
            if exists(chosen) and isfile(chosen):
                return chosen
        return None

    @staticmethod
    def dialog_for_directory_selection(parent: QWidget, title: str, start: str):
        start = start if len(start) > 0 else Cmm.user_document_dir()
        chosen = QFileDialog.getExistingDirectory(parent, title, start)
        if exists(chosen) and isdir(chosen):
            return chosen
        return None

    # region end - staticmethod
