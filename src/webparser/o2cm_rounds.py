import logging

from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmHeatRoundsParser(AbstractWebParser):

    def __init__(self, q, config):
        super(O2cmHeatRoundsParser, self).__init__(q, config)

    def parse(self, htmlDOM, data):
        logging.info("Scraping " + data["compId"] + ", " + data["eventName"])

        compId = data["compId"]
        heatId = data["eventId"]

        heatUrlSimple = data["url"].split("?")[0]
        selCount = htmlDOM.find('select', id='selCount')
        numRounds = 0
        self._enqueue(compId, heatId, 0, heatUrlSimple)
        if selCount is not None:
            numRounds = len(selCount.find_all('option'))
            for roundNum in range(1, numRounds):
                self._enqueue(compId, heatId, roundNum, heatUrlSimple)

    def _enqueue(self, compId, heatId, roundNum, heatUrlSimple):
        requestData = {
            'event': compId,
            'heatId': heatId,
            'selCount': roundNum
        }
        nextRequest = util.webutils.WebRequest(heatUrlSimple, "POST", requestData)

        newData = {
            'compId': compId,
            'eventId': heatId,
            'roundNum': roundNum
        }

        newTask = util.crawlerutils.ScraperTask(
            nextRequest,
            newData,
            ParserType.O2CM_HEAT)
        self.q.put(newTask)
