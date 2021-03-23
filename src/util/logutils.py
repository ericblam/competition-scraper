import logging
from time import time

class LogTimer(object):
    def __init__(self, context: str):
        self.context = context

    def __enter__(self):
        self.initial_time = time()
    
    def __exit__(self, type, value, traceback):
        logging.debug("{} took {:.3f}s".format(self.context, (time() - self.initial_time) * 1.0))
