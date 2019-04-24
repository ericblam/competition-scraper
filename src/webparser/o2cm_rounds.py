from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmHeatRoundsParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmHeatRoundsParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):
        print("Scraping " + data["compId"] + ", " + data["heatName"])

        compId = data["compId"]
        heatId = data["heatId"]

        heatUrlSimple = data["url"].split("?")[0]
        selCount = htmlDOM.find('select', id='selCount')
        numRounds = 0
        if selCount is not None:
            numRounds = len(selCount.find_all('option'))

            for roundNum in range(0, numRounds):
                requestData = {
                    'event': compId,
                    'heatId': heatId,
                    'selCount': roundNum
                }
                nextRequest = util.webutils.WebRequest(heatUrlSimple, "POST", requestData)

                newData = {
                    'compId': compId,
                    'heatId': heatId,
                    'roundNum': roundNum
                }

                newTask = util.crawlerutils.ScraperTask(
                    nextRequest,
                    newData,
                    ParserType.O2CM_HEAT)
                self.q.put(newTask)
