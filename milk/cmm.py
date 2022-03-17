import ctypes
import sys
from os import listdir, makedirs
from os.path import join, splitext, isdir, abspath, realpath, dirname
from pathlib import Path
from shutil import rmtree
from threading import Thread, Event
from traceback import format_exc, print_exc
from PIL import Image

import win32api
import win32con
from PyQt5.QtCore import QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox
from win32gui import SystemParametersInfo

from conf.settings import Settings


class StoppableThread(Thread):
    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class TraceBack:
    def __init__(self, clear=False):
        date = datetime.date(datetime.now())
        self.__save_at = Path(Cmm.app_cache_dir()).joinpath(
            f"{date}.log")
        if clear:
            self.clear()
        self.start()

    def clear(self):
        with open(self.__save_at, "wt", encoding="utf-8") as fb:
            fb.write("")

    def start(self):
        equal = "=" * 40
        self.save(f"\n{equal}start{equal}\n")

    def trace_back(self):
        stack = format_exc(limit=10)
        date = datetime.now()
        stack = f"{date}\n{stack}\n"
        self.save(stack)

    def save(self, text: str):
        with open(self.__save_at, "at", encoding="utf-8") as fb:
            fb.write(text)


class Cmm:
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
        return join(Cmm.local_cache_dir(), Settings.Names.app)

    @staticmethod
    def user_picture_dir():
        return QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)

    @staticmethod
    def user_document_dir():
        return QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

    @staticmethod
    def create_app_cache_dir():
        makedirs(Cmm.app_cache_dir(), exist_ok=True)

    @staticmethod
    def open_external_file(url: str):
        QDesktopServices.openUrl(QUrl("file:///" + url))

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

    # noinspection PyBroadException
    @staticmethod
    def get_screensize(multiplier=1):
        try:
            user32 = ctypes.windll.user32
            screensize = (user32.GetSystemMetrics(78) * multiplier, user32.GetSystemMetrics(79) * multiplier)
            print(f"\r[+] Status: Detected virtual monitor size {screensize[0]}x{screensize[1]}.", end="")
            if multiplier > 1:
                print(f"\r[+] Status: Multiplying to {screensize} for better quality.", end="")
            return screensize
        except:
            print(f"\r[-] Status: Encountered some problems while detecting your display size.", end="")
            print_exc()

    # noinspection PyBroadException
    @staticmethod
    def set_wallpaper(path):
        try:
            key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
            win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
            win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
            SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, abspath(path), win32con.SPIF_SENDWININICHANGE)
            win32api.RegCloseKey(key)
        except Exception:
            TraceBack().trace_back()


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
        try:
            msg = QMessageBox()
            msg.setIcon(ico)
            msg.setText(msg_text)
            msg.setWindowTitle(title)
            msg.setDetailedText(detail)
            msg.setStandardButtons(style)
            ret = msg.exec_()
            return ret
        except Exception:
            TraceBack().trace_back()
