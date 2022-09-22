import re
from os import makedirs, walk
from os.path import dirname, exists, isdir, join, splitext
from shutil import rmtree
from time import sleep

from PIL import Image
from PyQt5.QtCore import Qt

from milk.cmm import Cmm
from milk.conf import LangUI, settings, signals, UIDef, UserKey
from milk.gui import GUI


class _View(GUI.View):
    def __init__(self):
        super(_View, self).__init__()

        # create widgets
        self.ui_lab_locate_dir = GUI.create_label(LangUI.atlas_extractor_ui_lab_locate_dir)
        self.ui_lab_output_dir = GUI.create_label(LangUI.atlas_extractor_ui_lab_output_dir)
        self.ui_edit_atlas_locate_dir = GUI.create_line_edit(
            readonly=True,
            placeholder=LangUI.atlas_extractor_ui_edit_locate_dir)
        self.ui_edit_atlas_output_dir = GUI.create_line_edit(
            readonly=True,
            placeholder=LangUI.atlas_extractor_ui_edit_output_dir)
        self.ui_btn_parse = GUI.create_push_btn(LangUI.atlas_extractor_ui_btn_parse)
        self.ui_act_locate_dir = GUI.set_folder_action_for_line_edit(self.ui_edit_atlas_locate_dir)
        self.ui_act_output_dir = GUI.set_folder_action_for_line_edit(self.ui_edit_atlas_output_dir)

        # layout widget
        self.ui_layout = GUI.create_grid_layout(self)
        self.ui_layout.setAlignment(Qt.AlignTop)
        GUI.add_grid_in_rows(self.ui_layout, (
            (
                GUI.GridItem(self.ui_lab_locate_dir, 0, 1),
                GUI.GridItem(self.ui_edit_atlas_locate_dir, 1, 2),
            ),
            (
                GUI.GridItem(self.ui_lab_output_dir, 0, 1),
                GUI.GridItem(self.ui_edit_atlas_output_dir, 1, 2),
            ),
            (
                GUI.GridItem(self.ui_btn_parse, 0, 3),
            )
        ))
        GUI.set_grid_span(self.ui_layout, [], [2])


class SpineAtlasExtractorView(_View):
    def __init__(self):
        super(SpineAtlasExtractorView, self).__init__()

        self.setFixedSize(500, 118)
        self.setWindowTitle(LangUI.atlas_extractor_title)

        self.setup_window_code(UIDef.ImageSpineAtlasExtractor.value)
        self.setup_resize_keys(UserKey.SpineAtlasExtractor.window_width, UserKey.SpineAtlasExtractor.window_height)
        self.setup_ui_signals()
        self.setup_preferences()

    def setup_ui_signals(self):
        self.ui_edit_atlas_locate_dir.textChanged.connect(self.on_sync_atlas_locate_dir)
        self.ui_edit_atlas_output_dir.textChanged.connect(self.on_sync_atlas_output_dir)
        self.ui_act_locate_dir.triggered.connect(self.on_choose_locate_dir)
        self.ui_act_output_dir.triggered.connect(self.on_choose_output_dir)
        self.ui_btn_parse.clicked.connect(self.on_parse)

    def setup_preferences(self):
        self.ui_edit_atlas_locate_dir.setText(self.atlas_locate_dir())
        self.ui_edit_atlas_output_dir.setText(self.atlas_output_dir())

    @staticmethod
    def atlas_locate_dir():
        return settings.value(UserKey.SpineAtlasExtractor.atlas_locate_dir, "", str)

    @staticmethod
    def atlas_output_dir():
        return settings.value(UserKey.SpineAtlasExtractor.atlas_out_dir, "", str)

    def on_sync_atlas_locate_dir(self):
        settings.setValue(UserKey.SpineAtlasExtractor.atlas_locate_dir, self.ui_edit_atlas_locate_dir.text())
        self.ui_edit_atlas_locate_dir.setCursorPosition(0)

    def on_sync_atlas_output_dir(self):
        settings.setValue(UserKey.SpineAtlasExtractor.atlas_out_dir, self.ui_edit_atlas_output_dir.text())
        self.ui_edit_atlas_output_dir.setCursorPosition(0)

    def on_choose_locate_dir(self):
        title = LangUI.atlas_extractor_ui_edit_locate_dir
        where = self.ui_edit_atlas_locate_dir.text()
        dir_choose = GUI.dialog_for_directory_selection(self, title, where)
        if dir_choose is not None:
            self.ui_edit_atlas_locate_dir.setText(dir_choose)
            self.on_sync_atlas_locate_dir()

    def on_choose_output_dir(self):
        title = LangUI.atlas_extractor_ui_edit_output_dir
        where = self.ui_edit_atlas_output_dir.text()
        dir_choose = GUI.dialog_for_directory_selection(self, title, where)
        if dir_choose is not None:
            self.ui_edit_atlas_output_dir.setText(dir_choose)
            self.on_sync_atlas_output_dir()

    def on_parse(self):
        atlas_locate_dir = self.ui_edit_atlas_locate_dir.text()
        atlas_out_dir = self.ui_edit_atlas_output_dir.text()

        if not isdir(atlas_locate_dir):
            signals.logger_error.emit(LangUI.atlas_extractor_ui_edit_locate_dir)
            self.ui_edit_atlas_locate_dir.focusWidget()
            return

        if not isdir(atlas_out_dir):
            signals.logger_error.emit(LangUI.atlas_extractor_ui_edit_output_dir)
            self.ui_edit_atlas_output_dir.focusWidget()
            return

        self.reset_ui(False)
        self._parse(atlas_locate_dir, atlas_out_dir)

    def _parse(self, locate, out):
        file_no = []
        for root, dirs, files in walk(locate):
            for name in files:
                dir_name = splitext(name)[0]
                ext = splitext(name)[-1]
                if ext == '.atlas':
                    src_file = join(root, name)
                    dst_dir = join(out, dir_name)
                    file_no.append((src_file, dst_dir))
        if len(file_no) <= 0:
            signals.logger_error.emit(LangUI.msg_atlas_not_found)
        else:
            def _run():
                while len(file_no) > 0:
                    src, dst = file_no.pop()
                    self._parse_file(src, dst)
                    sleep(1)
                self.thread.stop()
                self.thread = None
                self.reset_ui(True)
                signals.logger_info.emit(LangUI.msg_all_extracted.format(locate))
                signals.window_switch_to_main.emit()

            self.thread = Cmm.StoppableThread(target=_run)
            self.thread.daemon = True
            self.thread.start()

    def reset_ui(self, ok: bool):
        self.ui_btn_parse.setEnabled(ok)

    # noinspection PyMethodMayBeStatic
    def _parse_file(self, src_file, dst_dir):
        if exists(dst_dir):
            rmtree(dst_dir)
        makedirs(dst_dir, exist_ok=True)

        root = dirname(src_file)
        src_image = None
        src_atlas = open(src_file, 'r')

        src_atlas.seek(0, 2)
        total = src_atlas.tell()
        src_atlas.seek(0)

        try:
            while True:
                line = src_atlas.readline().strip('\n')
                if src_atlas.tell() == total:
                    break

                match1 = re.match(r'.*\.[png|jpg]', line)
                if match1:
                    png_file = join(root, line)
                    src_image = Image.open(png_file)
                    for x in range(4):
                        src_atlas.readline()

                match2 = re.match(r'^[^\s]+', line)
                if not match1 and match2:
                    name = line.strip('\n')
                    rotate = src_atlas.readline().split(':')[1].strip('\n').strip(' ') == 'true'
                    xy = src_atlas.readline().split(':')[1].strip('\n').strip(' ')
                    size = src_atlas.readline().split(':')[1].strip('\n').strip(' ')
                    # orig = src_atlas.readline().split(':')[1].strip('\n').strip(' ')
                    # offset = src_atlas.readline().split(':')[1].strip('\n').strip(' ')
                    src_atlas.readline()

                    width = int(size.split(',')[0])
                    height = int(size.split(',')[1])
                    if rotate:
                        width, height = height, width

                    ltx = int(xy.split(',')[0])
                    lty = int(xy.split(',')[1])
                    rbx = ltx + width
                    rby = lty + height

                    split_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    frame = src_image.crop((ltx, lty, rbx, rby))
                    split_image.paste(frame, (0, 0, width, height))

                    levels = name.split('/')
                    fixed_path = dst_dir
                    for i in range(len(levels) - 1):
                        full_path = join(fixed_path, levels[i])
                        if not exists(full_path):
                            makedirs(full_path, exist_ok=True)
                        fixed_path = full_path
                    split_image.save(join(dst_dir, name + '.png'))
            signals.logger_info.emit(LangUI.msg_one_extracted.format(src_file))
            Cmm.open_external_file(dst_dir)
        except Exception as e:
            signals.logger_error.emit(str(e))
        finally:
            src_atlas.close()
