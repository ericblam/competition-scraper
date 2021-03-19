import argparse
import json
import logging
import pickle
import queue
import signal
import sys

from webcrawler.worker import WorkerThread
from util.dbutils import createConnFromConfig
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

def configureLogging(config):
    LOGGING_CONFIG_NAME = 'logging'
    LOGGING_CONFIG_PATH_NAME = 'path'
    LOGGING_CONFIG_LEVEL_NAME = 'level'
    if LOGGING_CONFIG_NAME not in config or LOGGING_CONFIG_PATH_NAME not in config[LOGGING_CONFIG_NAME]:
        return

    log_level = logging.INFO
    if LOGGING_CONFIG_LEVEL_NAME in config[LOGGING_CONFIG_NAME] is not None:
        log_level = getattr(logging, config[LOGGING_CONFIG_NAME][LOGGING_CONFIG_LEVEL_NAME].upper(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    console_log_formatter = logging.Formatter('%(levelname)s %(message)s')
    console_log = logging.StreamHandler(stream=sys.stdout)
    console_log.setLevel(log_level)
    console_log.setFormatter(console_log_formatter)
    logger.addHandler(console_log)

    file_log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s: %(message)s')
    file_log = logging.FileHandler(config[LOGGING_CONFIG_NAME][LOGGING_CONFIG_PATH_NAME])
    file_log.setLevel(log_level)
    file_log.setFormatter(file_log_formatter)
    logger.addHandler(file_log)

if __name__ == "__main__":

    signal.signal(signal.SIGTERM, _crawler_shutdown)
    signal.signal(signal.SIGINT, _crawler_shutdown)

    args = parseArgs()

    # initialize config
    config = {}
    with open(args.configFile[0]) as configFile:
        config = json.load(configFile)

    configureLogging(config)
    logger = logging.getLogger()

    # initialize queue
    q = queue.LifoQueue()

    if args.showExceptions:
        with createConnFromConfig(config) as conn:
            exceptions = conn.query("SELECT error_id, task, error_description FROM crawler.error").getresult()
            for e in exceptions:
                task = pickle.loads(conn.unescape_bytea(e[1]))
                logger.error(task)
                logger.error(e[2])
            exit()

    if args.clearExceptions:
        with createConnFromConfig(config) as conn:
            conn.query("DELETE FROM crawler.error")
            exit()

    if args.exceptions:
        with createConnFromConfig(config) as conn:
            conn = createConnFromConfig(config)
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
        conn = createConnFromConfig(config)
        worker = WorkerThread(q, config)
        worker.start()
        workers.append(worker)

    try:
        # block until we finish scraping
        q.join()
    except CrawlerExit:
        logging.info("Stopping crawler")
        for worker in workers:
            worker.stop()
    finally:
        # stop workers
        for i in range(args.numWorkers[0]):
            q.put(None)
        for worker in workers:
            worker.join()
