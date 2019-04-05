from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmCompParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmCompParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):
        print(data)
