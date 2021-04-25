import logging
import re
from collections import namedtuple
from typing import List

from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils
from util.dbutils import createConnFromConfig, convertDataToFileLike
from util.logutils import LogTimer, TimerType

EventData = namedtuple('EventData', ['compId', 'eventId', 'eventName', 'eventUrl', 'eventNum'])
EventEntry = namedtuple('EventEntry', ['compId', 'eventId', 'coupleNum', 'leaderName', 'followerName', 'placement', 'coupleLocation'])

class O2cmCompParser(AbstractWebParser):

    def __init__(self, q, config):
        super(O2cmCompParser, self).__init__(q, config)

    def parse(self, htmlDOM, data):
        compId = data['compId']
        with LogTimer('Parsing comp {}'.format(compId), TimerType.PARSE):
            tables = htmlDOM.find_all('table')
            mainTable = tables[1]
            rows = mainTable.find_all('tr')

            logging.info("Scraping " + compId)

            # Find first link
            rowNum = 0
            eventNum = 0
            while rowNum < len(rows):
                if (rows[rowNum].find('a') != None):
                    break
                rowNum += 1

            lastHeatName = None
            lastHeatLink = None
            # Keep finding appropriate links
            # As before, read first event page, read all heats of event
            events: List[EventData] = []
            entries: List[EventEntry] = []
            while rowNum < len(rows):
                rowText = rows[rowNum].get_text().strip()

                # Blank row
                if rowText == '----':
                    pass

                # Row is a link. Read event and heats.
                elif (rows[rowNum].find('a') != None):
                    lastHeatName, lastHeatId, lastHeatLink = _parseHeatLink(rows[rowNum])
                    if ("combine" not in lastHeatName.lower()):
                        events.append(EventData(compId, lastHeatId, lastHeatName, lastHeatLink, eventNum))
                        eventNum += 1

                # Row is a couple
                elif (lastHeatName is not None and "combine" not in lastHeatName.lower()):
                    coupleNum, leaderName, followerName, placement, coupleLocation = _parseEntry(rows[rowNum].get_text().strip())
                    entries.append(EventEntry(compId, lastHeatId, coupleNum, leaderName, followerName, placement, coupleLocation))
                rowNum += 1

        with LogTimer('Storing event data {}'.format(compId), TimerType.DB):
            self._storeEvents(events)

        with LogTimer('Storing entry data {}'.format(compId), TimerType.DB):
            self._storeEventEntries(entries)

        for event in events:
            self._enqueueRounds(event)

    def _storeEvents(self, compEvents: List[EventData]):
        with createConnFromConfig(self.config) as conn, conn.cursor() as cursor:
            cursor.copy_from(
                convertDataToFileLike(compEvents),
                'o2cm.event',
                columns=('comp_id', 'event_id', 'event_name', 'event_url', 'event_num'))

    def _storeEventEntries(self, eventEntries: List[EventEntry]):
        with createConnFromConfig(self.config) as conn, conn.cursor() as cursor:
            cursor.copy_from(
                convertDataToFileLike(eventEntries),
                'o2cm.entry',
                columns=('comp_id', 'event_id', 'couple_num', 'leader_name', 'follower_name', 'event_placement', 'couple_location'))

    def _enqueueRounds(self, compEvent: EventData):
        nextRequest = util.webutils.WebRequest(compEvent.eventUrl, "GET", {})
        nextData = {
            "url": compEvent.eventUrl,
            "compId": compEvent.compId,
            "eventId": compEvent.eventId,
            "eventName": compEvent.eventName
        } # TODO: populate this
        newTask = util.crawlerutils.ScraperTask(
            nextRequest,
            nextData,
            ParserType.O2CM_ROUNDS)
        self.q.put(newTask)

def _parseHeatLink(tag):
    heatName = tag.get_text().lstrip().strip()
    heatLink = tag.find('a')['href']
    m = re.match(r'scoresheet\d.asp\?.+&heatid=(\w+)&.+', heatLink)
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
            logging.info(entryText)
            # TODO: need to deal with this
            return 0, "", "", 0, ""
    else:
        location = m.group(7)
    placement = m.group(1)
    number = m.group(2)
    leader = m.group(4)
    follower = m.group(6)
    return number, leader, follower, placement, location
