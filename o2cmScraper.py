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

############################## MAIN ##############################

def main():
    args = initialize()

    compsOfInterest = args.comps

    comps = parseMainResultsPage(compsOfInterest)

    for comp in comps:
        compData = dba.DbObjectContainer()
        compData.addCompetition(comp)
        logging.info(">>>   %s   <<<", "%s, %s" % (comp.d_compName, comp.d_compDate))
        compPage = loadCompPage(comp.d_compId)
        readCompPage(compPage, comp.d_compId, compData)


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
    logLevel = logging.WARNING
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
    :returns: List of dbo.Competition objects
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
            fullDate = date + " " + year
            competitions.append(dbo.Competition(compId, compCode, compName, fullDate))
    return competitions

def loadCompPage(compId):
    """
    Loads page for competition compId

    :param compId: string compId
    :returns: bs4 object of results page for compId
    """

    url = 'http://results.o2cm.com/event3.asp'
    data = {
        'selDiv': '',
        'selAge': '',
        'selSkl': '',
        'selSty': '',
        'selEnt': '',
        'submit': 'OK',
        'event': compId
    }
    return loadPage(url, data, post=True)

def readCompPage(compPage, compId, compData):
    """
    Reads whole listing of results from competition page.

    :param compId: string id for the competition
    :param compPage: bs4 object of competition results page
    :returns:
    """

    tables = compPage.find_all('table')
    mainTable = tables[1]
    rows = mainTable.find_all('tr')

    # Find first link
    rowNum = 0
    while rowNum < len(rows):
        if (rows[rowNum].find('a') != None):
            break
        rowNum += 1

    lastHeatName = None
    lastHeadId = None
    lastHeatLink = None
    # Keep finding appropriate links
    # As before, read first event page, read all heats of event
    while rowNum < len(rows):
        rowText = rows[rowNum].get_text().strip()

        # Blank row
        if rowText == '----':
            pass
        # Row is a link. Read event and heats.
        elif (rows[rowNum].find('a') != None):
            lastHeatName, lastHeatId, lastHeatLink = parseHeatLink(rows[rowNum])
            if ("combine" not in lastHeatName.lower()):
                readHeatPages(compId, lastHeatId, lastHeatLink)
        # Row is a couple
        elif (lastHeatName is not None and "combine" not in lastHeatName.lower()):
            pass
            # TODO: replace this functionality
            # parseCouple(rowText, compId, lastHeatId)

        rowNum += 1

def readHeatPages(compId, heatId, heatUrl):
    pass

############################## UTILS ##############################
def parseHeatLink(tag):
    """
    Gets info from heat link tag.
    :param tag: Tag containing <a> tag with link to heat
    :returns: tuple of (heatName, heatId, heatLink)
    """

    heatName = tag.get_text().lstrip().strip()
    heatLink = tag.find('a')['href']
    m = re.match('scoresheet\d.asp\?.+&heatid=(\w+)&.+', heatLink)
    heatId = m.group(1)
    heatLink = 'http://results.o2cm.com/' + heatLink
    logging.info(heatName)
    return (heatName, heatId, heatLink)

############################## MAIN ##############################

if __name__ == "__main__":
    main()
