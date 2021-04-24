import logging
from enum import Enum
from time import time

class TimerType(Enum):
    GENERAL = 'NONE'
    DB = 'DB'
    PARSE = 'PARSE'
    WEB = 'WEB'

class LogTimer(object):
    def __init__(self, context: str, timer_type: TimerType = None):
        self.context = context
        self.timer_type = TimerType.GENERAL if timer_type is None else timer_type

    def __enter__(self):
        self.initial_time = time()
    
    def __exit__(self, type, value, traceback):
        logging.debug("({}Timer) {:.3f}s - {}".format(self.timer_type, (time() - self.initial_time) * 1.0, self.context))