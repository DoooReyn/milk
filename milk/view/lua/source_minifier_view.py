from os import walk
from os.path import exists, isdir, isfile, join, normpath, splitext
from time import sleep
from typing import List, Optional

from PyQt5.QtCore import Qt

from cmm import Cmm
from conf import LangUI, settings, UIDef, UserKey, StyleSheet
from milk.gui import GUI
from .lua_source_interpreter import LuaRestoreTree, LuaSourceInterpreter


class _View(GUI.View):
    def __init__(self):
        super(_View, self).__init__()

        self.ui_edit_folder = GUI.create_line_edit(readonly=True, placeholder=LangUI.lua_minifier_folder_at)
        self.ui_act_folder = GUI.set_folder_action_for_line_edit(self.ui_edit_folder)
        self.ui_btn_start = GUI.create_push_btn(LangUI.lua_minifier_start)
        self.ui_group_options = GUI.create_group_box(LangUI.lua_minifier_options)
        self.ui_check_replace = GUI.create_check_box(LangUI.lua_minifier_replace)
        self.ui_check_keep_comments = GUI.create_check_box(LangUI.lua_minifier_keep_comment)
        self.ui_check_wrap_table = GUI.create_check_box(LangUI.lua_minifier_wrap_table)
        self.ui_group_options_layout = GUI.create_horizontal_layout(self.ui_group_options)
        self.ui_group_options_layout.addWidget(self.ui_check_replace)
        self.ui_group_options_layout.addWidget(self.ui_check_keep_comments)
        self.ui_group_options_layout.addWidget(self.ui_check_wrap_table)
        self.ui_group_options_layout.setAlignment(Qt.AlignLeft)
        self.ui_check_replace.setChecked(True)
        self.ui_check_keep_comments.setChecked(False)
        self.ui_check_wrap_table.setChecked(False)
        self.ui_tb_log = GUI.create_text_browser()
        self.ui_tb_log.setStyleSheet(StyleSheet.TextBrowser)

        self.ui_layout = GUI.create_grid_layout(self)
        GUI.add_grid_in_rows(self.ui_layout, (
            (
                GUI.GridItem(self.ui_edit_folder, 0, 2),
                GUI.GridItem(self.ui_btn_start, 2, 1),
            ),
            (
                GUI.GridItem(self.ui_group_options, 0, 3),
            ),
            (
                GUI.GridItem(self.ui_tb_log, 0, 3),
            )
        ))
        GUI.set_grid_span(self.ui_layout, [2], [0, 1])


class SourceMinifierView(_View):
    def __init__(self):
        super(SourceMinifierView, self).__init__()

        self.thread: Optional[Cmm.StoppableThread] = None

        self.setWindowTitle(LangUI.lua_minifier_title)
        self.setMinimumSize(640, 480)
        self.setup_window_code(UIDef.LuaMinifier.value)
        self.setup_rect_key(UserKey.LuaMinifier.window_rect)
        self.setup_preferences()
        self.setup_ui_signals()

    def setup_preferences(self):
        self.ui_edit_folder.setText(self.lua_minifier_folder_at())

    def setup_ui_signals(self):
        self.ui_btn_start.clicked.connect(self.on_start_minifier)
        self.ui_act_folder.triggered.connect(self.on_select_folder)

    @staticmethod
    def lua_minifier_folder_at(at: str = None):
        if at is not None:
            settings.setValue(UserKey.LuaMinifier.folder_at, at)
        else:
            return settings.value(UserKey.LuaMinifier.folder_at, Cmm.user_document_dir(), str)

    def closeEvent(self, event):
        if self.thread is not None:
            self.thread.stop()
        super(SourceMinifierView, self).closeEvent(event)

    def on_select_folder(self):
        chosen = GUI.dialog_for_directory_selection(self, LangUI.lua_minifier_folder_at, self.lua_minifier_folder_at())
        if chosen is not None:
            self.ui_edit_folder.setText(chosen)
            self.lua_minifier_folder_at(chosen)
            self.on_start_minifier()

    def on_start_minifier(self):
        self.ui_tb_log.clear()
        self.start_check(self.lua_minifier_folder_at())

    @staticmethod
    def meet_extension(where: str):
        name, ext = splitext(where)
        return ext == '.lua'

    def start_check(self, where: str):
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
        self.ui_edit_folder.setEnabled(ok)
        self.ui_btn_start.setEnabled(ok)
        self.ui_group_options.setEnabled(ok)

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
        target = where
        if self.ui_check_replace.isChecked() is False:
            target = where + '.min'
        try:
            root = LuaRestoreTree(where).root()
            bracket_table_field = self.ui_check_wrap_table.isChecked()
            with_comments = self.ui_check_keep_comments.isChecked()
            interpreter = LuaSourceInterpreter(
                bracket_table_field=bracket_table_field,
                with_comments=with_comments)
            interpreter.interpret(root)
            text = interpreter.content()
            Cmm.save_file_content(target, text)
            self.ui_tb_log.append('<p style="color:green;">{}: OK</p>'.format(target))
        except Exception as e:
            self.ui_tb_log.append('<p style="color:red;">{}: Bad</p>'.format(target))
            print(e)
