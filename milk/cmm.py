import random
import sys
from os import listdir, makedirs
from os.path import dirname, isdir, join, realpath, splitext
from shutil import rmtree
from threading import Event, Thread
from traceback import format_exc, print_exc

import cchardet
from PyQt5.QtCore import QStandardPaths, QUrl
from PyQt5.QtGui import QColor, QDesktopServices

try:
    from collections import Iterable
except (AttributeError, ImportError):
    from collections.abc import Iterable


class Cmm:
    Iterable = Iterable

    class StoppableThread(Thread):
        def __init__(self, **kwargs):
            super(Cmm.StoppableThread, self).__init__(**kwargs)
            self._stop_event = Event()

        def stop(self):
            self._stop_event.set()

        def stopped(self):
            return self._stop_event.is_set()

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

    @staticmethod
    def get_file_encoding(filepath: str):
        with open(filepath, 'rb') as f:
            encoding = cchardet.detect(f.read())['encoding'].lower()
            return Cmm.format_file_encoding(encoding)

    @staticmethod
    def format_file_encoding(encoding: str):
        encoding = encoding.lower()
        if encoding in ["iso-8859-1", "ascii"]:
            return "utf-8"
        elif encoding == "euc-tw":
            return "gbk"
        return encoding

    @staticmethod
    def convert_file_encoding_to_utf8(filepath: str):
        with open(filepath, 'rb+') as f:
            content = f.read()
            encoding = cchardet.detect(content)['encoding']
            result = Cmm.format_file_encoding(encoding)
            try:
                if result != 'utf-8':
                    content = content.decode(encoding).encode('utf8')
                    f.seek(0)
                    f.write(content)
                return result, True
            except (UnicodeDecodeError, UnicodeEncodeError) as e:
                print(e)
                return result, False

    @staticmethod
    def is_utf8_file(filepath: str):
        return Cmm.get_file_encoding(filepath) in ['utf-8', 'utf8']
