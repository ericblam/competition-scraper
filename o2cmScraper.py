import argparse
import logging
import re
import signal

from pg import IntegrityError

import db.dbObjects as dbo
import db.dbAccessor as dba

from util.utils import *
from util.compUtils import *
from util.loadPage import loadPage

LOG_FILE_NAME = ".o2cmScraper.log"

O2CM_MAIN_RESULTS_URL = "http://results.o2cm.com/"

g_nextCompetitorId = 0
g_competitors = {} # (firstName, lastName): competitorId

def main():
    args = initialize()

    urlQueue = []
    compsOfInterest = args.comps

    comps = parseMainResultsPage(compsOfInterest)

    try:
        dba.insertCompetitionList(comps)
    except IntegrityError as e:
        logging.error(e);

    for comp in comps:
        logging.info(">>>   %s   <<<", "%s, %s" % (comp.d_compName, comp.d_compDate))
        compPage = loadCompPage(comp.d_compId)
        #readCompPage(comp.compId, compPage)


############################## SET UP ##############################
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
        dba.dbReset()

    if (args.clear is not None):
        dba.dbClearComp(args.clear[0])
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
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler for logging
    handler = logging.StreamHandler()
    handler.setLevel(logLevel)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create file handler for logging
    handler = logging.FileHandler(LOG_FILE_NAME, "w", encoding=None, delay="true")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # set up signal handler
    signal.signal(signal.SIGINT, sigintHandler)

    # initialize competitor lists
    results = dba.selectFromCompetitor()
    for res in results:
        g_competitors[(res.d_firstName, res.d_lastName)] = res.d_competitorId
    if (len(results) > 0):
        g_nextCompetitorId = max(g_competitors.values()) + 1

    return args

############################## Page scrapers ##############################

def parseMainResultsPage(compsOfInterest=[]):
    """
    Returns list of Competition objects of interest

    :param compsOfInterest: list of compIds to specifically scrape. Scrapes all if empty
    :returns:
    """

    soup = loadPage(O2CM_MAIN_RESULTS_URL, forceReload=True)
    compLinks = soup.find_all('a')
    competitions = []
    for tag in compLinks:
        year = tag.find_previous('td', 'h3').get_text().strip()
        date = tag.parent.previous_sibling.previous_sibling.string.strip()
        compName = tag.get_text()
        link = tag['href']
        m = re.match('event[23].asp\?event=([a-zA-Z]{0,4}\d{0,5}[a-zA-Z]?)&.*', link)
        compId = m.group(1).lower()
        if (len(compsOfInterest) == 0 or compId in compsOfInterest):
            m = re.match('([a-z]+)\d+.*', compId)
            compCode = m.group(1)
            competitions.append(dbo.Competition(compId, compCode, compName, date + " " + year))
    return competitions

def loadCompPage(compId):
    pass

############################## MAIN ##############################

if __name__ == "__main__":
    main()
