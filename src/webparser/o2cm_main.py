import re

from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmMainParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmMainParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):
        compsOfInterest = []
        if 'o2cm' in self.config and 'comps' in self.config['o2cm']:
            compsOfInterest = self.config['o2cm']['comps']

        compLinks = htmlDOM.find_all('a')
        for tag in compLinks:
            year = tag.find_previous('td', 'h3').get_text().strip()
            date = tag.parent.previous_sibling.previous_sibling.string.strip()
            compName = tag.get_text()
            link = tag['href']
            m = re.match('event[23].asp\?event=([a-zA-Z]{0,4}\d{0,5}[a-zA-Z]?)&.*', link)
            compId = m.group(1).lower()
            if (len(compsOfInterest) == 0 or compId in compsOfInterest):
                m = re.match('([a-z]+)\d+.*', compId)
                compCode = m.group(1)
                fullDate = date + " " + year

                url = 'http://results.o2cm.com/event3.asp'
                requestData = {
                    'selDiv': '',
                    'selAge': '',
                    'selSkl': '',
                    'selSty': '',
                    'selEnt': '',
                    'submit': 'OK',
                    'event': compId
                }
                nextRequest = util.webutils.WebRequest(url, 'POST', requestData)
                nextData = {
                    compId: compId
                }
                newTask = util.crawlerutils.ScraperTask(
                    nextRequest,
                    nextData,
                    ParserType.O2CM_COMP)
                self.q.put(newTask)

                print("Fetched data for %s (%s)" % (compId, compName))
