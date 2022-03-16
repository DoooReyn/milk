import ctypes
import traceback
from os import getenv, listdir, makedirs
from os.path import join, splitext, isdir, abspath
from pathlib import Path
from shutil import rmtree
from traceback import format_exc, print_exc

import win32api
import win32con
import win32gui
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox

from conf.settings import Settings


class Cmm:
    @staticmethod
    def local_cache_dir():
        return getenv("LOCALAPPDATA")

    @staticmethod
    def local_temp_dir():
        return getenv("TEMP")

    @staticmethod
    def user_root_dir():
        return getenv("USERPROFILE")

    @staticmethod
    def app_cache_dir():
        return join(Cmm.local_cache_dir(), Settings.Names.app)

    @staticmethod
    def user_picture_dir():
        return join(Cmm.user_root_dir(), "Pictures")

    @staticmethod
    def user_document_dir():
        return join(Cmm.user_root_dir(), "Documents")

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

    @staticmethod
    def set_wallpaper(path):
        try:
            key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
            win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "10")
            win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
            win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, abspath(path), win32con.SPIF_SENDWININICHANGE)
            win32api.RegCloseKey(key)
        except:
            traceback.print_exc()


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


class MsgBox:
    @staticmethod
    def ask(msg_text: str, title: str = "Ask", detail: str = "", ico=QMessageBox.Information):
        return MsgBox.makeBox(msg_text, title, detail, ico, QMessageBox.Ok | QMessageBox.Cancel)

    @staticmethod
    def msg(msg_text: str, title: str = "Tips", detail: str = "", ico=QMessageBox.Information):
        return MsgBox.makeBox(msg_text, title, detail, ico, QMessageBox.Ok)

    @staticmethod
    def makeBox(msg_text: str, title: str = "", detail: str = "", ico=QMessageBox.Information, style=QMessageBox.Ok):
        # noinspection PyBroadException
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
