from PyQt5.QtCore import QObject, pyqtSignal as QSignal


class Signals(QObject):
    # 输出日志
    logger_trace = QSignal(str)
    logger_debug = QSignal(str)
    logger_info = QSignal(str)
    logger_warn = QSignal(str)
    logger_error = QSignal(str)
    logger_fatal = QSignal(str)

    # windows
    window_closed = QSignal(int)
    window_switch_to_main = QSignal()
