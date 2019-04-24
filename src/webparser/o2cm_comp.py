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

        compId = data['compId']
        print("Scraping " + compId)

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
                lastHeatName, lastHeatId, lastHeatLink = _parseHeatLink(rows[rowNum])
                if ("combine" not in lastHeatName.lower()):
                    self._storeEvent(compId, lastHeatId, lastHeatName, lastHeatLink)
                    self._enqueueRounds(compId, lastHeatName, lastHeatId, lastHeatLink)

            # Row is a couple
            elif (lastHeatName is not None and "combine" not in lastHeatName.lower()):
                coupleNum, leaderName, followerName, placement, coupleLocation = _parseEntry(rows[rowNum].get_text().strip())
                self._storeEventEntry(compId, lastHeatId, coupleNum, leaderName, followerName, placement, coupleLocation)

            rowNum += 1


    def _storeEvent(self, compId, eventId, eventName, eventUrl):
        conn = self.conn
        conn.insert("o2cm.event",
                    comp_id=compId,
                    event_id=eventId,
                    event_name=eventName,
                    event_url=eventUrl)

    def _storeEventEntry(self, compId, eventId, coupleNum, leaderName, followerName, placement, coupleLocation=None):
        conn = self.conn
        conn.insert("o2cm.entry",
                    comp_id=compId,
                    event_id=eventId,
                    couple_num=coupleNum,
                    leader_name=leaderName,
                    follower_name=followerName,
                    event_placement=placement,
                    couple_location=coupleLocation)

    def _enqueueRounds(self, compId, heatName, heatId, heatLink):
        nextRequest = util.webutils.WebRequest(heatLink, "GET", {})
        nextData = {
            "url": heatLink,
            "compId": compId,
            "eventId": heatId,
            "eventName": heatName
        } # TODO: populate this
        newTask = util.crawlerutils.ScraperTask(
            nextRequest,
            nextData,
            ParserType.O2CM_ROUNDS)
        self.q.put(newTask)

def _parseHeatLink(tag):
    heatName = tag.get_text().lstrip().strip()
    heatLink = tag.find('a')['href']
    m = re.match('scoresheet\d.asp\?.+&heatid=(\w+)&.+', heatLink)
    heatId = m.group(1)
    heatLink = 'http://results.o2cm.com/' + heatLink
    return (heatName, heatId, heatLink)

def _parseEntry(entryText):
    patternBase = "(\d+)\\)\s+(\d+)(\s+(.+))?\s+\\&(\s+(.+))?"
    m = re.match(patternBase + "\s+\-\s+(\w+)", entryText)
    location = None
    if m is None:
        m = re.match(patternBase, entryText)
        if m is None:
            print(entryText)
            # TODO: need to deal with this
            return 0, "", "", 0, ""
    else:
        location = m.group(7)
    placement = m.group(1)
    number = m.group(2)
    leader = m.group(4)
    follower = m.group(6)
    return number, leader, follower, placement, location
