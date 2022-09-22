from os import remove
from os.path import exists, join
from typing import Optional

from PyQt5.QtCore import QFile, QFileInfo, QIODevice, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWidgets import QMessageBox, QWidget
from unsplash.api import Api
from unsplash.auth import Auth

from conf import UIDef
from milk.cmm import Cmm
from milk.conf import LangUI, settings, signals, UserKey
from milk.gui import GUI


class _View(GUI.View):
    def __init__(self, parent: QWidget = None):
        super(_View, self).__init__(parent)

        # creat widgets
        self.ui_lab_public_key = GUI.create_label(LangUI.wallpaper_ui_lab_public_key)
        self.ui_lab_private_key = GUI.create_label(LangUI.wallpaper_ui_lab_private_key)
        self.ui_lab_redirect_uri = GUI.create_label(LangUI.wallpaper_ui_lab_redirect_uri)
        self.ui_edit_public_key = GUI.create_line_edit(placeholder=LangUI.wallpaper_ui_public_key)
        self.ui_edit_private_key = GUI.create_line_edit(placeholder=LangUI.wallpaper_ui_private_key)
        self.ui_edit_redirect_uri = GUI.create_line_edit(placeholder=LangUI.wallpaper_ui_redirect_uri)
        self.ui_lab_save_at = GUI.create_label(LangUI.wallpaper_ui_btn_save)
        self.ui_edit_save_at = GUI.create_line_edit(readonly=True, placeholder=LangUI.wallpaper_ui_save_at)
        self.ui_act_save_at = GUI.set_folder_action_for_line_edit(self.ui_edit_save_at)
        self.ui_btn_random = GUI.create_push_btn(LangUI.wallpaper_ui_btn_random)
        self.ui_btn_setup = GUI.create_push_btn(LangUI.wallpaper_ui_btn_download)
        self.ui_btn_dislike = GUI.create_push_btn(LangUI.wallpaper_ui_btn_dislike)
        self.ui_progress_bar = GUI.create_progress_bar()
        self.ui_pixmap = GUI.create_label('')
        self.ui_btn_setup.setEnabled(False)
        self.ui_btn_dislike.setEnabled(False)
        self.ui_progress_bar.hide()
        self.ui_pixmap.hide()

        # layout widgets
        self.ui_layout = GUI.create_grid_layout(self)
        self.ui_layout.setAlignment(Qt.AlignTop)
        GUI.add_grid_in_rows(self.ui_layout, (
            (
                GUI.GridItem(self.ui_lab_public_key, 0, 1),
                GUI.GridItem(self.ui_edit_public_key, 1, 5)
            ),
            (
                GUI.GridItem(self.ui_lab_private_key, 0, 1),
                GUI.GridItem(self.ui_edit_private_key, 1, 5)
            ),
            (
                GUI.GridItem(self.ui_lab_redirect_uri, 0, 1),
                GUI.GridItem(self.ui_edit_redirect_uri, 1, 5)
            ),
            (
                GUI.GridItem(self.ui_lab_save_at, 0, 1),
                GUI.GridItem(self.ui_edit_save_at, 1, 5)
            ),
            (
                GUI.GridItem(self.ui_btn_random, 0, 1),
                GUI.GridItem(self.ui_btn_setup, 1, 1),
                GUI.GridItem(self.ui_btn_dislike, 2, 1),
                GUI.GridItem(self.ui_progress_bar, 3, 5),
            ),
            (
                GUI.GridItem(self.ui_pixmap, 0, 6),
            ),
        ))
        GUI.set_grid_span(self.ui_layout, [], [4, 5])


class WallPaperView(_View):
    def __init__(self, parent: QWidget = None):
        super(WallPaperView, self).__init__(parent)

        self.screen_width, self.screen_height = GUI.get_screensize()
        self.network_manager = QNetworkAccessManager()
        self.file_save_at: Optional[str] = None
        self.network_reply: Optional[QNetworkReply] = None
        self.temp_file_handler: Optional[QFile] = None
        self.file_link: Optional[QUrl] = None

        self.setWindowTitle(LangUI.wallpaper_title)

        self.setup_window_code(UIDef.ToolsWallpaper.value)
        self.setup_resize_keys(UserKey.Wallpaper.window_width, UserKey.Wallpaper.window_height)
        self.setMinimumSize(500, 184)
        self.setup_ui_signals()
        self.setup_preferences()

    def setup_ui_signals(self):
        self.ui_edit_public_key.returnPressed.connect(self.on_sync_public_key)
        self.ui_edit_public_key.editingFinished.connect(self.on_sync_public_key)
        self.ui_edit_private_key.returnPressed.connect(self.on_sync_private_key)
        self.ui_edit_private_key.editingFinished.connect(self.on_sync_private_key)
        self.ui_edit_redirect_uri.returnPressed.connect(self.on_sync_redirect_uri)
        self.ui_edit_redirect_uri.editingFinished.connect(self.on_sync_redirect_uri)
        self.ui_act_save_at.triggered.connect(self.on_choose_save_dir)
        self.ui_btn_random.clicked.connect(self.on_random_wallpaper)
        self.ui_btn_setup.clicked.connect(self.on_set_wallpaper)
        self.ui_btn_dislike.clicked.connect(self.on_abandon_wallpaper)

    def setup_preferences(self):
        self.ui_edit_public_key.setText(self.public_key())
        self.ui_edit_private_key.setText(self.private_key())
        self.ui_edit_redirect_uri.setText(self.redirect_uri())
        self.ui_edit_save_at.setText(self.save_at())

    @staticmethod
    def public_key():
        return settings.value(UserKey.Wallpaper.public_key, "", str)

    @staticmethod
    def private_key():
        return settings.value(UserKey.Wallpaper.private_key, "", str)

    @staticmethod
    def redirect_uri():
        return settings.value(UserKey.Wallpaper.redirect_uri, "", str)

    @staticmethod
    def save_at():
        return settings.value(UserKey.Wallpaper.save_at, Cmm.user_picture_dir(), str)

    def on_random_wallpaper(self):
        public_key = self.ui_edit_public_key.text()
        if len(public_key) < 10:
            signals.logger_error.emit(LangUI.msg_invalid_public_key)
            signals.window_switch_to_main.emit()
            return

        private_key = self.ui_edit_private_key.text()
        if len(private_key) < 10:
            signals.logger_error.emit(LangUI.msg_invalid_private_key)
            signals.window_switch_to_main.emit()
            return

        redirect_ui = self.ui_edit_redirect_uri.text()
        if len(redirect_ui) < 10:
            signals.logger_error.emit(LangUI.msg_invalid_redirect_ui)
            signals.window_switch_to_main.emit()
            return

        if not exists(self.ui_edit_save_at.text()):
            signals.logger_error.emit(LangUI.wallpaper_ui_save_at)
            signals.window_switch_to_main.emit()
            return

        self.ui_btn_random.setEnabled(False)
        photo = None
        try:
            api = Api(Auth(public_key, private_key, redirect_ui))
            photos = api.photo.random(count=1, w=self.screen_width, h=self.screen_height, orientation="landscape")
            if len(photos) <= 0:
                signals.logger_error.emit(LangUI.msg_request_wallpaper_failed)
            photo = photos[0]
        except Exception as e:
            signals.logger_error.emit(str(e))
            self.ui_btn_random.setEnabled(True)
        if photo and photo.urls:
            url = photo.urls.full or photo.urls.regular or photo.urls.raw
            signals.logger_info.emit(LangUI.wallpaper_downloading.format(url))
            self.start_download(QUrl(url))

    def on_set_wallpaper(self):
        GUI.set_wallpaper(self.file_save_at)

    def on_abandon_wallpaper(self):
        remove(self.file_save_at)
        self.on_random_wallpaper()

    def start_download(self, url):
        self.file_link = url
        file_info = QFileInfo(url.path())
        file_name = join(self.ui_edit_save_at.text(), file_info.fileName() + '.jpg')
        self.file_save_at = file_name
        self.temp_file_handler = QFile(file_name)
        if not self.temp_file_handler.open(QIODevice.WriteOnly):
            title = LangUI.wallpaper_ui_msg_title
            detail = LangUI.msg_can_not_save_file.format(file_name, self.temp_file_handler.errorString())
            QMessageBox.information(self, title, detail)
            self.temp_file_handler = None
            return

        self.ui_btn_random.setEnabled(False)
        self.ui_btn_setup.setEnabled(False)
        self.ui_btn_dislike.setEnabled(False)
        self.network_reply = self.network_manager.get(QNetworkRequest(url))
        self.network_reply.finished.connect(self.on_http_finished)
        self.network_reply.readyRead.connect(self.on_http_ready_read)
        self.network_reply.downloadProgress.connect(self.on_update_data_read_progress)

    def on_http_finished(self):
        self.ui_btn_random.setEnabled(True)
        self.ui_btn_dislike.setEnabled(True)
        self.temp_file_handler.flush()
        self.temp_file_handler.close()

        target = self.network_reply.attribute(QNetworkRequest.RedirectionTargetAttribute)

        if self.network_reply.error():
            title = LangUI.wallpaper_ui_msg_title
            detail = LangUI.msg_download_wallpaper_failed.format(self.network_reply.errorString())
            QMessageBox.information(self, title, detail)
            self.temp_file_handler.remove()
            self.temp_file_handler = None
            self.network_reply.deleteLater()
            self.network_reply = None
            return
        elif target is not None:
            new_url = self.file_link.resolved(target)
            self.temp_file_handler.remove()
            self.network_reply.deleteLater()
            self.network_reply = None
            self.temp_file_handler.open(QIODevice.WriteOnly)
            self.temp_file_handler.resize(0)
            self.start_download(new_url)
            return
        else:
            width = self.screen_width // 2
            height = self.screen_height // 2
            self.ui_pixmap.setScaledContents(True)
            self.ui_pixmap.resize(width, height)
            self.ui_pixmap.setPixmap(QPixmap(self.file_save_at))
            self.ui_btn_setup.setEnabled(True)
            self.ui_btn_dislike.setEnabled(True)
            self.ui_pixmap.show()
            self.ui_progress_bar.hide()
            self.resize(width + 20, height + 194)

        self.network_reply.deleteLater()
        self.network_reply = None
        self.temp_file_handler = None

    def on_http_ready_read(self):
        if self.temp_file_handler is not None:
            self.temp_file_handler.write(self.network_reply.readAll())

    def on_update_data_read_progress(self, bytes_read, total_bytes):
        self.ui_progress_bar.show()
        self.ui_progress_bar.setMaximum(total_bytes)
        self.ui_progress_bar.setValue(bytes_read)

    def on_choose_save_dir(self):
        dir_choose = GUI.dialog_for_directory_selection(self, LangUI.wallpaper_ui_save_at, self.ui_edit_save_at.text())
        if dir_choose is not None:
            self.ui_edit_save_at.setText(dir_choose)
            self.on_sync_save_at()

    def on_sync_public_key(self):
        settings.setValue(UserKey.Wallpaper.public_key, self.ui_edit_public_key.text())

    def on_sync_private_key(self):
        settings.setValue(UserKey.Wallpaper.private_key, self.ui_edit_private_key.text())

    def on_sync_redirect_uri(self):
        settings.setValue(UserKey.Wallpaper.redirect_uri, self.ui_edit_redirect_uri.text())

    def on_sync_save_at(self):
        settings.setValue(UserKey.Wallpaper.save_at, self.ui_edit_save_at.text())
