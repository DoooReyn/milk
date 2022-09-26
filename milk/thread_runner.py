from threading import Event, Thread
from time import sleep
from typing import Callable, Dict

from milk.cmm import Cmm
from milk.conf import signals


class ThreadNotFound(Exception):
    def __init__(self, tid: str):
        super(ThreadNotFound, self).__init__()
        self.tid = tid


class StoppableThread(Thread):
    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = Event()
        self._pause_event = Event()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def paused(self):
        return self._pause_event.is_set()

    def running(self):
        return (not self.stopped()) and (not self.paused())

    def start(self):
        super(StoppableThread, self).start()


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class ThreadRunner:
    def __init__(self):
        print('--- thread_runner', id(self))
        self._threads: Dict[str, StoppableThread] = dict()

    def start(self, runner: Callable, interval: float = 0.015, stop_on_error: bool = False):
        interval = max(0.015, interval)

        def on_error(err: str):
            signals.logger_error.emit(err)

        def _runner():
            while True:
                if thread is None or thread.stopped():
                    break
                if thread.running():
                    sleep(interval)
                    Cmm.trace(runner, on_error if stop_on_error else lambda: thread.stop())

        thread = StoppableThread(target=_runner, daemon=True)
        thread.name = str(id(thread))
        thread.start()

        self._threads.setdefault(thread.name, thread)
        return thread.name

    def _call(self, tid: str, method: str, fn: Callable = None):
        thread = self._threads.get(tid)
        if thread is not None:
            m = getattr(thread, method, None)
            if m is not None:
                if fn is not None:
                    fn()
                return m()
        raise ThreadNotFound(tid)

    def pause(self, tid: str):
        self._call(tid, 'pause')

    def resume(self, tid: str):
        self._call(tid, 'resume')

    def stop(self, tid: str):
        self._call(tid, 'stop', lambda: self._threads.pop(tid))

    def paused(self, tid: str):
        return self._call(tid, 'paused')

    def running(self, tid: str):
        return self._call(tid, 'running')

    def stopped(self, tid: str):
        return self._call(tid, 'stopped')
