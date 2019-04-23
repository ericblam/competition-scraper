import argparse
import json
import queue
import signal
import threading
import traceback

from webparser import webparser
from util.dbutils import createConn
from util.crawlerutils import ScraperTask
from util.webutils import WebRequest, loadPage

class CrawlerExit(Exception):
    pass

def _crawler_shutdown(signum, frame):
    raise CrawlerExit

"""
Function each worker calls to do scraping work
Returns True if finished, False otherwise
"""
def scrapeFromQueue(q, conn, config):
    task = q.get()

    try:
        # if there are "None" tasks in the queue, we are done
        if task is None:
            return True

        # get HTML
        htmlDOM = loadPage(task.request)

        # if no hint, need to create one
        if task.hint is None:
            task.hint = webparser.getParserHint(task.request)

        # determine how to parse HTML
        parser = webparser.ParserFactory(q, conn, config, task.hint)

        # parse HTML
        if parser is not None:
            parser.parse(htmlDOM, task.data)
    except:
        traceback.print_exc()

    q.task_done()

    return False

class WorkerThread(threading.Thread):

    def __init__(self, q, conn, config):
        super(WorkerThread, self).__init__()
        self.q = q
        self.conn = conn
        self.config = config
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            if scrapeFromQueue(self.q, self.conn, self.config):
                break

    def stop(self):
        self.stop_event.set()

def parseArgs():
    """
    Parses command-line arguments
    """

    parser = argparse.ArgumentParser(description="Crawl around a website to scrape")
    parser.add_argument(
        "seedUrls"
        , nargs = "+"
        , type  = str
        , help  = "first urls to scrape for information"
    )
    parser.add_argument(
        "-n"
        , "--numWorkers"
        , nargs   = 1
        , type    = int
        , default = [4]
        , help    = "Number of workers to spawn"
    )
    parser.add_argument(
        "-c"
        , "--configFile"
        , nargs   = 1
        , type    = str
        , help    = "Configuration file path"
    )
    return parser.parse_args()

if __name__ == "__main__":

    signal.signal(signal.SIGTERM, _crawler_shutdown)
    signal.signal(signal.SIGINT, _crawler_shutdown)

    args = parseArgs()

    # initialize config
    config = {}
    with open(args.configFile[0]) as configFile:
        config = json.load(configFile)

    # initialize queue
    q = queue.Queue()
    for url in args.seedUrls:
        request = WebRequest(url)
        request.forceReload = True
        seedTask = ScraperTask(request, { 'url': url })
        q.put(seedTask)

    # start workers
    workers = []
    for i in range(args.numWorkers[0]):
        conn = createConn(config['db'])
        worker = WorkerThread(q, conn, config)
        worker.start()
        workers.append(worker)

    try:
        # block until we finish scraping
        q.join()
    except CrawlerExit:
        print("Stopping crawler")
        for worker in workers:
            worker.stop()
    finally:
        # stop workers
        for i in range(args.numWorkers[0]):
            q.put(None)
        for worker in workers:
            worker.join()
