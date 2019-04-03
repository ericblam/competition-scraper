import argparse
import logging
import re
import signal

from pg import IntegrityError

import db.dbObjects as dbo
import db.dbAccessor as dba

from util.sysUtils import *
from util.compUtils import *
from util.webUtils import loadPage

LOG_FILE_NAME = ".o2cmScraper.log"

O2CM_MAIN_RESULTS_URL = "http://results.o2cm.com/"

g_nextCompetitorId = 0
g_competitorToNames = {} # unsplitString: (firstName, lastName)
g_competitors = {}       # (firstName, lastName): competitorId

############################## MAIN ##############################

def main():
    args = initialize()

    compsOfInterest = args.comps

    comps = parseMainResultsPage(compsOfInterest)

    for comp in comps:
        compData = dba.DbObjectContainer()
        compData.addCompetition(comp)
        logging.info(">>>   %s   <<<", "%s, %s" % (comp.d_compName, comp.d_compDate))
        readCompPage(comp.d_compId, compData)
        compData.dumpToDb()


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
            competitions.append(dbo.Competition(compId, compName, fullDate))
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

def readCompPage(compId, compData):
    """
    Reads whole listing of results from competition page.

    :param compId: string id for the competition
    :param compData: Aggregate to save data into
    :effects: Adds appropriate data to compData
    """

    compPage = loadCompPage(compId)
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
                # TODO: Add data to compData
        # Row is a couple
        elif (lastHeatName is not None and "combine" not in lastHeatName.lower()):
            parseCouple(rowText, compId, lastHeatId, compData)

        rowNum += 1

def loadHeatPage(heatUrl):
    """
    Loads page for heat with heatUrl

    :param heatUrl: url from which to fetch
    """
    return loadPage(heatUrl)

def getHeatPage(compId, heatId, roundNum, url):
    """
    Gets all heat pages for a given event

    :param compId: string competition id
    :param heatId: string event id
    :param roundNum: int round number for heat
    :param url: string url for heat
    :returns: bs4 object representing comp event heat
    """

    return loadPage(url, {'event': compId, 'heatId': heatId, 'selCount': roundNum}, True)

def getAllHeatPagesForEvent(page, compId, heatId, url):
    heatUrlSimple = url.split("?")[0]
    selCount = page.find('select', id='selCount')
    numRounds = 0
    if selCount is not None:
        numRounds = len(selCount.find_all('option')) - 1
        for r in range(numRounds - 1, 0, -1):
            yield r, getHeatPage(compId, heatId, r, heatUrlSimple)
    yield 0, page

def readHeatPages(compId, heatId, heatUrl):
    """
    Gets all pages for event and parses through each

    :param compId: string id for the competition
    :param heatId: string id for the event
    :param heatUrl: string url for the event pages
    """

    heatPage = loadHeatPage(heatUrl)
    for heatNum, page in getAllHeatPagesForEvent(heatPage, compId, heatId, heatUrl):
        readHeatPage(compId, heatId, heatNum, page)

def readHeatPage(compId, heatId, heatNum, page):
    """
    Read information from heat page

    :param compId: string comp id
    :param heatId: string event id
    :param heatNum: int representing the heat (0 is final, 1 is semi, ...)
    :param page: bs4 object of event heat
    """

    pass

def parseCouple(rowText, compId, heatId, compData):
    """
    Parses 'rowText' for leader and follower information

    :param rowText: Text from row containing leader and follwer information
    :param compId: id of competition
    :param lastHeatId: id of heat to which to add competitiors
    :param compData: Aggregate to save data into
    :effects: Add competitor and entry info into compData
    """

    m = re.match('\d+\) (\d{1,3}) (.+) & (.+) \- (.+)', rowText)
    state = 'N/A'
    if (m != None):
        state = m.group(4).strip()
    else:
        m = re.match('\d+\) (\d{1,3}) (.+) & (.+)', rowText)
    coupleNumber = m.group(1).strip()
    leaderString = m.group(2).strip()
    leader = competitorName(leaderString)
    leaderId = getCompetitorIdAndSave(leader, compData)
    followerString = m.group(3).strip()
    follower = competitorName(followerString)
    followerId = getCompetitorIdAndSave(follower, compData)

    compData.addCompetitionEntry(dbo.CompetitionEntry(compId, heatId, coupleNumber, leaderId, followerId))

############################## UTILS ##############################
def getCompetitorIdAndSave(nameTuple, compData):
    """
    Gets competitor id from database. If competitor not in database, adds it to compData

    :param nameTuple: tuple (firstName, lastName)
    :param compData: Aggregate to save competitor data to
    """

    global g_nextCompetitorId
    global g_competitors

    if nameTuple not in g_competitors:
        g_competitors[nameTuple] = g_nextCompetitorId
        compData.addCompetitor(dbo.Competitor(g_nextCompetitorId, nameTuple[0], nameTuple[1]))
        g_nextCompetitorId += 1
    return g_competitors[nameTuple]

def competitorName(name):
    """
    Parses name into first and last name, checking against o2cm if ambiguous

    :param name: string containing full name
    :returns: tuple (firstName, lastName)
    """

    global g_competitorToNames

    tokens = name.split()
    if (len(tokens) < 2):
        return (name, '')
    elif (len(tokens) == 2):
        return (tokens[0], tokens[1])
    else:
        if (name in g_competitorToNames):
            return g_competitorToNames[name]
        found = False
        for i in range(1, len(tokens)):
            firstName = ' '.join(tokens[0:i])
            lastName = ' '.join(tokens[i:len(tokens)])
            soup = loadPage('http://results.o2cm.com/individual.asp', {'szFirst': firstName, 'szLast': lastName}, True)
            if (soup.find('b') != None and 'no results' not in soup.find('b').get_text().lower()):
                if (found):
                    logging.warning("multiple people named %s", name)
                found = True
        if (found):
            g_competitorToNames[name] = (firstName, lastName)
            return (firstName, lastName)
        return (name, '')

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
