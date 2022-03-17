from enum import Enum, unique


@unique
class LogLevel(Enum):
    trace = 1
    debug = 2
    info = 3
    warn = 4
    error = 5
    fatal = 6


LogColor = {
    "trace": '<span style="color:#f5f6fa; font-size:14px;">{0}</span>',
    "debug": '<span style="color:#00a8ff; font-size:14px;">{0}</span>',
    "info": '<span style="color:#1eff1e; font-size:14px;">{0}</span>',
    "warn": '<span style="color:#ffee6f; font-size:14px;">{0}</span>',
    "error": '<span style="color:#e55039; font-size:14px;">{0}</span>',
    "fatal": '<span style="background-color:#c8161d; color:#e8eaf6; font-size:14px;">{0}</span>',
}
