import json
import queue
import sys

from crawler import scrapeFromQueue
from webparser import webparser, parsertype
from util.crawlerutils import ScraperTask
from util.dbutils import createConn
from util.webutils import WebRequest, loadPage

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python3 %s <config-file>" % sys.argv[0])
        exit()

    # mock setup
    config = {}
    with open(sys.argv[1]) as configFile:
        config = json.load(configFile)

    q = queue.Queue()
    conn = createConn(config['db'])

    url = "http://results.o2cm.com/scoresheet3.asp"
    compId = "rub19"
    heatId = "40323030"
    roundNum = 1

    # set up data/requests/tasks
    requestData = {
        'event': compId,
        'heatId': heatId,
        'selCount': roundNum
    }
    nextRequest = WebRequest(url, "POST", requestData)

    newData = {
        'compId': compId,
        'heatId': heatId,
        'roundNum': roundNum
    }

    task = ScraperTask(
        nextRequest,
        newData,
        parsertype.ParserType.O2CM_HEAT)

    q.put(task)

    ############################# actual crawling

    scrapeFromQueue(q, conn, config)
