from typing import Union

from PyQt5.QtWidgets import QWidget, QTextBrowser, QPushButton

from milk.conf import LangUI, StyleSheet, LogLevel, LogColor, signals, settings, UserKey
from .ui_base import UIBase


class MainUI(UIBase):

    def __init__(self):
        self.ui_logger: Union[QTextBrowser, None] = None
        self.ui_right_panel: Union[QWidget, None] = None
        self.ui_btn_clear: Union[QPushButton, None] = None
        self.ui_btn_trace: Union[QPushButton, None] = None
        self.ui_btn_debug: Union[QPushButton, None] = None
        self.ui_btn_info: Union[QPushButton, None] = None
        self.ui_btn_warn: Union[QPushButton, None] = None
        self.ui_btn_error: Union[QPushButton, None] = None
        self.ui_btn_fatal: Union[QPushButton, None] = None

        super(MainUI, self).__init__()

    def setup_ui(self):
        self.add_horizontal_layout(self)
        self.ui_logger = self.add_text_browser(self)
        self.ui_right_panel = self.add_widget(self)
        self.add_vertical_layout(self.ui_right_panel)
        self.ui_btn_clear = self.add_push_button(LangUI.main_ui_btn_clear, self.ui_right_panel)
        self.add_label(LangUI.main_ui_lab_log_level, self.ui_right_panel).setFixedHeight(6)
        self.ui_btn_trace = self.add_check_button(LangUI.main_ui_btn_trace, self.ui_right_panel)
        self.ui_btn_debug = self.add_check_button(LangUI.main_ui_btn_debug, self.ui_right_panel)
        self.ui_btn_info = self.add_check_button(LangUI.main_ui_btn_info, self.ui_right_panel)
        self.ui_btn_warn = self.add_check_button(LangUI.main_ui_btn_warn, self.ui_right_panel)
        self.ui_btn_error = self.add_check_button(LangUI.main_ui_btn_error, self.ui_right_panel)
        self.ui_btn_fatal = self.add_check_button(LangUI.main_ui_btn_fatal, self.ui_right_panel)

        self.ui_logger.setStyleSheet(StyleSheet.TextBrowser)

        self.ui_btn_trace.setChecked(settings.value(UserKey.Main.log_trace, True, bool))
        self.ui_btn_debug.setChecked(settings.value(UserKey.Main.log_debug, True, bool))
        self.ui_btn_info.setChecked(settings.value(UserKey.Main.log_info, True, bool))
        self.ui_btn_warn.setChecked(settings.value(UserKey.Main.log_warn, True, bool))
        self.ui_btn_error.setChecked(settings.value(UserKey.Main.log_error, True, bool))
        self.ui_btn_fatal.setChecked(settings.value(UserKey.Main.log_fatal, True, bool))

    def setup_signals(self):
        self.ui_btn_clear.clicked.connect(self.on_btn_clear)

        self.ui_btn_trace.clicked.connect(lambda state: self.on_btn_checked(self.ui_btn_trace, LogLevel.trace,
                                                                            UserKey.Main.log_trace))
        self.ui_btn_debug.clicked.connect(lambda state: self.on_btn_checked(self.ui_btn_debug, LogLevel.debug,
                                                                            UserKey.Main.log_debug))
        self.ui_btn_info.clicked.connect(lambda state: self.on_btn_checked(self.ui_btn_info, LogLevel.info,
                                                                           UserKey.Main.log_info))
        self.ui_btn_warn.clicked.connect(lambda state: self.on_btn_checked(self.ui_btn_warn, LogLevel.warn,
                                                                           UserKey.Main.log_warn))
        self.ui_btn_error.clicked.connect(lambda state: self.on_btn_checked(self.ui_btn_error, LogLevel.error,
                                                                            UserKey.Main.log_error))
        self.ui_btn_fatal.clicked.connect(lambda state: self.on_btn_checked(self.ui_btn_fatal, LogLevel.fatal,
                                                                            UserKey.Main.log_fatal))

        signals.logger_trace.connect(lambda msg: self.add_log(LogLevel.trace, msg))
        signals.logger_debug.connect(lambda msg: self.add_log(LogLevel.debug, msg))
        signals.logger_info.connect(lambda msg: self.add_log(LogLevel.info, msg))
        signals.logger_warn.connect(lambda msg: self.add_log(LogLevel.warn, msg))
        signals.logger_error.connect(lambda msg: self.add_log(LogLevel.error, msg))
        signals.logger_fatal.connect(lambda msg: self.add_log(LogLevel.fatal, msg))

    def on_btn_clear(self):
        self.ui_logger.clear()

    def on_btn_checked(self, btn: QPushButton, level: LogLevel, key: str):
        msg = LangUI.msg_enabled if btn.isChecked() else LangUI.msg_disabled
        self.add_log(level, "[{0}] {1}.".format(btn.text(), msg), True)
        settings.setValue(key, btn.isChecked())

    def is_level_valid(self, level: LogLevel):
        btn = getattr(self, 'ui_btn_' + level.name, None)
        if btn is not None:
            return btn.isChecked()
        return False

    def add_log(self, level: LogLevel, msg: str, force: bool = False):
        if force:
            msg = LogColor.get(LogLevel.info.name).format(msg.replace("\n", "<br>"))
            self.ui_logger.append(msg)
        elif self.is_level_valid(level):
            msg = LogColor.get(level.name).format(msg.replace("\n", "<br>"))
            self.ui_logger.append(msg)
