from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QMenuBar, QWidget, QComboBox, QLineEdit

from conf.lang import Lang, LangUI
from conf import signals


class GUI:
    @staticmethod
    def create_menu_bar(menus, parent: QWidget):
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
                    if getattr(parent, trigger, None) is not None:
                        act.triggered.connect(getattr(parent, trigger))
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
    def init_combo_box(combo: QComboBox):
        combo.setEditable(False)
        line_edit = QLineEdit()
        line_edit.selectionChanged.connect(lambda: line_edit.deselect())
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setReadOnly(True)
        combo.setLineEdit(line_edit)
        for i in range(combo.count()):
            combo.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
