from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QMenu, QTreeWidgetItem

from milk.cmm import Cmm
from milk.conf import LangUI, settings, signals, StyleSheet, UIDef, UserKey
from milk.gui import GUI
from .lua_source_interpreter import LuaSourceExtractor


class _View(GUI.View):
    def __init__(self):
        super(_View, self).__init__()

        self.ui_edit_file = GUI.create_line_edit(readonly=True, placeholder=LangUI.lua_extractor_file_at)
        self.ui_act_file = GUI.set_folder_action_for_line_edit(self.ui_edit_file)
        self.ui_btn_extract = GUI.create_push_btn(LangUI.lua_extractor_start)
        self.ui_group_options = GUI.create_group_box(LangUI.lua_extractor_options)
        self.ui_layout_group_options = GUI.create_horizontal_layout(self.ui_group_options)
        self.ui_layout_group_options.setAlignment(Qt.AlignLeft)
        self.ui_btn_check_comment = GUI.create_check_button(LangUI.lua_extractor_ele_comment)
        self.ui_btn_check_string = GUI.create_check_button(LangUI.lua_extractor_ele_string)
        self.ui_btn_check_function = GUI.create_check_button(LangUI.lua_extractor_ele_function)
        GUI.hv_layout_widgets(self.ui_layout_group_options, (
            self.ui_btn_check_comment,
            self.ui_btn_check_string,
            self.ui_btn_check_function
        ))

        self.ui_tree_result = GUI.create_tree_widget()
        self.ui_tree_result.setFont(GUI.font())
        self.ui_tree_result.setColumnCount(3)
        self.ui_tree_result.setUniformRowHeights(True)
        self.ui_tree_result.setStyleSheet(StyleSheet.TreeView)
        self.ui_tree_result.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_tree_result.setHeaderLabels(['Name', 'Line', 'Content'])
        self.ui_tree_result.header().setFont(GUI.font())
        self.ui_tree_result.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui_tree_result.header().setStyleSheet(StyleSheet.HeaderView)
        self.ui_tree_result.clear()

        self.ui_layout = GUI.create_grid_layout(self)
        GUI.add_grid_in_rows(self.ui_layout, (
            (
                GUI.GridItem(self.ui_edit_file, 0, 2),
                GUI.GridItem(self.ui_btn_extract, 2, 1),
            ),
            (
                GUI.GridItem(self.ui_group_options, 0, 3),
            ),
            (
                GUI.GridItem(self.ui_tree_result, 0, 3),
            ),
        ))
        GUI.set_grid_span(self.ui_layout, [2], [0])


class ElementExtractorView(_View):
    def __init__(self):
        super(ElementExtractorView, self).__init__()

        self._level = -1
        self._data = None

        self.setWindowTitle(LangUI.lua_extractor_title)
        self.setMinimumSize(640, 480)

        self.setup_rect_key(UserKey.LuaExtractor.window_rect)
        self.setup_window_code(UIDef.LuaExtractor.value)
        self.setup_preferences()
        self.setup_ui_signals()

    def setup_preferences(self):
        self.ui_edit_file.setText(self.file_at())

    def setup_ui_signals(self):
        self.ui_btn_extract.clicked.connect(self.on_start_extract)
        self.ui_act_file.triggered.connect(self.on_select_file)
        self.ui_tree_result.customContextMenuRequested.connect(self.right_click_menu)

    @staticmethod
    def get_tree_item_level(item: QTreeWidgetItem):
        level = 0
        while True:
            if item.parent() is None:
                break
            item = item.parent()
            level += 1
        return level

    def right_click_menu(self, pos):
        current = self.ui_tree_result.currentItem()

        if current is None:
            return

        level = self.get_tree_item_level(current)

        if level == 0 or level == 1:
            if current.childCount() == 0:
                return

        self._level = level

        try:
            menu = QMenu()
            act_copy = menu.addAction(LangUI.lua_extractor_copy)
            act_copy.triggered.connect(self.on_copy_item)
            menu.exec_(self.ui_tree_result.mapToGlobal(pos))
        except Exception as e:
            signals.logger_error.emit(str(e))

    def on_copy_item(self):
        current = self.ui_tree_result.currentItem()
        print(current.text(0), current.text(1), current.text(2))
        if self._level == 0:
            lines = []
            for key, items in self._data.items():
                for _, _, text in items:
                    lines.append(text)
            GUI.clipboard().setText('\n'.join(lines))
        elif self._level == 1:
            data = self._data.get(current.text(0))
            text = '\n'.join([text for _, _, text in data])
            GUI.clipboard().setText(text)
        elif self._level == 2:
            GUI.clipboard().setText(current.text(2))

    @staticmethod
    def file_at(at: str = None):
        if at is not None:
            settings.setValue(UserKey.LuaExtractor.file_at, at)
        else:
            return settings.value(UserKey.LuaExtractor.file_at, Cmm.user_document_dir(), str)

    def on_select_file(self):
        chosen = GUI.dialog_for_file_selection(self, LangUI.lua_extractor_file_at, self.file_at())
        if chosen is not None:
            self.ui_edit_file.setText(chosen)
            self.file_at(chosen)
            self.on_start_extract()

    def on_start_extract(self):
        self.ui_tree_result.clear()
        self.set_widgets_enabled(False)
        Cmm.trace(on_start=lambda: self.start_extract(self.file_at()),
                  on_error=lambda err: signals.logger_error.emit(err),
                  on_final=lambda: self.set_widgets_enabled(True))

    def set_widgets_enabled(self, ok: bool):
        self.ui_edit_file.setEnabled(ok)
        self.ui_btn_extract.setEnabled(ok)
        self.ui_group_options.setEnabled(ok)
        self.ui_tree_result.setEnabled(ok)

    def start_extract(self, file: str):
        data = LuaSourceExtractor(file).parse()
        root = QTreeWidgetItem(self.ui_tree_result)
        root.setText(0, LangUI.lua_extractor_options)
        self._data = data

        colors = {
            'string': Qt.green,
            'comment': Qt.gray,
            'function': GUI.color('#90dbff')
        }

        def add_items(key: str):
            data_list = data.get(key)

            if len(data_list) == 0:
                return

            child = QTreeWidgetItem(root)
            child.setBackground(0, colors.get(key))
            child.setText(0, key)
            child.setText(1, '')
            child.setText(2, '')
            child.setFont(0, GUI.font())
            child.setFont(1, GUI.font())
            child.setFont(2, GUI.font())
            child.setTextAlignment(0, Qt.AlignCenter)
            child.setTextAlignment(1, Qt.AlignCenter)
            child.setTextAlignment(2, Qt.AlignLeft)

            for name, line, content in data_list:
                item = QTreeWidgetItem(child)
                item.setBackground(1, GUI.color('#f0f0f5'))
                item.setFont(0, GUI.font())
                item.setFont(1, GUI.font())
                item.setFont(2, GUI.font())
                item.setText(0, '')
                item.setText(1, line)
                item.setText(2, content)
                item.setTextAlignment(0, Qt.AlignCenter)
                item.setTextAlignment(1, Qt.AlignCenter)
                item.setTextAlignment(2, Qt.AlignLeft)

        if self.ui_btn_check_comment.isChecked():
            add_items('comment')

        if self.ui_btn_check_function.isChecked():
            add_items('function')

        if self.ui_btn_check_string.isChecked():
            add_items('string')

        self.ui_tree_result.addTopLevelItem(root)
        self.ui_tree_result.expandAll()
        self.set_widgets_enabled(True)
