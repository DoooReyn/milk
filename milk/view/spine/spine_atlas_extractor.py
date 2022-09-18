import re
import time
from os import makedirs, walk
from os.path import dirname, exists, isdir, join, splitext
from shutil import rmtree
from typing import Union

from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QPushButton, QWidget

from milk.cmm import StoppableThread
from milk.conf import Lang, LangUI, settings, signals, UIDef, UserKey
from milk.view.ui_base import UIBase


class SpineAtlasExtractor(UIBase):
    def __init__(self, parent: QWidget = None):
        self.ui_edit_atlas_locate_dir: Union[QLineEdit, None] = None
        self.ui_btn_atlas_choose: Union[QPushButton, None] = None
        self.ui_edit_atlas_out_dir: Union[QLineEdit, None] = None
        self.ui_btn_out_choose: Union[QPushButton, None] = None
        self.ui_btn_parse: Union[QPushButton, None] = None
        self.setup_window_code(UIDef.ImageSpineAtlasExtractor.value)

        super().__init__(parent)

    def setup_ui(self):
        self.add_vertical_layout(self)

        line1 = self.add_widget(self)
        self.add_horizontal_layout(line1)
        self.ui_edit_atlas_locate_dir = self.add_line_edit(LangUI.atlas_extractor_ui_edit_atlas_dir, line1)
        self.ui_btn_atlas_choose = self.add_push_button(LangUI.atlas_extractor_ui_btn_choose, line1)

        line2 = self.add_widget(self)
        self.add_horizontal_layout(line2)
        self.ui_edit_atlas_out_dir = self.add_line_edit(LangUI.atlas_extractor_ui_edit_out_dir, line2)
        self.ui_btn_out_choose = self.add_push_button(LangUI.atlas_extractor_ui_btn_choose, line2)

        line3 = self.add_widget(self)
        self.add_horizontal_layout(line3)
        self.ui_btn_parse = self.add_push_button(LangUI.atlas_extractor_ui_btn_parse, line3)

        self.setWindowTitle(Lang.get("item_image_spine_atlas_extractor"))
        self.ui_edit_atlas_locate_dir.setText(settings.value(UserKey.SpineAtlasExtractor.atlas_locate_dir, "", str))
        self.ui_edit_atlas_out_dir.setText(settings.value(UserKey.SpineAtlasExtractor.atlas_out_dir, "", str))

    def setup_signals(self):
        self.ui_edit_atlas_locate_dir.returnPressed.connect(self.on_sync_atlas_locate_dir)
        self.ui_edit_atlas_locate_dir.editingFinished.connect(self.on_sync_atlas_locate_dir)
        self.ui_edit_atlas_out_dir.returnPressed.connect(self.on_sync_atlas_out_dir)
        self.ui_edit_atlas_out_dir.editingFinished.connect(self.on_sync_atlas_out_dir)
        self.ui_btn_parse.clicked.connect(self.on_parse)
        self.ui_btn_atlas_choose.clicked.connect(self.on_choose_locate_dir)
        self.ui_btn_out_choose.clicked.connect(self.on_choose_out_dir)

    def on_sync_atlas_locate_dir(self):
        settings.setValue(UserKey.SpineAtlasExtractor.atlas_locate_dir, self.ui_edit_atlas_locate_dir.text())

    def on_sync_atlas_out_dir(self):
        settings.setValue(UserKey.SpineAtlasExtractor.atlas_out_dir, self.ui_edit_atlas_out_dir.text())

    def on_choose_locate_dir(self):
        dir_choose = QFileDialog.getExistingDirectory(self, LangUI.atlas_extractor_ui_edit_atlas_dir,
                                                      self.ui_edit_atlas_locate_dir.text())
        if len(dir_choose) > 0:
            self.ui_edit_atlas_locate_dir.setText(dir_choose)
            settings.setValue(UserKey.SpineAtlasExtractor.atlas_locate_dir, dir_choose)

    def on_choose_out_dir(self):
        dir_choose = QFileDialog.getExistingDirectory(self, LangUI.atlas_extractor_ui_edit_out_dir,
                                                      self.ui_edit_atlas_out_dir.text())
        if len(dir_choose) > 0:
            self.ui_edit_atlas_out_dir.setText(dir_choose)
            settings.setValue(UserKey.SpineAtlasExtractor.atlas_out_dir, dir_choose)

    def on_parse(self):
        atlas_locate_dir = self.ui_edit_atlas_locate_dir.text()
        atlas_out_dir = self.ui_edit_atlas_out_dir.text()

        if not isdir(atlas_locate_dir):
            signals.logger_error.emit(LangUI.atlas_extractor_ui_edit_atlas_dir)
            self.ui_edit_atlas_locate_dir.focusWidget()
            return

        if not isdir(atlas_out_dir):
            signals.logger_error.emit(LangUI.atlas_extractor_ui_edit_out_dir)
            self.ui_edit_atlas_out_dir.focusWidget()
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
                    time.sleep(1)
                self.thread.stop()
                self.thread = None
                self.reset_ui(True)
                signals.logger_info.emit(LangUI.msg_all_extracted.format(locate))
                signals.window_switch_to_main.emit()

            self.thread = StoppableThread(target=_run)
            self.thread.daemon = True
            self.thread.start()

    def reset_ui(self, ok: bool):
        self.ui_btn_atlas_choose.setEnabled(ok)
        self.ui_btn_out_choose.setEnabled(ok)
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
        src_atlas.seek(0, 0)

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
        except Exception as e:
            signals.logger_error.emit(str(e))
        finally:
            src_atlas.close()
