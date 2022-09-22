from os import remove
from os.path import exists, join
from typing import Optional

from PIL import Image
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QAction, QListWidgetItem, QMenu

from milk.cmm import Cmm
from milk.conf import LangUI, settings, signals, UIDef, UserKey
from milk.gui import GUI
from .conf import UnpackerMenus
from .graphics_canvas import DroppableGraphicsScene, ResizableGraphicsView
from .plist_parser import PlistParser


class _View(GUI.View):
    def __init__(self):
        super(_View, self).__init__()

        # create widgets
        self.ui_layout = GUI.create_horizontal_layout(self)
        self.ui_graphics_view = ResizableGraphicsView()
        self.ui_graphics_scene = DroppableGraphicsScene(self.ui_graphics_view)
        self.ui_graphics_view.setMinimumSize(640, 640)
        self.ui_list_img = GUI.create_list_widget()
        self.ui_list_img.setMaximumWidth(320)
        self.ui_list_img.setContextMenuPolicy(Qt.CustomContextMenu)

        # layout widgets
        GUI.hv_layout_widgets(self.ui_layout, [self.ui_graphics_view, self.ui_list_img])

        # menu bar
        self.ui_layout.setMenuBar(GUI.create_menu_bar(UnpackerMenus, self))


class TextureUnpackerView(_View):
    def __init__(self):
        super(TextureUnpackerView, self).__init__()

        self.plist_data: Optional[dict] = None
        self.setWindowTitle(LangUI.texture_unpacker_title)

        self.setup_resize_keys(UserKey.TextureUnpacker.window_width, UserKey.TextureUnpacker.window_height)
        self.setup_window_code(UIDef.ImageTextureUnpacker.value)
        self.setup_ui_signals()

    def setup_ui_signals(self):
        self.ui_graphics_scene.image_dropped.connect(self.on_image_dropped)
        self.ui_list_img.itemClicked.connect(self.on_select_part)
        self.ui_list_img.customContextMenuRequested.connect(self.on_request_list_menu)

    @staticmethod
    def get_image_mode(src_image):
        return "RGBA" if (src_image.mode in ('RGBA', 'LA') or (
                src_image.mode == 'P' and 'transparency' in src_image.info)) else "RGB"

    # noinspection PyBroadException
    def extract_picture(self, choose_dir, filename):
        if not self.plist_data:
            return
        self.extract(choose_dir, filename)

    # noinspection PyBroadException
    def extract(self, choose_dir, filename=None):
        src_image = None
        try:
            src_image = Image.open(self.ui_graphics_scene.image_path)
            mode = self.get_image_mode(src_image)
            frames = self.plist_data.get("frames")
            if filename is not None:
                for frame in frames:
                    name = frame.get("name")
                    if name == filename:
                        # print("extract 1: ", mode, name, frame)
                        self.extract_frame(choose_dir, mode, src_image, frame, name)
                        break
            else:
                for frame in frames:
                    name = frame.get("name")
                    # print("extract 2: ", mode, name, frame)
                    self.extract_frame(choose_dir, mode, src_image, frame, name)
        except Exception:
            # print("extract failed: ", e)
            pass
        finally:
            if src_image is not None:
                src_image.close()
            Cmm.open_external_file(choose_dir)

    @staticmethod
    def extract_frame(choose_dir, mode, src_image, frame, name):
        ox, oy = frame.get("offset")
        rotated = frame.get("rotated")
        sw, sh = frame.get("source_size")
        ltx, lty, rbx, rby = frame.get("crop_rect")
        save_at = join(choose_dir, name)

        if exists(save_at):
            remove(save_at)

        dst_image = Image.new(mode, (sw, sh), (0, 0, 0, 0))
        crop_frame = src_image.crop((ltx, lty, rbx, rby))
        if rotated:
            crop_frame = crop_frame.rotate(90, expand=1)
        dst_image.paste(crop_frame, (ox, oy), mask=0)
        dst_image.save(save_at)
        dst_image.close()

        # print(frame)

    def on_request_list_menu(self, position):
        pop_menu = QMenu()
        save_act = QAction(LangUI.texture_unpacker_ui_btn_save, self)
        pop_menu.addAction(save_act)
        if self.ui_list_img.itemAt(position):
            pop_menu.addAction(save_act)
        save_act.triggered.connect(self.on_save_one)
        pop_menu.exec_(self.ui_list_img.mapToGlobal(position))

    # noinspection PyBroadException
    def on_save_all(self):
        if self.plist_data is None:
            return

        last_dir = settings.value(UserKey.TextureUnpacker.last_save_at, Cmm.user_picture_dir(), str)
        choose_dir = GUI.dialog_for_directory_selection(self, LangUI.texture_unpacker_ui_save_dir, last_dir)
        if choose_dir is not None:
            settings.setValue(UserKey.TextureUnpacker.last_save_at, choose_dir)
            self.extract(choose_dir)

    def on_save_one(self):
        cur_row = self.ui_list_img.currentRow()
        cur_item = self.ui_list_img.item(cur_row)
        if cur_item is None:
            return

        cur_name = cur_item.text()
        last_dir = settings.value(UserKey.TextureUnpacker.last_save_at, Cmm.user_picture_dir(), str)
        choose_dir = GUI.dialog_for_directory_selection(self, LangUI.texture_unpacker_ui_save_dir, last_dir)
        if choose_dir is not None:
            self.extract_picture(choose_dir, cur_name)
            settings.setValue(UserKey.TextureUnpacker.last_save_at, choose_dir)

    # noinspection PyBroadException
    def on_image_dropped(self, plist_path):
        def on_error(error):
            self.ui_graphics_scene.reset(True)
            signals.logger_error.emit(
                LangUI.texture_unpacker_parse_fail.format(LangUI.texture_unpacker_title, plist_path))
            signals.logger_error.emit(error)
            signals.window_switch_to_main.emit()

        def on_start():
            self.plist_data = PlistParser.parse(plist_path)
            self.refresh_list_widget()

        Cmm.trace(on_start, on_error)

    def refresh_list_widget(self):
        self.ui_list_img.clear()
        if self.plist_data is not None:
            frames = self.plist_data.get("frames")
            names = (frame.get("name") for frame in frames)
            self.ui_list_img.addItems(names)

    def on_select_part(self, item: QListWidgetItem):
        try:
            name = item.text()
            if self.plist_data:
                frames = self.plist_data.get("frames")
                for frame in frames:
                    if frame.get("name") == name:
                        # print("locate " + name + " ...")
                        x, y, w, h = frame.get("frame_rect")
                        rect = QRectF(x, y, w, h)
                        self.ui_graphics_scene.click_rect(rect)
                        break
        except Exception as e:
            print(e)
