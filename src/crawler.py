import argparse
import json
import queue
import traceback

from webparser import webparser
from db import dbAccessor
from threading import Thread
from util.webUtils import WebRequest, loadPage

class ScraperTask:

    """
    Object containing information on what to scrape next.

    :param request: webUtils.WebRequest representing what page to fetch
    :param data: multi-level data from previous layer
    :param hint: hint for what kind of parser to use
    """
    def __init__(self, request, data = None, hint = None):
        self.request = request
        self.data = data
        self.hint = hint

    def __str__(self):
        return '%s\ndata: %s' % (self.request, self.data)

"""
Function each worker calls to do scraping work
"""
def scraper_worker(q, conn):
    while True:
        task = q.get()

        try:
            # if there are "None" tasks in the queue, we are done
            if task is None:
                break

            # get HTML
            html = loadPage(task.request)

            # if no hint, need to create one
            if task.hint is None:
                task.hint = webparser.getParserHint(task.request)

            # determine how to parse HTML
            parser = webparser.ParserFactory(q, conn, task.hint)

            # parse HTML
            parser.parse(html, task.data)
        except:
            traceback.print_exc()
            pass

        q.task_done()

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
        conn = dbAccessor.createConn(config['db'])
        worker = Thread(target=scraper_worker, args=(q, conn))
        worker.start()
        workers.append(worker)

    # block until we finish scraping
    q.join()

    # stop workers
    for i in range(args.numWorkers[0]):
        q.put(None)
    for worker in workers:
        worker.join()
