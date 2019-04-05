from abc import ABC, abstractmethod

class AbstractWebParser(ABC):

    def __init__(self, q, conn, config=None):
        self.q = q
        self.conn = conn
        self.config = config

    @abstractmethod
    def parse(self, htmlDOM, data):
        pass
