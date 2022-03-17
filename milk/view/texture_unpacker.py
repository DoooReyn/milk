import json
import plistlib
import random
from os.path import basename, dirname, join, exists, abspath
from typing import Union
from PIL import Image

from PyQt5.QtCore import pyqtSignal, QRectF, QRect, Qt
from PyQt5.QtGui import QPixmap, QColor, QPen, QBrush, QKeyEvent
from PyQt5.QtWidgets import QListWidget, QHBoxLayout, QGraphicsScene, QGraphicsView, QListWidgetItem, \
    QGraphicsRectItem, QMenu, QMenuBar, QAction, QVBoxLayout, QWidget, QMainWindow, QFileDialog

from milk.cmm import TraceBack, Cmm
from milk.conf import Lang, signals, UIDef
from .ui_base import UIBase


def _mapping_list(_result, _name, _data):
    for i, v in enumerate(_name):
        if isinstance(v, list):
            _mapping_list(_result, v, _data[i])
        else:
            _result[v] = _data[i]

    return _result


def _parse_str(_name, _str):
    return _mapping_list({}, _name, json.loads(_str.replace("{", "[").replace("}", "]")))


def parse_plist(data):
    fmt = data.get("metadata").get("format")
    # check file format
    if fmt not in (0, 1, 2, 3):
        print("fail: unsupported format " + str(fmt))
        return None

    ret = {}
    frame_data_list = []

    for (name, config) in data.get("frames").items():
        frame_data = {}
        if fmt == 0:
            source_size = {
                "w": config.get("originalWidth", 0),
                "h": config.get("originalHeight", 0),
            }
            rotated = False
            src_rect = (
                config.get("x", 0),
                config.get("y", 0),
                config.get("x", 0) + config.get("originalWidth", 0),
                config.get("y", 0) + config.get("originalHeight", 0),
            )
            dst_rect = (
                config.get("x", 0),
                config.get("y", 0),
                config.get("width", 0),
                config.get("height", 0),
            )
            offset = {
                "x": config.get("offsetX", False),
                "y": config.get("offsetY", False),
            }
        elif fmt == 1 or fmt == 2:
            frame = _parse_str([["x", "y"], ["w", "h"]], config.frame)
            center_offset = _parse_str(["x", "y"], config.offset)
            source_size = _parse_str(["w", "h"], config.sourceSize)
            rotated = config.get("rotated", False)
            src_rect = (
                frame["x"],
                frame["y"],
                frame["x"] + (frame["h"] if rotated else frame["w"]),
                frame["y"] + (frame["w"] if rotated else frame["h"])
            )
            offset = {
                "x": source_size["w"] / 2 + center_offset["x"] - frame["w"] / 2,
                "y": source_size["h"] / 2 - center_offset["y"] - frame["h"] / 2,
            }
            dst_rect = (
                frame["x"],
                frame["y"],
                frame["x"] + frame["w"],
                frame["y"] + frame["h"]
            )
        elif fmt == 3:
            frame = _parse_str([["x", "y"], ["w", "h"]], config.textureRect)
            center_offset = _parse_str(["x", "y"], config.spriteOffset)
            source_size = _parse_str(["w", "h"], config.spriteSourceSize)
            rotated = config.get("textureRotated", False)
            src_rect = (
                frame["x"],
                frame["y"],
                frame["x"] + (frame["h"] if rotated else frame["w"]),
                frame["y"] + (frame["w"] if rotated else frame["h"])
            )
            dst_rect = (
                frame["x"],
                frame["y"],
                frame["x"] + frame["w"],
                frame["y"] + frame["h"]
            )
            offset = {
                "x": source_size["w"] / 2 + center_offset["x"] - frame["w"] / 2,
                "y": source_size["h"] / 2 - center_offset["y"] - frame["h"] / 2,
            }
        else:
            continue

        frame_data["name"] = name
        frame_data["source_size"] = (int(source_size["w"]), int(source_size["h"]))
        frame_data["rotated"] = rotated
        frame_data["src_rect"] = [int(x) for x in src_rect]
        frame_data["dst_rect"] = [int(x) for x in dst_rect]
        frame_data["offset"] = (int(offset["x"]), int(offset["y"]))

        frame_data_list.append(frame_data)

    ret["frames"] = frame_data_list
    ret["texture"] = data.get("metadata").get("textureFileName")
    return ret


class ResizableGraphicsView(QGraphicsView):
    resize_event = pyqtSignal()

    def resizeEvent(self, evt):
        self.resize_event.emit()
        evt.accept()


class DroppableGraphicsScene(QGraphicsScene):
    image_dropped = pyqtSignal(str, str)

    def __init__(self, view: ResizableGraphicsView = None):
        super(DroppableGraphicsScene, self).__init__()
        self.addText("请在此处拖入 .png/.plist 文件")
        # view.setAlignment(Qt.AlignCenter)
        view.setScene(self)
        view.resize_event.connect(self.__resize)
        self.image_view = view
        self.image_path = None
        self.plist_path = None

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
        self.image_dropped.emit(self.image_path, self.plist_path)
        event.acceptProposedAction()

    def __apply_image(self):
        if self.image_path and self.plist_path and exists(self.plist_path) and exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            # width = pixmap.width()
            # height = pixmap.height()
            # w_width = self.image_view.width()
            # w_height = self.image_view.height()
            # if width // w_width > height // w_height:
            #     pixmap = pixmap.scaledToWidth(w_width, Qt.SmoothTransformation)
            # else:
            #     pixmap = pixmap.scaledToHeight(w_height, Qt.SmoothTransformation)
            self.clear()
            self.addPixmap(pixmap)
        else:
            self.plist_path = None
            self.image_path = None
            self.clear()
            self.addText("请在此处拖入 .png/.plist 文件")


class TextureUnpacker(UIBase, QMainWindow):
    def __init__(self):
        self.ui_graphics_scene: Union[DroppableGraphicsScene, None] = None
        self.ui_graphics_view: Union[ResizableGraphicsView, None] = None
        self.ui_list_img: Union[QListWidget, None] = None
        self.selected_rect: Union[QGraphicsRectItem, None] = None
        self.plist_data: Union[dict, None] = None

        super(QMainWindow, self).__init__()
        super(TextureUnpacker, self).__init__()

    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        menu_bar = QMenuBar()
        menu = menu_bar.addMenu("文件")
        save_all = QAction("保存所有图片", self)
        save_all.setShortcut("Ctrl+S")
        save_all.triggered.connect(self.on_save_all)
        save_one = QAction("保存选中图片", self)
        save_one.setShortcut("Ctrl+Shift+S")
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
        save_act = QAction("保存", self)
        pop_menu.addAction(save_act)
        if self.ui_list_img.itemAt(position):
            pop_menu.addAction(save_act)
        save_act.triggered.connect(self.on_save_one)
        pop_menu.exec_(self.ui_list_img.mapToGlobal(position))

    # noinspection PyBroadException
    def on_save_all(self):
        if not self.plist_data:
            return

        dir_choose = QFileDialog.getExistingDirectory(self, "请选择图片保存位置", Cmm.user_picture_dir())
        if len(dir_choose) <= 0:
            return

        print(dir_choose, self.ui_graphics_scene.image_path)

        src_image = None
        try:
            src_image = Image.open(self.ui_graphics_scene.image_path)
            frames = self.plist_data.get("frames")
            for frame in frames:
                filename = frame.get("name")
                save_at = join(dir_choose, filename)
                ltx, lty, rbx, rby = frame.get("src_rect")
                sw, sh = frame.get("source_size")
                split_image = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
                crop_frame = src_image.crop((ltx, lty, rbx, rby))
                split_image.paste(crop_frame, (0, 0, sw, sh))
                split_image.save(save_at)
                split_image.close()
        except:
            TraceBack().trace_back()
        finally:
            if src_image is not None:
                src_image.close()
                Cmm.open_external_file(dir_choose)

    def on_save_one(self):
        cur_row = self.ui_list_img.currentRow()
        cur_item = self.ui_list_img.item(cur_row)
        if cur_item is None:
            return

        cur_name = cur_item.text()

        dir_choose = QFileDialog.getExistingDirectory(self, "请选择图片保存位置", Cmm.user_picture_dir())
        if len(dir_choose) > 0:
            self.extract_picture(dir_choose, cur_name)

    # noinspection PyBroadException
    def extract_picture(self, save_at, filename):
        if not self.plist_data:
            return
        frames = self.plist_data.get("frames")

        src_image = None
        split_image = None

        try:
            for frame in frames:
                if frame.get("name") == filename:
                    ltx, lty, rbx, rby = frame.get("src_rect")
                    sw, sh = frame.get("source_size")
                    src_image: Image = Image.open(self.ui_graphics_scene.image_path)
                    split_image = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
                    crop_frame = src_image.crop((ltx, lty, rbx, rby))
                    split_image.paste(crop_frame, (0, 0, sw, sh))
                    split_image.save(join(save_at, filename))
                    split_image.close()
                    src_image.close()
                    Cmm.open_external_file(save_at)
                    break
        except:
            TraceBack().trace_back()
        finally:
            if split_image is not None:
                split_image.close()
            if src_image is not None:
                src_image.close()

    def on_image_dropped(self, image_path, plist_path):
        print("on_image_dropped: ", image_path, plist_path)
        self.parse_image(plist_path)

    # noinspection PyBroadException
    def parse_image(self, path):
        def on_fail():
            signals.logger_error("[{0}] 读取 '{0}' 失败！".format(Lang.get("item_image_texture_unpacker"), path))
            signals.window_switch_to_main.emit()

        try:
            with open(path, 'rb') as fp:
                data = plistlib.load(fp)

                if data is None:
                    on_fail()
                    return

                data = parse_plist(data)
                if not data or not data.get("frames") or not data.get("texture"):
                    on_fail()

                self.refresh_list_widget(data)
        except:
            TraceBack().trace_back()
            on_fail()

    @staticmethod
    def random_color():
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 80)

    def refresh_list_widget(self, data):
        self.plist_data = data
        frames = data.get("frames")
        names = []
        for frame in frames:
            names.append(frame.get("name"))
        self.ui_list_img.clear()
        self.ui_list_img.addItems(names)

    def on_select_part(self, item: QListWidgetItem):
        name = item.text()
        if self.selected_rect is not None:
            self.ui_graphics_scene.removeItem(self.selected_rect)
            self.selected_rect = None
        if self.plist_data:
            frames = self.plist_data.get("frames")
            for frame in frames:
                if frame.get("name") == name:
                    x, y, w, h = frame.get("dst_rect")
                    rect = QRectF(x, y, w, h)
                    pen = QPen(self.random_color())
                    brush = QBrush(self.random_color())
                    self.selected_rect = self.ui_graphics_scene.addRect(rect, pen=pen, brush=brush)
                    break

    def closeEvent(self, event):
        event.accept()
        signals.window_closed.emit(UIDef.ImageTextureUnpacker.value)
