import re

from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmCompParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmCompParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):
        tables = htmlDOM.find_all('table')
        mainTable = tables[1]
        rows = mainTable.find_all('tr')

        # Find first link
        rowNum = 0
        while rowNum < len(rows):
            if (rows[rowNum].find('a') != None):
                break
            rowNum += 1

        lastHeatName = None
        lastHeadId = None
        lastHeatLink = None
        # Keep finding appropriate links
        # As before, read first event page, read all heats of event
        while rowNum < len(rows):
            rowText = rows[rowNum].get_text().strip()

            # Blank row
            if rowText == '----':
                pass

            # Row is a link. Read event and heats.
            elif (rows[rowNum].find('a') != None):
                lastHeatName, lastHeatId, lastHeatLink = parseHeatLink(rows[rowNum])
                if ("combine" not in lastHeatName.lower()):
                    # TODO: add task to queue to get all rounds for this event
                    # readHeatPages(compId, lastHeatId, lastHeatLink)
                    # TODO: Store data
                    pass

            # Row is a couple
            elif (lastHeatName is not None and "combine" not in lastHeatName.lower()):
                # parseCouple(rowText, compId, lastHeatId, compData)
                # TODO: parse couple; get last name/first name; may need some sort of thread-safe cache for name -> (firstname, lastname)
                print(data['compId'], lastHeatName, rowText)
                pass

            rowNum += 1


            # TODO: Store data

def parseHeatLink(tag):
    heatName = tag.get_text().lstrip().strip()
    heatLink = tag.find('a')['href']
    m = re.match('scoresheet\d.asp\?.+&heatid=(\w+)&.+', heatLink)
    heatId = m.group(1)
    heatLink = 'http://results.o2cm.com/' + heatLink
    return (heatName, heatId, heatLink)
