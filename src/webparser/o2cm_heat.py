from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmHeatParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmHeatParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):
        print(data)
