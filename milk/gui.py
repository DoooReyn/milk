import ctypes
from os.path import abspath, exists, isdir, isfile
from traceback import print_exc
from typing import List, Union

import win32api
import win32con
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QAction, QApplication, QButtonGroup, QCheckBox, QComboBox, QFileDialog, \
    QGridLayout, \
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenu, QMenuBar, QMessageBox, QProgressBar, \
    QPushButton, \
    QRadioButton, QTableWidget, QTableWidgetItem, QTextBrowser, QTextEdit, QTreeWidget, QVBoxLayout, QWidget
from win32gui import SystemParametersInfo

from milk.cmm import Cmm
from milk.conf import Lang, LangUI, ResMap, settings, signals, StyleSheet


class GUI:
    # region start - class

    class Preferences:
        layout_spacing = 8

        font_size = 11

        line_height = 36

        button_size = QSize(84, 36)

        view_size = QSize(640, 480)

        minimum_line_width = 400

        font_name = 'Microsoft YaHei'

    class GridItem:
        def __init__(self, widget: QWidget, start: int, col_span: int):
            self.widget = widget
            self.start = start
            self.col_span = col_span

    class View(QWidget):
        window_code: int = 0
        resize_keys: (str, str,) = None
        rect_key: str = None

        def closeEvent(self, event):
            if self.rect_key is not None:
                self.save_win_rect()
            if self.window_code > 0:
                signals.window_closed.emit(self.window_code)
            event.accept()
            super().closeEvent(event)

        def setup_window_code(self, code: int):
            self.window_code = code

        def setup_rect_key(self, kr: str):
            self.rect_key = kr
            tx, ty, w, h = self.get_win_rect()
            self.setGeometry(tx, ty, w, h)

        def get_win_rect(self):
            if self.rect_key is not None:
                return [int(v) for v in settings.value(self.rect_key, '640,640,640,480', str).split(',')]
            else:
                r = self.geometry()
                return r.topLeft().x(), r.topLeft().y(), r.width(), r.height()

        def save_win_rect(self):
            if self.rect_key is not None:
                r = self.geometry()
                rect = [r.topLeft().x(), r.topLeft().y(), r.width(), r.height()]
                rect = ','.join([str(r) for r in rect])
                settings.setValue(self.rect_key, rect)

    class MsgBox:
        @staticmethod
        def ask(msg_text: str, title: str = "Ask", detail: str = "", ico=QMessageBox.Information):
            return GUI.MsgBox.makeBox(msg_text, title, detail, ico, QMessageBox.Ok | QMessageBox.Cancel)

        @staticmethod
        def msg(msg_text: str, title: str = "Tips", detail: str = "", ico=QMessageBox.Information):
            return GUI.MsgBox.makeBox(msg_text, title, detail, ico)

        # noinspection PyBroadException
        @staticmethod
        def makeBox(msg_text: str, title: str = "", detail: str = "", ico=QMessageBox.Information,
                    style=QMessageBox.Ok):
            msg = QMessageBox()
            msg.setIcon(ico)
            msg.setText(msg_text)
            msg.setWindowTitle(title)
            msg.setDetailedText(detail)
            msg.setStandardButtons(style)
            return msg.exec_()

    # region end - class

    # region start - staticmethod

    @staticmethod
    def view_size():
        return GUI.Preferences.view_size

    @staticmethod
    def font():
        font = QFont()
        font.setPointSize(GUI.Preferences.font_size)
        font.setFamily(GUI.Preferences.font_name)
        return font

    @staticmethod
    def icon(path: str):
        return QIcon(path)

    @staticmethod
    def color(color: str):
        return QColor(color)

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
    def create_combo_box(items: Cmm.Iterable[str], default_index: int = 0):
        combo = QComboBox()

        combo.setEditable(False)
        line_edit = GUI.create_line_edit(readonly=True)
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
        line_edit = GUI.create_line_edit(readonly=True)
        line_edit.selectionChanged.connect(lambda: line_edit.deselect())
        line_edit.setAlignment(Qt.AlignCenter)
        combo.setLineEdit(line_edit)
        for i in range(combo.count()):
            combo.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

    @staticmethod
    def create_grid_layout(parent: QWidget):
        layout = QGridLayout()
        layout.setSpacing(GUI.Preferences.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def create_horizontal_layout(parent: QWidget):
        layout = QHBoxLayout()
        layout.setSpacing(GUI.Preferences.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def create_vertical_layout(parent: QWidget):
        layout = QVBoxLayout()
        layout.setSpacing(GUI.Preferences.layout_spacing)
        parent.setLayout(layout)
        return layout

    @staticmethod
    def create_label(text: str):
        lab = QLabel(text)
        lab.setFont(GUI.font())
        return lab

    @staticmethod
    def create_line_edit(text: str = '', readonly: bool = False, placeholder: str = ''):
        edit = QLineEdit(text)
        edit.setFont(GUI.font())
        edit.setReadOnly(readonly)
        edit.setCursorPosition(0)
        if len(placeholder) > 0:
            edit.setPlaceholderText(placeholder)
        return edit

    @staticmethod
    def set_folder_action_for_line_edit(edit: QLineEdit):
        icon = GUI.icon(ResMap.img_folder_open)
        pos = QLineEdit.TrailingPosition
        edit.addAction(icon, pos)
        return edit.actions()[-1]

    @staticmethod
    def create_progress_bar():
        bar = QProgressBar()
        bar.setFont(GUI.font())
        return bar

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
    def create_check_box(text: str):
        box = QCheckBox(text)
        box.setFont(GUI.font())
        return box

    @staticmethod
    def create_group_box(title: str = ''):
        box = QGroupBox(title)
        return box

    @staticmethod
    def create_list_item(parent: QListWidget, text: str, icon: str = None):
        if icon is not None:
            item = QListWidgetItem(GUI.icon(icon), text, parent)
        else:
            item = QListWidgetItem(text, parent)
        item.setFont(GUI.font())
        return item

    @staticmethod
    def create_table_widget(headers: List[str]):
        table = QTableWidget()
        table.setFont(GUI.font())
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        header_font = GUI.font()
        header_font.setBold(True)
        table.horizontalHeader().setSectionsClickable(False)
        table.horizontalHeader().setFont(header_font)
        table.verticalHeader().setFont(header_font)
        return table

    @staticmethod
    def create_table_item(text: str, icon: str = None, tag: int = 0):
        if icon is not None:
            item = QTableWidgetItem(GUI.icon(icon), text, tag)
        else:
            item = QTableWidgetItem(text, tag)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(GUI.font())
        return item

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
        child.setFixedSize(GUI.Preferences.button_size)
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
    def set_text_browser_selectable(tb: QTextBrowser, ok: bool):
        tb.setTextInteractionFlags(Qt.TextBrowserInteraction if ok else Qt.NoTextInteraction)

    @staticmethod
    def add_grid_in_row(layout: QGridLayout, row: int, items: Cmm.Iterable[GridItem]):
        for item in items:
            layout.addWidget(item.widget, row, item.start, 1, item.col_span)

    @staticmethod
    def add_grid_in_rows(layout: QGridLayout, rows: Cmm.Iterable[Cmm.Iterable[GridItem]]):
        for row, items in enumerate(rows):
            GUI.add_grid_in_row(layout, row, items)

    @staticmethod
    def set_grid_span(layout: QGridLayout, rows: Cmm.Iterable[int], cols: Cmm.Iterable[int]):
        for row in rows:
            layout.setRowStretch(row, 1)
        for col in cols:
            layout.setColumnStretch(col, 1)

    @staticmethod
    def application():
        return QApplication.instance()

    @staticmethod
    def clipboard():
        return QApplication.clipboard()

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

    # noinspection PyBroadException
    @staticmethod
    def get_screensize(multiplier=1):
        try:
            user32 = ctypes.windll.user32
            screensize = (user32.GetSystemMetrics(78) * multiplier, user32.GetSystemMetrics(79) * multiplier)
            print(f"\r[+] Status: Detected virtual monitor size {screensize[0]}x{screensize[1]}.", end="")
            if multiplier > 1:
                print(f"\r[+] Status: Multiplying to {screensize} for better quality.", end="")
            return screensize
        except:
            print(f"\r[-] Status: Encountered some problems while detecting your display size.", end="")
            print_exc()

    # noinspection PyBroadException
    @staticmethod
    def set_wallpaper(path):
        def on_start():
            key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
            win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
            win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
            SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, abspath(path), win32con.SPIF_SENDWININICHANGE)
            win32api.RegCloseKey(key)

        Cmm.trace(on_start)

    @staticmethod
    def create_list_widget():
        return QListWidget()

    @staticmethod
    def create_tree_widget():
        return QTreeWidget()

    @staticmethod
    def hv_layout_widgets(layout: Union[QHBoxLayout, QVBoxLayout], widgets: Cmm.Iterable[QWidget]):
        [layout.addWidget(w) for w in widgets]

    # region end - staticmethod
