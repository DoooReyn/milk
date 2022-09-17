from PyQt5.QtWidgets import QApplication, QMainWindow

from milk.cmm import Cmm
from milk.conf import LangUI, Settings, signals, UIDef
from milk.gui import GUI
from milk.view.about_me import AboutMe
from milk.view.spine_atlas_extractor import SpineAtlasExtractor
from milk.view.TestView import TestView
from milk.view.translate.translate import TranslateView
from milk.view.texture_unpacker import TextureUnpacker
from milk.view.wallpaper import UnsplashWallPaper
from milk.view.weread import WeRead
from .main_ui import MainUI


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setup()
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

    def on_sub_window_closed(self, win_code: int):
        win_def = UIDef(win_code)
        win = self.windows[win_def.name]
        if win is not None:
            self.windows[win_def.name] = None
            signals.logger_debug.emit('{0} 关闭.'.format(win_def.name))
        else:
            signals.logger_fatal.emit("{0} 未正确关闭!".format(win_def.name))

    def setup(self):
        self.resize(Settings.Sizes.ori_width, Settings.Sizes.ori_height)

        rect = QApplication.desktop().availableGeometry(0)
        x = (rect.width() - Settings.Sizes.ori_width) // 2 + Settings.Sizes.ori_off_x
        y = (rect.height() - Settings.Sizes.ori_height) // 2 + Settings.Sizes.ori_off_y
        self.setMinimumSize(Settings.Sizes.min_width, Settings.Sizes.min_height)

        self.move(x, y)

    def set_ui(self):
        self.setCentralWidget(MainUI())
        self.setMenuBar(GUI.create_menu_bar(Settings.Menus, self))

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

    def on_menu_tools_weread(self):
        self.open_menu(UIDef.ToolsWeRead, WeRead)

    def on_menu_test_view(self):
        self.open_menu(UIDef.FileTest, TestView)

    def on_menu_tools_translate(self):
        self.open_menu(UIDef.ToolsTranslate, TranslateView)

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

    @staticmethod
    def open_api_document(url: str):
        Cmm.open_external_url(url)

    @staticmethod
    def on_menu_doc_typescript():
        Window.open_api_document("https://www.typescriptlang.org/docs/")

    @staticmethod
    def on_menu_doc_qt():
        Window.open_api_document("https://doc.qt.io/qtforpython/")

    @staticmethod
    def on_menu_doc_cocos2dx():
        Window.open_api_document("https://docs.cocos2d-x.org/api-ref/index.html")

    @staticmethod
    def on_menu_doc_cocos_creator():
        Window.open_api_document("https://docs.cocos.com/creator/manual/zh/")

    @staticmethod
    def on_menu_doc_lua():
        Window.open_api_document("https://www.lua.org/docs.html")

    @staticmethod
    def on_menu_doc_python():
        Window.open_api_document("https://docs.python.org/zh-cn/3.10/reference/index.html")

    @staticmethod
    def on_menu_doc_html():
        Window.open_api_document("https://developer.mozilla.org/zh-CN/docs/Web/HTML")

    @staticmethod
    def on_menu_doc_css():
        Window.open_api_document("https://developer.mozilla.org/zh-CN/docs/Web/CSS")

    @staticmethod
    def on_menu_doc_javascript():
        Window.open_api_document("https://developer.mozilla.org/zh-CN/docs/Learn/JavaScript")

    @staticmethod
    def on_menu_doc_canvas():
        Window.open_api_document("https://developer.mozilla.org/zh-CN/docs/Web/API/Canvas_API/Tutorial")

    @staticmethod
    def on_menu_doc_go():
        Window.open_api_document("https://go.dev/doc/")

    def closeEvent(self, evt):
        for key, win in self.windows.items():
            if win is not None:
                win.close()
