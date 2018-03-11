import argparse
import logging
import signal

from util.utils import *
from util.compUtils import *
from util.loadPage import loadPage
from db.dbObjects import *
from db.dbAccessor import *

LOG_FILE_NAME = ".o2cmScraper.log"

g_nextCompetitorId = 0
g_competitors = {} # (firstName, lastName): competitorId

def main():
    args = initialize()

    urlQueue = []
    compsOfInterest = args.comps


def parseArgs():
    """
    Parses command line arguments
    """
    parser = argparse.ArgumentParser(description="Scrape O2CM database")
    parser.add_argument("comps",
                        nargs   = "*",
                        help    = "competition ids from which to scrape")
    parser.add_argument("--clear",
                        dest    = "clear",
                        nargs   = 1,
                        default = None,
                        help    = "clears data from specified competition")
    parser.add_argument("--reset",
                        dest    = "reset",
                        action  = 'store_true',
                        default = False,
                        help    = 'resets database')
    parser.add_argument("--verbose",
                        dest    = "verbose",
                        action  = 'store_true',
                        default = False,
                        help    = 'Outputs verbosely')
    args = parser.parse_args()

    # reset database if appropriate
    if (args.reset):
        dbReset()

    if (args.clear is not None):
        dbClearComp(args.clear[0])
        exit(0)

    return args

def initialize():
    """
    Initialize scraper.

    Parses command line arguments, opens log, sets up signal handlers
    """

    global g_competitors
    global g_nextCompetitorId

    args = parseArgs()

    # Open Log
    logLevel = logging.DEBUG
    if (args.verbose):
        logLevel = logging.INFO
    logging.basicConfig(filename = LOG_FILE_NAME,
                        format   = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                        datefmt  = "%y-%m-%d %H:%M:%S",
                        level    = logLevel)

    signal.signal(signal.SIGINT, sigintHandler)

    results = selectFromCompetitor()
    for res in results:
        g_competitors[(res.d_firstName, res.d_lastName)] = res.d_competitorId
    if (len(results) > 0):
        g_nextCompetitorId = max(g_competitors.values()) + 1

    return args



if __name__ == "__main__":
    main()
