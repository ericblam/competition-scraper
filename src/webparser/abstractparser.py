from abc import ABC, abstractmethod

class AbstractWebParser(ABC):

    def __init__(self, q, conn):
        self.q = q
        self.conn = conn

    @abstractmethod
    def parse(self, html, data):
        pass
