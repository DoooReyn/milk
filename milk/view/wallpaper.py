from os.path import exists, join
from typing import Union

from PyQt5.QtCore import QFileInfo, QFile, QIODevice, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager
from PyQt5.QtWidgets import QLineEdit, QPushButton, QWidget, QProgressBar, QFileDialog, QLabel, QMessageBox
from unsplash.api import Api
from unsplash.auth import Auth

from milk.cmm import Cmm
from milk.conf import settings, UserKey, signals, UIDef, LangUI
from milk.view.ui_base import UIBase


class UnsplashWallPaper(UIBase):

    def __init__(self, parent: QWidget = None):
        self.screen_size = Cmm.get_screensize()
        self.ui_bar: Union[QProgressBar, None] = None
        self.ui_public_key: Union[QLineEdit, None] = None
        self.ui_private_key: Union[QLineEdit, None] = None
        self.ui_redirect_uri: Union[QLineEdit, None] = None
        self.ui_save_at: Union[QLineEdit, None] = None
        self.ui_btn_random: Union[QPushButton, None] = None
        self.ui_btn_save: Union[QPushButton, None] = None
        self.ui_btn_download: Union[QPushButton, None] = None
        self.ui_lab_image: Union[QLabel, None] = None
        self.nam = QNetworkAccessManager()
        self.reply: Union[QNetworkReply, None] = None
        self.out_file: Union[QFile, None] = None
        self.url: Union[QUrl, None] = None
        self.file_name: Union[str, None] = None

        super().__init__(parent)

    def setup_ui(self):
        self.add_vertical_layout(self)

        ui_line_1 = self.add_widget(self)
        self.add_horizontal_layout(ui_line_1)
        self.add_label(LangUI.wallpaper_ui_lab_public_key, ui_line_1).setFixedWidth(120)
        self.ui_public_key = self.add_line_edit(LangUI.wallpaper_ui_public_key, ui_line_1)

        ui_line_2 = self.add_widget(self)
        self.add_horizontal_layout(ui_line_2)
        self.add_label(LangUI.wallpaper_ui_lab_private_key, ui_line_2).setFixedWidth(120)
        self.ui_private_key = self.add_line_edit(LangUI.wallpaper_ui_private_key, ui_line_2)

        ui_line_3 = self.add_widget(self)
        self.add_horizontal_layout(ui_line_3)
        self.add_label(LangUI.wallpaper_ui_lab_redirect_uri, ui_line_3).setFixedWidth(120)
        self.ui_redirect_uri = self.add_line_edit(LangUI.wallpaper_ui_redirect_uri, ui_line_3)

        ui_line_4 = self.add_widget(self)
        self.add_horizontal_layout(ui_line_4)
        self.ui_btn_save = self.add_push_button(LangUI.wallpaper_ui_btn_save, ui_line_4)
        self.ui_save_at = self.add_line_edit(LangUI.wallpaper_ui_save_at, ui_line_4)
        self.ui_btn_save.setFixedWidth(120)

        ui_line_5 = self.add_widget(self)
        self.add_horizontal_layout(ui_line_5)
        self.ui_btn_random = self.add_push_button(LangUI.wallpaper_ui_btn_random, ui_line_5)
        self.ui_btn_download = self.add_push_button(LangUI.wallpaper_ui_btn_download, ui_line_5)
        self.ui_bar = self.add_progress_bar(ui_line_5)

        self.ui_lab_image = self.add_label("", self)

        self.ui_public_key.setText(settings.value(UserKey.Wallpaper.public_key, ""))
        self.ui_private_key.setText(settings.value(UserKey.Wallpaper.private_key, ""))
        self.ui_redirect_uri.setText(settings.value(UserKey.Wallpaper.redirect_uri, ""))
        self.ui_save_at.setText(settings.value(UserKey.Wallpaper.save_at, Cmm.user_picture_dir()))
        self.ui_save_at.setReadOnly(True)
        self.ui_bar.hide()
        # self.ui_btn_download.hide()

    def setup_signals(self):
        self.ui_public_key.returnPressed.connect(self.on_sync_public_key)
        self.ui_public_key.editingFinished.connect(self.on_sync_public_key)
        self.ui_private_key.returnPressed.connect(self.on_sync_private_key)
        self.ui_private_key.editingFinished.connect(self.on_sync_private_key)
        self.ui_redirect_uri.returnPressed.connect(self.on_sync_redirect_uri)
        self.ui_redirect_uri.editingFinished.connect(self.on_sync_redirect_uri)
        self.ui_btn_random.clicked.connect(self.on_random)
        self.ui_btn_download.clicked.connect(self.on_set_wallpaper)
        self.ui_btn_save.clicked.connect(self.on_choose_save_dir)

    def on_random(self):
        public_key = self.ui_public_key.text()
        if len(public_key) < 10:
            signals.logger_error.emit(LangUI.msg_invalid_public_key)
            signals.window_switch_to_main.emit()
            return

        private_key = self.ui_private_key.text()
        if len(private_key) < 10:
            signals.logger_error.emit(LangUI.msg_invalid_private_key)
            signals.window_switch_to_main.emit()
            return

        redirect_ui = self.ui_redirect_uri.text()
        if len(redirect_ui) < 10:
            signals.logger_error.emit(LangUI.msg_invalid_redirect_ui)
            signals.window_switch_to_main.emit()
            return

        if not exists(self.ui_save_at.text()):
            signals.logger_error.emit(LangUI.wallpaper_ui_save_at)
            signals.window_switch_to_main.emit()
            return

        photo = None
        try:
            api = Api(Auth(public_key, private_key, redirect_ui))
            photos = api.photo.random(count=1, w=self.screen_size[0], h=self.screen_size[1], orientation="landscape")
            if len(photos) <= 0:
                signals.logger_error.emit(LangUI.msg_request_wallpaper_failed)

            photo = photos[0]
        except Exception as e:
            signals.logger_error.emit(str(e))

        if photo and photo.urls:
            url = photo.urls.full or photo.urls.regular or photo.urls.raw
            signals.logger_info.emit(url)
            self.start_download(QUrl(url))

    def on_set_wallpaper(self):
        Cmm.set_wallpaper(self.file_name)

    def start_download(self, url):
        self.url = url
        file_info = QFileInfo(url.path())
        file_name = join(self.ui_save_at.text(), file_info.fileName() + '.jpg')
        self.file_name = file_name
        print("save at: ", file_name)

        self.out_file = QFile(file_name)
        if not self.out_file.open(QIODevice.WriteOnly):
            QMessageBox.information(self, LangUI.wallpaper_ui_msg_title,
                                    LangUI.msg_can_not_save_file.format(file_name, out_file.errorString()))
            self.out_file = None
            return

        self.ui_btn_random.setEnabled(False)
        self.ui_btn_download.hide()
        self.reply = self.nam.get(QNetworkRequest(url))
        self.reply.finished.connect(self.on_http_finished)
        self.reply.readyRead.connect(self.on_http_ready_read)
        self.reply.downloadProgress.connect(self.on_update_data_read_progress)

    def on_http_finished(self):
        self.ui_btn_random.setEnabled(True)
        self.out_file.flush()
        self.out_file.close()

        target = self.reply.attribute(QNetworkRequest.RedirectionTargetAttribute)

        if self.reply.error():
            self.out_file.remove()
            self.out_file = None
            self.reply.deleteLater()
            self.reply = None
            QMessageBox.information(self, LangUI.wallpaper_ui_msg_title,
                                    LangUI.msg_download_wallpaper_failed.format(self.reply.errorString()))
            return
        elif target is not None:
            self.out_file.remove()
            new_url = self.url.resolved(target)
            self.reply.deleteLater()
            self.reply = None
            self.out_file.open(QIODevice.WriteOnly)
            self.out_file.resize(0)
            self.start_download(new_url)
            return
        else:
            self.ui_lab_image.setScaledContents(True)
            self.ui_lab_image.setFixedSize(self.screen_size[0] // 2, self.screen_size[1] // 2)
            self.ui_lab_image.setPixmap(QPixmap(self.file_name))
            self.ui_btn_download.show()
            self.ui_bar.hide()

        self.reply.deleteLater()
        self.reply = None
        self.out_file = None

    def on_http_ready_read(self):
        if self.out_file is not None:
            self.out_file.write(self.reply.readAll())

    def on_update_data_read_progress(self, bytes_read, total_bytes):
        self.ui_bar.show()
        self.ui_bar.setMaximum(total_bytes)
        self.ui_bar.setValue(bytes_read)

    def on_choose_save_dir(self):
        dir_choose = QFileDialog.getExistingDirectory(self, LangUI.wallpaper_ui_save_at, self.ui_save_at.text())
        if len(dir_choose) > 0:
            self.ui_save_at.setText(dir_choose)
            settings.setValue(UserKey.Wallpaper.save_at, dir_choose)

    def on_sync_public_key(self):
        settings.setValue(UserKey.Wallpaper.public_key, self.ui_public_key.text())

    def on_sync_private_key(self):
        settings.setValue(UserKey.Wallpaper.private_key, self.ui_private_key.text())

    def on_sync_redirect_uri(self):
        settings.setValue(UserKey.Wallpaper.redirect_uri, self.ui_redirect_uri.text())

    def on_sync_save_at(self):
        settings.setValue(UserKey.Wallpaper.save_at, self.ui_save_at.text())

    def closeEvent(self, event):
        event.accept()
        signals.window_closed.emit(UIDef.ToolsWallpaper.value)
