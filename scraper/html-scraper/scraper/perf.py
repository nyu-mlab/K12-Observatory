""" Performance profiling helpers
"""
import time


class TimerError(Exception):
    pass


class Timer:
    "Timer with context manager"

    def __init__(self, fmt="Elapsed time: {:0.4f} seconds", logger=print):
        self.timers = {}
        self.format = fmt
        self.logger = logger
        self._start_time = None

    def start(self):
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter_ns()

    def stop(self):
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")
        elapsed_time = (time.perf_counter_ns() -
                        self._start_time) / 1000_000_000
        self._start_time = None
        if self.logger:
            self.logger(self.format.format(elapsed_time))

        return elapsed_time

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()
