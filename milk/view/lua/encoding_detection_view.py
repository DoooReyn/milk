from os import walk
from os.path import exists, isdir, isfile, join, normpath, splitext
from time import sleep

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTextEdit

from milk.cmm import Cmm
from milk.conf import LangUI, settings, StyleSheet, UIDef
from milk.gui import GUI


class _View(GUI.View):
    def __init__(self):
        super(_View, self).__init__()

        # create widgets
        self.ui_lab_choose = GUI.create_label(LangUI.lua_encoding_detection_folder_selection)
        self.ui_edit_choose = GUI.create_line_edit(placeholder=LangUI.lua_encoding_detection_folder_selection)
        self.ui_act_choose = GUI.set_folder_action_for_line_edit(self.ui_edit_choose)
        self.ui_lab_only = GUI.create_label(LangUI.lua_encoding_detection_extension_specify)
        self.ui_edit_only = GUI.create_line_edit(placeholder=".lua,.py,.js,...")
        self.ui_cb_convert = GUI.create_check_box(LangUI.lua_encoding_detection_convert_to_utf8)
        self.ui_cb_non_utf8 = GUI.create_check_box(LangUI.lua_encoding_detection_non_utf8_only)
        self.ui_tb_log = GUI.create_text_browser()
        self.ui_tb_log.setStyleSheet(StyleSheet.TextBrowser)
        self.ui_tb_log.setLineWrapMode(QTextEdit.NoWrap)
        self.ui_tb_log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # layout widgets
        self.ui_layout = GUI.create_grid_layout(self)
        GUI.add_grid_in_rows(self.ui_layout, [
            (
                GUI.GridItem(self.ui_lab_choose, 0, 1),
                GUI.GridItem(self.ui_edit_choose, 1, 3),
            ),
            (
                GUI.GridItem(self.ui_lab_only, 0, 1),
                GUI.GridItem(self.ui_edit_only, 1, 3),
            ),
            (
                GUI.GridItem(self.ui_cb_convert, 1, 1),
                GUI.GridItem(self.ui_cb_non_utf8, 2, 1),
            ),
            (
                GUI.GridItem(self.ui_tb_log, 0, 4),
            ),
        ])
        GUI.set_grid_span(self.ui_layout, [2], [3])


class EncodingDetectionView(_View):
    def __init__(self):
        super(EncodingDetectionView, self).__init__()

        self.colors = [QColor('#ff6b81'), QColor('#6bddcd'), ]
        self.color_index = 0
        self.setWindowTitle(LangUI.lua_encoding_detection_title)
        self.setMinimumSize(640, 400)
        self.setup_window_code(UIDef.LuaEncodingChecker.value)
        self.setup_ui_signals()
        self.ui_edit_choose.setText(self.last_at())

    def setup_ui_signals(self):
        self.ui_edit_choose.returnPressed.connect(self.on_detect)
        self.ui_edit_only.returnPressed.connect(self.on_detect)
        self.ui_act_choose.triggered.connect(self.on_choose_files)
        self.ui_cb_non_utf8.toggled.connect(self.on_detect)

    def on_detect(self):
        self.ui_tb_log.clear()
        self.ui_tb_log.setFocus()
        self.start_detection(self.last_at())

    @staticmethod
    def last_at(at: str = None):
        if at is not None:
            settings.setValue('lua:encoding_detection:last_dir', at)
        else:
            return settings.value('lua:encoding_detection:last_dir', Cmm.user_document_dir(), str)

    def set_widgets_enabled(self, ok: bool):
        GUI.set_text_browser_selectable(self.ui_tb_log, ok)
        widgets = [self.ui_edit_choose, self.ui_edit_only, self.ui_cb_convert, self.ui_cb_non_utf8]
        [w.setEnabled(ok) for w in widgets]

    def set_next_color(self, color=None):
        self.ui_tb_log.setTextColor(color if color is not None else self.next_color())

    def next_color(self):
        self.color_index += 1
        if self.color_index == len(self.colors):
            self.color_index = 0
        return self.colors[self.color_index]

    def extensions(self):
        extensions = self.ui_edit_only.text().split(',')
        for i in range(len(extensions) - 1, -1, -1):
            if len(extensions[i].strip()) <= 1:
                extensions.pop(i)
        return extensions

    @staticmethod
    def meet_file_extensions(extensions: Cmm.Iterable[str], ext: str):
        if len(extensions) == 0:
            return True
        return ext in extensions

    def detect_one(self, where: str):
        if self.ui_cb_convert.isChecked():
            encoding, converted = Cmm.convert_file_encoding_to_utf8(where)
            text = "[ {} ] {} ".format(encoding, normpath(where))
            text = text + LangUI.lua_encoding_detection_convert_ok if converted else LangUI.lua_encoding_detection_convert_bad
        else:
            converted = True
            encoding = Cmm.get_file_encoding(where)
            text = "[ {} ] {} ".format(encoding, normpath(where))
        output = True
        is_utf8 = Cmm.is_utf8_encoding(encoding)
        if self.ui_cb_non_utf8.isChecked():
            output = not is_utf8
        if output is True:
            if is_utf8 is False or converted is False:
                self.bad(text)
            else:
                self.ok(text)

    def _detect_encoding(self, file_list: [str]):
        file_list.reverse()

        def _run():
            while len(file_list) > 0:
                where = file_list.pop()
                self.detect_one(where)
                sleep(0.015)

            if self.thread:
                self.thread.stop()

            self.set_widgets_enabled(True)

        self.thread = Cmm.StoppableThread(target=_run)
        self.thread.daemon = True
        self.thread.start()

    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
        super(EncodingDetectionView, self).closeEvent(event)

    def ok(self, text: str):
        self.set_next_color()
        self.ui_tb_log.append(text)
        self.scrollToBottom()

    def bad(self, text: str):
        self.set_next_color(Qt.red)
        self.ui_tb_log.append(text)
        self.scrollToBottom()

    def scrollToBottom(self):
        bar = self.ui_tb_log.verticalScrollBar()
        bar.setValue(bar.maximum())

    def start_detection(self, where: str):
        if not exists(where):
            return

        extensions = self.extensions()
        file_list = []
        if isdir(where):
            for root, dirs, files in walk(where):
                for file in files:
                    filename = normpath(join(root, file))
                    if Cmm.is_hiding_path(filename) is False:
                        if self.meet_file_extensions(extensions, splitext(filename)[1]):
                            file_list.append(filename)
        elif isfile(where):
            file_list.append(where)
        else:
            self.bad(LangUI.lua_encoding_detection_file_not_found.format(normpath(where)))
            return

        if len(file_list) > 0:
            self.set_widgets_enabled(False)
            self._detect_encoding(file_list)

    def on_choose_files(self):
        title = LangUI.lua_encoding_detection_folder_selection
        chosen = GUI.dialog_for_directory_selection(self, title, self.last_at())
        if chosen is not None:
            self.ui_edit_choose.setText(chosen)
            self.last_at(chosen)
            self.on_detect()
