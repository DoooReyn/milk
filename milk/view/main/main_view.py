from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtCore import Qt

from milk.conf import LangUI, LogColor, LogLevel, settings, signals, StyleSheet, UserKey
from milk.gui import GUI
from milk.view.ui_base import UIBase


class _View(UIBase):
    def __init__(self):
        super(_View, self).__init__()

        # create widgets
        self.ui_logger = GUI.create_text_browser()
        self.ui_logger.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.ui_logger.setStyleSheet(StyleSheet.TextBrowser)
        self.ui_right_panel = QWidget()
        self.ui_btn_clear = GUI.create_push_btn(LangUI.main_ui_btn_clear)
        self.ui_lab_level = GUI.create_label(LangUI.main_ui_lab_log_level)
        self.ui_lab_level.setFixedHeight(6)
        self.ui_btn_trace = GUI.create_check_button(LangUI.main_ui_btn_trace)
        self.ui_btn_debug = GUI.create_check_button(LangUI.main_ui_btn_debug)
        self.ui_btn_info = GUI.create_check_button(LangUI.main_ui_btn_info)
        self.ui_btn_warn = GUI.create_check_button(LangUI.main_ui_btn_warn)
        self.ui_btn_error = GUI.create_check_button(LangUI.main_ui_btn_error)
        self.ui_btn_fatal = GUI.create_check_button(LangUI.main_ui_btn_fatal)

        # layout widgets
        self.ui_layout = GUI.create_horizontal_layout(self)
        self.ui_layout.addWidget(self.ui_logger)
        self.ui_layout.addWidget(self.ui_right_panel)
        self.ui_right_layout = GUI.create_vertical_layout(self.ui_right_panel)
        self.ui_right_layout.setAlignment(Qt.AlignTop)
        self.ui_right_layout.addWidget(self.ui_btn_clear)
        self.ui_right_layout.addWidget(self.ui_lab_level)
        self.ui_right_layout.addWidget(self.ui_btn_trace)
        self.ui_right_layout.addWidget(self.ui_btn_debug)
        self.ui_right_layout.addWidget(self.ui_btn_info)
        self.ui_right_layout.addWidget(self.ui_btn_warn)
        self.ui_right_layout.addWidget(self.ui_btn_error)
        self.ui_right_layout.addWidget(self.ui_btn_fatal)


class MainView(_View):
    def __init__(self):
        super(MainView, self).__init__()

        self.setup_ui_status()
        self.setup_ui_signals()

    def setup_ui_status(self):
        self.ui_btn_trace.setChecked(settings.value(UserKey.Main.log_trace, True, bool))
        self.ui_btn_debug.setChecked(settings.value(UserKey.Main.log_debug, True, bool))
        self.ui_btn_info.setChecked(settings.value(UserKey.Main.log_info, True, bool))
        self.ui_btn_warn.setChecked(settings.value(UserKey.Main.log_warn, True, bool))
        self.ui_btn_error.setChecked(settings.value(UserKey.Main.log_error, True, bool))
        self.ui_btn_fatal.setChecked(settings.value(UserKey.Main.log_fatal, True, bool))

    def setup_ui_signals(self):
        self.ui_btn_clear.clicked.connect(lambda: self.ui_logger.clear())
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
