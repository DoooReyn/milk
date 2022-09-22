from os import walk
from os.path import exists, isdir, isfile, join, normpath, relpath, splitext
from time import sleep
from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QSplitter, QTableWidgetItem

from milk.cmm import Cmm
from milk.conf import LangUI, ResMap, settings, StyleSheet, UIDef, UserKey
from milk.gui import GUI
from .lua_syntax_checker import LuaSyntaxChecker


class _View(GUI.View):
    def __init__(self):
        super(_View, self).__init__()

        # create widgets
        self.ui_label_select = GUI.create_label(LangUI.lua_grammar_folder_at)
        self.ui_edit_select = GUI.create_line_edit(readonly=True, placeholder=LangUI.lua_grammar_folder_at)
        self.ui_act_select = GUI.set_folder_action_for_line_edit(self.ui_edit_select)
        self.ui_btn_check = GUI.create_push_btn(LangUI.lua_grammar_check_start)
        self.ui_group_files = GUI.create_group_box(LangUI.lua_grammar_check_result)
        self.ui_group_files_layout = GUI.create_horizontal_layout(self.ui_group_files)
        self.ui_table_files = GUI.create_table_widget([LangUI.lua_grammar_lua_filename, LangUI.lua_grammar_max_nested])
        self.ui_table_files.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui_table_files.horizontalHeader().setStyleSheet(StyleSheet.HeaderView)
        self.ui_table_files.setMinimumWidth(300)
        # self.ui_table_files.setSelectionBehavior(QAbstractItemView.SelectionBehavior.)
        self.ui_table_files.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui_tb_nested = GUI.create_text_browser()
        self.ui_tb_nested.setMinimumWidth(300)
        self.ui_tb_nested.hide()
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setLineWidth(4)
        splitter.addWidget(self.ui_table_files)
        splitter.addWidget(self.ui_tb_nested)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)
        splitter.setSizes([100, 500])
        splitter.setChildrenCollapsible(False)
        self.ui_group_files_layout.addWidget(splitter)

        # layout widgets
        self.ui_layout = GUI.create_grid_layout(self)
        GUI.add_grid_in_rows(self.ui_layout, (
            (
                GUI.GridItem(self.ui_label_select, 0, 1),
                GUI.GridItem(self.ui_edit_select, 1, 2),
                GUI.GridItem(self.ui_btn_check, 3, 1)
            ),
            (
                GUI.GridItem(self.ui_group_files, 0, 4),
            ),
        ))
        GUI.set_grid_span(self.ui_layout, [1], [2])


class SyntaxInspectionView(_View):
    def __init__(self):
        super(SyntaxInspectionView, self).__init__()

        self.row_info = []
        self.thread: Optional[Cmm.StoppableThread] = None
        self.setup_window_code(UIDef.LuaGrammarChecker.value)
        self.setWindowTitle(LangUI.lua_grammar_title)
        self.setMinimumSize(640, 640)
        self.setup_preferences()
        self.setup_ui_signals()

    def setup_preferences(self):
        w, h = self.win_size()
        self.resize(w, h)
        self.ui_edit_select.setText(self.lua_grammar_folder_at())

    def setup_ui_signals(self):
        self.ui_btn_check.clicked.connect(self.on_start_check)
        self.ui_edit_select.returnPressed.connect(self.on_start_check)
        self.ui_act_select.triggered.connect(self.on_select_folder)
        self.ui_table_files.clicked.connect(self.on_item_double_clicked)

    @staticmethod
    def win_size(width: int = None, height: int = None):
        if width is not None and height is not None:
            settings.setValue(UserKey.LuaGrammar.window_width, width)
            settings.setValue(UserKey.LuaGrammar.window_height, height)
        else:
            w = settings.value(UserKey.LuaGrammar.window_width, 640, int)
            h = settings.value(UserKey.LuaGrammar.window_height, 640, int)
            return w, h

    @staticmethod
    def lua_grammar_folder_at(at: str = None):
        if at is not None:
            settings.setValue(UserKey.LuaGrammar.folder_at, at)
        else:
            return settings.value(UserKey.LuaGrammar.folder_at, Cmm.user_document_dir(), str)

    def resizeEvent(self, event) -> None:
        self.win_size(self.width(), self.height())
        event.accept()
        super(SyntaxInspectionView, self).resizeEvent(event)

    def closeEvent(self, event):
        if self.thread is not None:
            self.thread.stop()
        super(SyntaxInspectionView, self).closeEvent(event)

    def on_select_folder(self):
        chosen = GUI.dialog_for_directory_selection(self, LangUI.lua_grammar_folder_at, self.lua_grammar_folder_at())
        if chosen is not None:
            self.ui_edit_select.setText(chosen)
            self.lua_grammar_folder_at(chosen)
            self.on_start_check()

    def on_start_check(self):
        self.ui_table_files.clearContents()
        self.ui_table_files.setRowCount(0)
        self.start_check(self.lua_grammar_folder_at())

    @staticmethod
    def meet_extension(where: str):
        name, ext = splitext(where)
        return ext == '.lua'

    def start_check(self, where: str):
        self.ui_tb_nested.hide()

        if not exists(where):
            return

        file_list = []
        if isdir(where):
            for root, dirs, files in walk(where):
                for file in files:
                    filename = normpath(join(root, file))
                    if Cmm.is_hiding_path(filename) is False:
                        if self.meet_extension(filename):
                            file_list.append(filename)
        elif isfile(where):
            if self.meet_extension(where):
                file_list.append(where)
        else:
            return

        if len(file_list) > 0:
            self.set_widgets_enabled(False)
            self.check_all(file_list)

    def set_widgets_enabled(self, ok: bool):
        self.ui_edit_select.setEnabled(ok)
        self.ui_btn_check.setEnabled(ok)

    def check_all(self, files: List[str]):
        files.reverse()

        def check_one():
            while len(files) > 0:
                where = files.pop()
                self.check_one(where)
                sleep(0.015)

            if self.thread:
                self.thread.stop()
                self.thread = None

            self.set_widgets_enabled(True)

        self.thread = Cmm.StoppableThread(target=check_one)
        self.thread.daemon = True
        self.thread.start()

    def check_one(self, where: str):
        ok, blocks = LuaSyntaxChecker.check_nested(where)

        text = relpath(where, self.lua_grammar_folder_at())
        icon = ResMap.img_correct if ok else ResMap.img_error
        level_num = len(blocks)
        level = str(level_num - 1) if ok else '0'
        item1 = GUI.create_table_item(text, icon=icon)
        item2 = GUI.create_table_item(level)
        if level_num > 6:
            item2.setBackground(Qt.red)
        row = self.ui_table_files.rowCount()
        self.ui_table_files.setRowCount(row + 1)
        self.ui_table_files.setItem(row, 0, item1)
        self.ui_table_files.setItem(row, 1, item2)
        self.row_info.append((where, blocks,))

    def on_item_double_clicked(self, item: QTableWidgetItem):
        where, blocks = self.row_info[item.row()]
        print(item.row(), where)
        self.ui_tb_nested.clear()
        self.ui_tb_nested.hide()
        limit_level = 5
        start = limit_level + 1
        if blocks is not None:
            blocks = reversed(blocks[start:])
            display = False
            for block_list in blocks:
                display = True
                for block in block_list:
                    for line in block.source():
                        self.ui_tb_nested.append(line)
            if display:
                self.ui_tb_nested.show()
