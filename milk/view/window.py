from typing import Union

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QAction, QMenuBar

from milk.cmm import Cmm
from milk.conf import Settings, Lang, LangUI, signals, UIDef
from .main_ui import MainUI
from view.wallpaper import UnsplashWallPaper
from view.about_me import AboutMe
from view.spine_atlas_extractor import SpineAtlasExtractor
from view.texture_unpacker import TextureUnpacker


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setup()
        self.set_menu()
        self.set_ui()
        self.setup_signals()

        self.windows = {}
        for item in UIDef:
            self.windows.setdefault(item.name, None)

    def setup_signals(self):
        signals.window_closed.connect(self.on_sub_window_closed)
        signals.window_switch_to_main.connect(self.on_switch_to_main)

    def on_switch_to_main(self):
        self.activateWindow()

    def on_sub_window_closed(self, win_code):
        win_def = UIDef(win_code)
        win = self.windows[win_def.name]
        if win is not None:
            self.windows[win_def.name] = None
        else:
            signals.logger_fatal.emit("{0} not closed!".format(win_def.name))

    def setup(self):
        self.resize(Settings.Sizes.ori_width, Settings.Sizes.ori_height)

        rect = QApplication.desktop().availableGeometry(0)
        x = (rect.width() - Settings.Sizes.ori_width) // 2 + Settings.Sizes.ori_off_x
        y = (rect.height() - Settings.Sizes.ori_height) // 2 + Settings.Sizes.ori_off_y
        self.setMinimumSize(Settings.Sizes.min_width, Settings.Sizes.min_height)

        self.move(x, y)

    def set_menu(self):
        menu_bar = QMenuBar()

        for menu_class in Settings.Menus.all:
            menu_name = Lang.get(menu_class.Name) or menu_class.Name
            menu = QMenu(menu_name, self)
            for action in menu_class.Actions:
                name = action.get("name")
                name = Lang.get(name) or name
                hotkey = action.get("hotkey")
                icon = action.get("icon")
                trigger = action.get("trigger")
                act = QAction(name, menu)
                if trigger is not None:
                    if getattr(self, trigger, None) is not None:
                        act.triggered.connect(getattr(self, trigger))
                    else:
                        act.triggered.connect(lambda *args, m=menu_name, n=name: self.on_bind_not_implemented(m, n))
                else:
                    act.triggered.connect(lambda *args, m=menu_name, n=name: self.on_bind_not_implemented(m, n))
                if hotkey is not None:
                    act.setShortcut(hotkey)
                if icon is not None:
                    act.setIcon(QIcon(icon))
                menu.addAction(act)
            menu_bar.addMenu(menu)

        self.setMenuBar(menu_bar)

    def set_ui(self):
        self.setCentralWidget(MainUI())

    # noinspection PyMethodMayBeStatic
    def on_bind_not_implemented(self, menu, name):
        signals.logger_warn.emit(LangUI.msg_not_implemented.format(menu, name))

    @staticmethod
    def on_menu_open_cache():
        Cmm.open_external_file(Cmm.app_cache_dir())

    # noinspection PyMethodMayBeStatic
    def on_menu_clear_cache(self):
        Cmm.clean_cache_dir()
        signals.logger_info.emit(LangUI.msg_clear_cache_ok)

    @staticmethod
    def on_menu_open_about_qt():
        QApplication.aboutQt()

    def on_menu_open_about_me(self):
        self.open_menu(UIDef.FileAboutMe, AboutMe)

    @staticmethod
    def on_menu_exit_app():
        QApplication.exit(0)

    def open_menu(self, ui: UIDef, class_obj):
        win = self.windows[ui.name]
        if win is not None:
            win.activateWindow()
            return
        self.windows[ui.name] = class_obj()
        self.windows[ui.name].show()

    def on_menu_image_split(self):
        # self.open_menu(UIDef.ImageSplit, UnsplashWallPaper)
        pass

    def on_menu_image_compress(self):
        # self.open_menu(UIDef.ImageCompress, UnsplashWallPaper)
        pass

    def on_menu_image_texture_packer(self):
        # self.open_menu(UIDef.ImageTexturePacker, UnsplashWallPaper)
        pass

    def on_menu_image_texture_unpacker(self):
        self.open_menu(UIDef.ImageTextureUnpacker, TextureUnpacker)

    def on_menu_image_spine_atlas_extractor(self):
        self.open_menu(UIDef.ImageSpineAtlasExtractor, SpineAtlasExtractor)

    def on_menu_tools_random_wallpaper(self):
        self.open_menu(UIDef.ToolsWallpaper, UnsplashWallPaper)

    def closeEvent(self, evt):
        for key, win in self.windows.items():
            if win is not None:
                win.close()
