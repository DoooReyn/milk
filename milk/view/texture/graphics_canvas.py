from os.path import abspath, basename, dirname, exists, join

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRectF
from PyQt5.QtGui import QBrush, QColor, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsView

from milk.conf import LangUI


class ResizableGraphicsView(QGraphicsView):
    resize_event = pyqtSignal()

    @pyqtSlot()
    def resizeEvent(self, evt):
        # noinspection PyUnresolvedReferences
        self.resize_event.emit()
        evt.accept()


class DroppableGraphicsScene(QGraphicsScene):
    image_dropped = pyqtSignal(str)

    def __init__(self, view: ResizableGraphicsView = None):
        super(DroppableGraphicsScene, self).__init__()
        view.setScene(self)
        # noinspection PyUnresolvedReferences
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
        # noinspection PyUnresolvedReferences
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
