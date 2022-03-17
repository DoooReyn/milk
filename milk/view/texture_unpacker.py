import plistlib
import re
from os import remove
from os.path import basename, dirname, join, exists, abspath
from typing import Union

from PIL import Image
from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QPixmap, QPen, QBrush, QColor, QIcon
from PyQt5.QtWidgets import QListWidget, QHBoxLayout, QGraphicsScene, QGraphicsView, QListWidgetItem, \
    QMenu, QMenuBar, QAction, QMainWindow, QFileDialog

from milk.cmm import Cmm
from milk.conf import Lang, signals, UIDef, LangUI, settings, UserKey, ResMap
from .ui_base import UIBase


class PlistParser:
    class FileNotFoundException(ValueError):
        pass

    class InvalidFileException(ValueError):
        pass

    class InvalidFormatException(ValueError):
        pass

    class FloatNotSupportException(ValueError):
        pass

    @staticmethod
    def parse(plist_path):
        if not exists(plist_path):
            raise PlistParser.FileNotFoundException("No such file: {0}".format(plist_path))

        try:
            with open(plist_path, 'rb') as f:
                plist_dict = plistlib.load(f)
        except plistlib.InvalidFileException:
            raise PlistParser.InvalidFileException("Invalid plist file: {0}".format(plist_path))

        try:
            if isinstance(plist_dict, dict) and plist_dict.get("frames") and plist_dict.get(
                    "metadata"):
                metadata = plist_dict.get("metadata")
                plist_format = metadata.get("format")
                texture_name = metadata.get("textureFileName")
                plist_frames = plist_dict.get("frames")

                if plist_format not in (0, 1, 2, 3):
                    raise PlistParser.InvalidFormatException("Invalid plist format: {0}".format(plist_format))

                result = {
                    "frames": [],
                    "texture": texture_name
                }

                if plist_format == 0:
                    PlistParser.__parse_format_0(result, plist_frames)
                elif plist_format == 1 or plist_format == 2:
                    PlistParser.__parse_format_1x2(result, plist_frames)
                elif plist_format == 3:
                    PlistParser.__parse_format_3(result, plist_frames)

                return result
            else:
                raise PlistParser.InvalidFileException("Invalid plist file: {0}".format(plist_path))
        except ValueError:
            raise PlistParser.FloatNotSupportException("Not support float value in frame")

    @staticmethod
    def __parse_format_0(result: dict, plist_frames: dict):
        for (name, config) in plist_frames.items():
            ow = int(config.get("originalWidth", 0))
            oh = int(config.get("originalHeight", 0))
            sx = int(config.get("x", 0))
            sy = int(config.get("y", 0))
            ox = int(config.get("offsetX", 0))
            oy = int(config.get("offsetY", 0))
            result["frames"].append({
                "name": name,
                "rotated": False,
                "source_size": (ow, oh),
                "offset": (ox, oy),
                "frame_rect": (sx, sy, ow, oh),
                "crop_rect": (sx, sy, sx + ow, sy + oh)
            })

    @staticmethod
    def __parse_format_1x2(result: dict, plist_frames: dict):
        for (name, config) in plist_frames.items():
            fx, fy, fw, fh = PlistParser.__extract_frame_field(config.get("frame"))
            cx, cy = PlistParser.__extract_frame_field(config.get("offset"))
            sw, sh = PlistParser.__extract_frame_field(config.get("sourceSize"))
            rotated = config.get("rotated", False)
            frame = PlistParser.__get_format1x2x3(name, rotated, fx, fy, fw, fh, cx, cy, sw, sh)
            result["frames"].append(frame)

    @staticmethod
    def __parse_format_3(result: dict, plist_frames: dict):
        for (name, config) in plist_frames.items():
            fx, fy, fw, fh = PlistParser.__extract_frame_field(config.get("textureRect"))
            cx, cy = PlistParser.__extract_frame_field(config.get("spriteOffset"))
            sw, sh = PlistParser.__extract_frame_field(config.get("spriteSourceSize"))
            rotated = config.get("textureRotated", False)
            frame = PlistParser.__get_format1x2x3(name, rotated, fx, fy, fw, fh, cx, cy, sw, sh)
            result["frames"].append(frame)

    @staticmethod
    def __get_format1x2x3(name, rotated, fx, fy, fw, fh, cx, cy, sw, sh):
        ow, oh = (fh, fw) if rotated else (fw, fh)

        return {
            "name": name,
            "rotated": rotated,
            "source_size": (sw, sh),
            "offset": ((sw / 2 + cx - fw / 2), (sh / 2 - cy - fh / 2)),
            "frame_rect": (fx, fy, ow, oh),
            "crop_rect": (fx, fy, fx + ow, fy + oh)
        }

    @staticmethod
    def __extract_frame_field(text):
        return (int(x) for x in re.sub(r"[{}]", "", text).split(','))


class ResizableGraphicsView(QGraphicsView):
    resize_event = pyqtSignal()

    def resizeEvent(self, evt):
        self.resize_event.emit()
        evt.accept()


class DroppableGraphicsScene(QGraphicsScene):
    image_dropped = pyqtSignal(str)

    def __init__(self, view: ResizableGraphicsView = None):
        super(DroppableGraphicsScene, self).__init__()
        view.setScene(self)
        view.resize_event.connect(self.__resize)
        self.setBackgroundBrush(QBrush(QColor("#8e9eab")))

        self.image_view = view
        self.image_path = None
        self.plist_path = None
        self.__selected_rect = None
        self.reset(True)

    def click_rect(self, rect: QRectF):
        if self.__selected_rect:
            self.removeItem(self.__selected_rect)
            self.__selected_rect = None
        pen = QPen(QColor("#00000000"))
        brush = QBrush(QColor(193, 44, 31, 80))
        self.__selected_rect = self.addRect(rect, pen=pen, brush=brush)

    def __resize(self):
        self.setSceneRect(0, 0, self.image_view.width(), self.image_view.height())

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()
        if urls and len(urls) > 0:
            self.image_path = None
            for url in urls:
                file_path = abspath(url.toLocalFile())
                if file_path.endswith(".png"):
                    plist_name = basename(file_path).replace('.png', '.plist')
                    plist_path = abspath(join(dirname(file_path), plist_name))
                    if exists(plist_path):
                        self.image_path = file_path
                        self.plist_path = plist_path
                        break
                elif file_path.endswith(".plist"):
                    plist_name = basename(file_path).replace('.plist', '.png')
                    plist_path = abspath(join(dirname(file_path), plist_name))
                    if exists(plist_path):
                        self.image_path = plist_path
                        self.plist_path = file_path
                        break

            if self.image_path is not None:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        event.accept()

    def dragMoveEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        event.accept()

    def dropEvent(self, event):
        self.__apply_image()
        self.image_dropped.emit(self.plist_path)
        event.acceptProposedAction()

    def __apply_image(self):
        if self.image_path and self.plist_path and exists(self.plist_path) and exists(self.image_path):
            self.reset()
            self.addPixmap(QPixmap(self.image_path))
        else:
            self.reset(True)

    def reset(self, force: bool = False):
        self.clear()
        self.__selected_rect = None
        if force:
            self.plist_path = None
            self.image_path = None
            self.addText(LangUI.texture_unpacker_ui_tip)


class TextureUnpacker(UIBase, QMainWindow):
    def __init__(self):
        self.ui_graphics_scene: Union[DroppableGraphicsScene, None] = None
        self.ui_graphics_view: Union[ResizableGraphicsView, None] = None
        self.ui_list_img: Union[QListWidget, None] = None
        self.plist_data: Union[dict, None] = None

        super(QMainWindow, self).__init__()
        super(TextureUnpacker, self).__init__()

    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        menu_bar = QMenuBar()
        menu = menu_bar.addMenu(LangUI.texture_unpacker_ui_btn_file)
        save_all = QAction(LangUI.texture_unpacker_action_save_all, self)
        save_all.setShortcut("Ctrl+S")
        save_all.setIcon(QIcon(ResMap.img_save_one))
        save_all.triggered.connect(self.on_save_all)
        save_one = QAction(LangUI.texture_unpacker_action_save_one, self)
        save_one.setShortcut("Ctrl+Shift+S")
        save_one.setIcon(QIcon(ResMap.img_save_one))
        save_one.triggered.connect(self.on_save_one)
        menu.addAction(save_all)
        menu.addAction(save_one)
        self.setMenuBar(menu_bar)

        self.ui_graphics_view = ResizableGraphicsView()
        self.ui_graphics_scene = DroppableGraphicsScene(self.ui_graphics_view)
        self.ui_graphics_view.setMinimumSize(640, 640)
        layout.addWidget(self.ui_graphics_view)

        self.ui_list_img = QListWidget()
        self.ui_list_img.setMinimumWidth(200)
        self.ui_list_img.setMaximumWidth(320)
        self.ui_list_img.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_list_img.customContextMenuRequested.connect(self.on_request_list_menu)
        layout.addWidget(self.ui_list_img)

        self.setWindowTitle(Lang.get("item_image_texture_unpacker"))

    def setup_signals(self):
        self.ui_graphics_scene.image_dropped.connect(self.on_image_dropped)
        self.ui_list_img.itemClicked.connect(self.on_select_part)

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
        if not self.plist_data:
            return

        last_dir = settings.value(UserKey.TextureUnpacker.last_save_at, Cmm.user_picture_dir(), str)
        choose_dir = QFileDialog.getExistingDirectory(self, LangUI.texture_unpacker_ui_save_dir, last_dir)
        if len(choose_dir) <= 0:
            return

        settings.setValue(UserKey.TextureUnpacker.last_save_at, choose_dir)
        self.extract(choose_dir)

    def on_save_one(self):
        cur_row = self.ui_list_img.currentRow()
        cur_item = self.ui_list_img.item(cur_row)
        if cur_item is None:
            return

        cur_name = cur_item.text()
        last_dir = settings.value(UserKey.TextureUnpacker.last_save_at, Cmm.user_picture_dir(), str)
        choose_dir = QFileDialog.getExistingDirectory(self, LangUI.texture_unpacker_ui_save_dir, last_dir)
        if len(choose_dir) > 0:
            self.extract_picture(choose_dir, cur_name)
            settings.setValue(UserKey.TextureUnpacker.last_save_at, choose_dir)

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
                        self.extract_frame(choose_dir, mode, src_image, frame, name)
                        break
            else:
                for frame in frames:
                    name = frame.get("name")
                    self.extract_frame(choose_dir, mode, src_image, frame, name)
        except Exception as e:
            print(e)
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

    # noinspection PyBroadException
    def on_image_dropped(self, plist_path):
        def on_error(error):
            self.ui_graphics_scene.reset(True)
            signals.logger_error.emit(
                LangUI.texture_unpacker_parse_fail.format(Lang.get("item_image_texture_unpacker"), plist_path))
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
                        print("locate " + name + " ...")
                        x, y, w, h = frame.get("frame_rect")
                        rect = QRectF(x, y, w, h)
                        self.ui_graphics_scene.click_rect(rect)
                        break
        except Exception as e:
            print(e)

    def closeEvent(self, event):
        event.accept()
        signals.window_closed.emit(UIDef.ImageTextureUnpacker.value)
