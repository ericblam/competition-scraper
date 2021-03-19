import argparse
import json
import pickle
import queue
import signal
import sys

from webcrawler.worker import WorkerThread
from util.dbutils import createConn
from util.crawlerutils import ScraperTask
from util.webutils import WebRequest

class CrawlerExit(Exception):
    pass

def _crawler_shutdown(signum, frame):
    raise CrawlerExit

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
        "-r"
        , "--reload"
        , action = "store_true"
        , help   = "Reload seedUrls - do not use cache"
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
    parser.add_argument(
        "-E"
        , "--clearExceptions"
        , action  = "store_true"
        , help    = "Clear tasks from exception queue"
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
    q = queue.LifoQueue()

    if args.showExceptions:
        conn = createConn(config['db'])
        exceptions = conn.query("SELECT error_id, task, error_description FROM crawler.error").getresult()
        for e in exceptions:
            task = pickle.loads(conn.unescape_bytea(e[1]))
            print(task)
            print(e[2])
        exit()

    if args.clearExceptions:
        conn = createConn(config['db'])
        conn.query("DELETE FROM crawler.error")
        exit()

    if args.exceptions:
        conn = createConn(config['db'])
        exceptions = conn.query("SELECT error_id, task, error_description FROM crawler.error").getresult()
        for e in exceptions:
            task = pickle.loads(conn.unescape_bytea(e[1]))
            q.put(task)
        conn.query("DELETE FROM crawler.error")

    for url in args.seedUrls:
        request = WebRequest(url)
        request.forceReload = args.reload
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
