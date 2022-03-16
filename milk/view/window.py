from typing import Union

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QAction, QMenuBar

from milk.cmm import Cmm
from milk.conf import Settings, Lang, LangUI, signals, UIDef
from .main_ui import MainUI
from view.wallpaper import UnsplashWallPaper
from view.about_me import AboutMe


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setup()
        self.set_menu()
        self.set_ui()
        self.setup_signals()

        self.win_wallpaper: Union[UnsplashWallPaper, None] = None
        self.win_about_me: Union[AboutMe, None] = None

    def setup_signals(self):
        signals.window_closed.connect(self.on_sub_window_closed)
        signals.window_switch_to_main.connect(self.on_switch_to_main)

    def on_switch_to_main(self):
        self.activateWindow()

    def on_sub_window_closed(self, win):
        code = UIDef(win)
        if code == UIDef.ToolsWallpaper:
            self.win_wallpaper = None
        if code == UIDef.FileAboutMe:
            self.win_about_me = None

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
        if self.win_about_me is not None:
            self.win_about_me.activateWindow()
            return
        self.win_about_me = AboutMe()
        self.win_about_me.show()

    @staticmethod
    def on_menu_exit_app():
        QApplication.exit(0)

    def on_menu_image_split(self):
        if self.win_wallpaper is not None:
            self.win_wallpaper.activateWindow()
            return
        self.win_wallpaper = UnsplashWallPaper()
        self.win_wallpaper.show()

    def on_menu_image_compress(self):
        if self.win_wallpaper is not None:
            self.win_wallpaper.activateWindow()
            return
        self.win_wallpaper = UnsplashWallPaper()
        self.win_wallpaper.show()

    def on_menu_image_texture_packer(self):
        if self.win_wallpaper is not None:
            self.win_wallpaper.activateWindow()
            return
        self.win_wallpaper = UnsplashWallPaper()
        self.win_wallpaper.show()

    def on_menu_tools_random_wallpaper(self):
        if self.win_wallpaper is not None:
            self.win_wallpaper.activateWindow()
            return
        self.win_wallpaper = UnsplashWallPaper()
        self.win_wallpaper.show()

    def closeEvent(self, evt):
        if self.win_wallpaper:
            self.win_wallpaper.close()
        if self.win_about_me:
            self.win_about_me.close()
