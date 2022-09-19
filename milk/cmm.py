
import random
import sys
from os import listdir, makedirs
from os.path import dirname, isdir, join, realpath, splitext
from shutil import rmtree
from threading import Event, Thread
from traceback import format_exc, print_exc

from PyQt5.QtCore import QStandardPaths, QUrl
from PyQt5.QtGui import QColor, QDesktopServices
from PyQt5.QtWidgets import QMessageBox


class StoppableThread(Thread):
    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Cmm:
    # noinspection PyBroadException
    @staticmethod
    def trace(on_start, on_error=None, on_final=None):
        try:
            return on_start()
        except Exception:
            print_exc()
            if on_error:
                return on_error(format_exc())
        finally:
            if on_final:
                return on_final()

    @staticmethod
    def is_debug_mode():
        return sys.executable.endswith("python.exe")

    @staticmethod
    def app_running_dir():
        return realpath(join(dirname(__file__), '..')) if Cmm.is_debug_mode else realpath(dirname(sys.executable))

    @staticmethod
    def local_cache_dir():
        return QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)

    @staticmethod
    def local_temp_dir():
        return QStandardPaths.writableLocation(QStandardPaths.TempLocation)

    @staticmethod
    def user_root_dir():
        return QStandardPaths.writableLocation(QStandardPaths.HomeLocation)

    @staticmethod
    def app_cache_dir():
        return Cmm.local_cache_dir()

    @staticmethod
    def user_picture_dir():
        return QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)

    @staticmethod
    def user_document_dir():
        return QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

    @staticmethod
    def create_app_cache_dir():
        makedirs(Cmm.app_cache_dir(), exist_ok=True)

    # noinspection PyBroadException
    @staticmethod
    def open_external_file(url: str):
        def on_start():
            filepath = QUrl("file:///" + realpath(url))
            QDesktopServices.openUrl(filepath)

        Cmm.trace(on_start)

    @staticmethod
    def open_external_url(url: str):
        QDesktopServices.openUrl(QUrl(url))
        # def on_start():
        #     QDesktopServices.openUrl(QUrl(url))
        # Cmm.trace(on_start)

    @staticmethod
    def get_ext_name(path):
        return splitext(path)[-1]

    @staticmethod
    def is_ext_matched(path, ext):
        return Cmm.get_ext_name(path).lower() == ext.lower()

    @staticmethod
    def ext_matched_files(path, extensions):
        files = []
        if not isdir(path):
            return files
        for filename in listdir(path):
            ext = Cmm.get_ext_name(filename).lower()
            if ext not in extensions:
                continue
            files.append(filename)
        return files

    @staticmethod
    def clean_cache_dir():
        root = Cmm.app_cache_dir()
        for d in listdir(root):
            rmtree(join(root, d), ignore_errors=True)

    @staticmethod
    def random_color(alpha: int = 255):
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), alpha)


class MsgBox:
    @staticmethod
    def ask(msg_text: str, title: str = "Ask", detail: str = "", ico=QMessageBox.Information):
        return MsgBox.makeBox(msg_text, title, detail, ico, QMessageBox.Ok | QMessageBox.Cancel)

    @staticmethod
    def msg(msg_text: str, title: str = "Tips", detail: str = "", ico=QMessageBox.Information):
        return MsgBox.makeBox(msg_text, title, detail, ico, QMessageBox.Ok)

    # noinspection PyBroadException
    @staticmethod
    def makeBox(msg_text: str, title: str = "", detail: str = "", ico=QMessageBox.Information, style=QMessageBox.Ok):
        def on_start():
            msg = QMessageBox()
            msg.setIcon(ico)
            msg.setText(msg_text)
            msg.setWindowTitle(title)
            msg.setDetailedText(detail)
            msg.setStandardButtons(style)
            ret = msg.exec_()
            return ret

        return Cmm.trace(on_start)
