from abc import ABC, abstractmethod

class AbstractWebParser(ABC):

    def __init__(self, q, config):
        self.q = q
        self.config = config

    @abstractmethod
    def parse(self, htmlDOM, data):
        pass
