from os import walk
from os.path import exists, isdir, isfile, join, normpath, splitext

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from milk.cmm import Cmm
from milk.conf import LangUI, settings, UIDef
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
        self.ui_radio_convert = GUI.create_radio_btn(LangUI.lua_encoding_detection_convert_to_utf8)
        self.ui_tb_log = GUI.create_text_browser()
        self.ui_tb_log.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.ui_tb_log.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # layout widgets
        self.ui_layout = GUI.create_grid_layout(self)
        GUI.add_grid_in_rows(self.ui_layout, [
            (
                GUI.GridItem(self.ui_lab_choose, 0, 1),
                GUI.GridItem(self.ui_edit_choose, 1, 2),
            ),
            (
                GUI.GridItem(self.ui_lab_only, 0, 1),
                GUI.GridItem(self.ui_edit_only, 1, 1),
                GUI.GridItem(self.ui_radio_convert, 2, 1)
            ),
            (
                GUI.GridItem(self.ui_tb_log, 0, 3),
            ),
        ])
        GUI.set_grid_span(self.ui_layout, [2], [1])


class EncodingDetectionView(_View):
    def __init__(self):
        super(EncodingDetectionView, self).__init__()

        self.colors = [QColor('#ff6b81'), QColor('#6bddcd'), ]
        self.color_index = 0
        self.setWindowTitle(LangUI.lua_encoding_detection_title)
        self.setMinimumSize(400, 400)
        self.resize(600, 400)
        self.setup_window_code(UIDef.LuaEncodingChecker.value)
        self.setup_ui_signals()
        self.ui_edit_choose.setText(self.last_at())

    def setup_ui_signals(self):
        self.ui_edit_choose.returnPressed.connect(self.on_detect)
        self.ui_edit_only.returnPressed.connect(self.on_detect)
        self.ui_act_choose.triggered.connect(self.on_choose_files)

    def on_detect(self):
        self.ui_tb_log.clear()
        self.start_detection(self.last_at())

    @staticmethod
    def last_at(at: str = None):
        if at is not None:
            settings.setValue('lua:encoding_detection:last_dir', at)
        else:
            return settings.value('lua:encoding_detection:last_dir', Cmm.user_document_dir(), str)

    def set_next_color(self, color=None):
        self.ui_tb_log.setTextColor(color if color else self.next_color())

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

    def _detect_encoding(self, where: str):
        one_thread: Cmm.StoppableThread

        def _run():
            if self.ui_radio_convert.isChecked():
                encoding, converted = Cmm.convert_file_encoding_to_utf8(where)
                result = "[ {} ] {} ".format(encoding, normpath(where))
                if converted:
                    self.ok(result + LangUI.lua_encoding_detection_convert_ok)
                else:
                    self.bad(result + LangUI.lua_encoding_detection_convert_bad)
            else:
                encoding = Cmm.get_file_encoding(where)
                result = "[ {} ] {} ".format(encoding, normpath(where))
                self.ok(result)
            if one_thread:
                one_thread.stop()

        one_thread = Cmm.StoppableThread(target=_run)
        one_thread.daemon = True
        one_thread.start()

    def ok(self, text: str):
        self.set_next_color()
        self.ui_tb_log.append(text)

    def bad(self, text: str):
        self.set_next_color(QColor(Qt.red))
        self.ui_tb_log.append("<b>{}</b>".format(text))

    def start_detection(self, where: str):
        if not exists(where):
            return

        extensions = self.extensions()
        if isdir(where):
            file_list = []
            for root, dirs, files in walk(where):
                for file in files:
                    filename = join(root, file)
                    ext = splitext(filename)[1]
                    if self.meet_file_extensions(extensions, ext):
                        file_list.append(filename)
            [self.start_detection(name) for name in file_list]
        elif isfile(where):
            self._detect_encoding(where)
        else:
            self.bad(LangUI.lua_encoding_detection_file_not_found.format(normpath(where)))

    def on_choose_files(self):
        title = LangUI.lua_encoding_detection_folder_selection
        chosen = GUI.dialog_for_directory_selection(self, title, self.last_at())
        if chosen is not None:
            self.ui_edit_choose.setText(chosen)
            self.last_at(chosen)
            self.on_detect()
