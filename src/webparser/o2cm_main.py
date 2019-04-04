from webparser.abstractparser import AbstractWebParser
from util.webUtils import getHostname

class O2cmMainParser(AbstractWebParser):

    def __init__(self, q, conn):
        super(O2cmMainParser, self).__init__(q, conn)

    def parse(self, html, data):
        print(data)
