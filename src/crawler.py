import argparse
import json
import pickle
import queue
import signal
import sys
import threading
import traceback

from webparser import parserfactory
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
            task.hint = parserfactory.getParserHint(task.request)

        # determine how to parse HTML
        parser = parserfactory.ParserFactory(q, conn, config, task.hint)

        # parse HTML
        if parser is not None:
            try:
                parser.parse(htmlDOM, task.data)
            except Exception as e:
                stacktraceText = traceback.format_exc()
                print(stacktraceText)
                conn.insert("crawler.error",
                            task=conn.escape_bytea(pickle.dumps(task)),
                            error_description=stacktraceText)
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
    parser.add_argument(
        "-e"
        , "--exceptions"
        , action  = "store_true"
        , help    = "Load tasks from exception queue"
    )
    parser.add_argument(
        "-x"
        , "--showExceptions"
        , action  = "store_true"
        , help    = "Show tasks from exception queue"
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

    if args.exceptions or args.showExceptions:
        conn = createConn(config['db'])
        exceptions = conn.query("SELECT error_id, task, error_description FROM crawler.error").getresult()
        for e in exceptions:
            task = pickle.loads(conn.unescape_bytea(e[1]))

            if args.showExceptions:
                print(task)
                print(e[2])

            if args.exceptions:
                q.put(task)
        if args.showExceptions:
            exit()
        if args.exceptions:
            conn.query("DELETE FROM crawler.error")

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
