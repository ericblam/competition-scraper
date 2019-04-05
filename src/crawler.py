import argparse
import json
import queue
import traceback

from webparser import webparser
from db import dbaccessor
from threading import Thread
from util.crawlerutils import ScraperTask
from util.webutils import WebRequest, loadPage

"""
Function each worker calls to do scraping work
"""
def scraper_worker(q, conn, config):
    while True:
        task = q.get()

        try:
            # if there are "None" tasks in the queue, we are done
            if task is None:
                break

            # get HTML
            htmlDOM = loadPage(task.request)

            # if no hint, need to create one
            if task.hint is None:
                task.hint = webparser.getParserHint(task.request)

            # determine how to parse HTML
            parser = webparser.ParserFactory(q, conn, config, task.hint)

            # parse HTML
            parser.parse(htmlDOM, task.data)
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
        conn = dbaccessor.createConn(config['db'])
        worker = Thread(target=scraper_worker, args=(q, conn, config))
        worker.start()
        workers.append(worker)

    # block until we finish scraping
    q.join()

    # stop workers
    for i in range(args.numWorkers[0]):
        q.put(None)
    for worker in workers:
        worker.join()
