import argparse
import logging
import signal
from math import floor
from pg import DB, IntegrityError

from re import match
from util.comp_utils import *
from util.loadPage import loadPage

LOG_FILE_NAME = ".o2cmScraper.log"

db = None
compsOfInterest = ['rpi17']
newCompetitorId = 0
competitorToNames = {} # unsplitString: (firstName, lastName)
competitors = {}       # (firstName, lastName): competitorId
judges = {}            # (compId, judgeId): judgeName
heats = set()          # (compId, eventId)

def main():
    initialize()

    global compsOfInterest

    comps = getListofComps(compsOfInterest)
    for comp in comps:
        try:
            db.insert("competitions",
                      competition_id=comp.compId,
                      comp_host="",
                      comp_name=comp.compName,
                      comp_date=comp.date)
            compPage = getCompPage(comp.compId)
            print(">>>   %s   <<<" % comp)
            logging.info(">>>   %s   <<<", comp)
            readCompPage(comp.compId, compPage)
        except IntegrityError as e:
            logging.error(e);

def initialize():
    """
    Initializes state from database
    """

    parser = argparse.ArgumentParser(description="Scrape O2CM database")
    parser.add_argument("comps",
                        nargs="*",
                        help="competition ids from which to scrape")
    parser.add_argument("--clear",
                        dest="clear",
                        nargs=1,
                        default=None,
                        help="clears data from specified competition")
    parser.add_argument("--reset",
                        dest="reset",
                        action='store_true',
                        default=False,
                        help='resets database')
    parser.add_argument("--verbose",
                        dest="verbose",
                        action='store_true',
                        default=False,
                        help='Outputs verbosely')
    args = parser.parse_args()

    # Open Log
    logLevel = logging.DEBUG
    if (args.verbose):
        logLevel = logging.INFO
    logging.basicConfig(filename=LOG_FILE_NAME,
                        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                        datefmt="%y-%m-%d %H:%M:%S",
                        level=logLevel)


    signal.signal(signal.SIGINT, sigintHandler)

    # initialize database connection
    global db
    db = DB(dbname='ballroom_competitions',
            host='localhost',
            port=5432,
            user='postgres',
            passwd='postgres')
    global compsOfInterest
    if (len(args.comps) > 0):
        compsOfInterest = args.comps

    # reset database if appropriate
    if (args.reset):
        sqlClearing = open('ballroom.sql')
        db.query(sqlClearing.read())
        sqlClearing.close()

    if (args.clear is not None):
        compToClear = args.clear[0]
        with open('clear.sql') as queryFile:
            query = queryFile.read() % ((compToClear,) * 6)
            db.query(query)
        exit(0)

    # initialize next available competitor id
    result = db.query("select max(competitor_id) from competitors").getresult()
    global newCompetitorId
    if (len(result) > 0 and result[0][0] is not None):
        newCompetitorId = result[0][0] + 1

    # initialize competitors
    global competitors
    result = db.query("select * from competitors").getresult()
    if (len(result) > 0):
        competitors = {(x[1], x[2]): x[0] for x in result}

    # initialize judges
    global judges
    result = db.query("select * from judges").getresult()
    if (len(result) > 0):
        judges = {(x[0], x[1]): x[2] for x in result}

    # initialize heats
    global heats
    result = db.query("select * from events").getresult()
    if (len(result) > 0):
        heats = set([(x[0], x[1]) for x in result])

def getListofComps(compsOfInterest=[]):
    """
    Returns list of Competition objects of interest

    :param compsOfInterest: list of compIds to specifically scrape. Scrapes all if empty
    :returns: list of Competitions
    """

    url = 'http://results.o2cm.com/'
    soup = loadPage(url)
    compLinks = soup.find_all('a')
    competitions = []
    for tag in compLinks:
        year = tag.find_previous('td', 'h3').get_text().strip()
        date = tag.parent.previous_sibling.previous_sibling.string.strip()
        compName = tag.get_text()
        link = tag['href']
        m = match('event[23].asp\?event=([a-zA-Z]{0,4}\d{0,5}[a-zA-Z]?)&.*', link)
        compId = m.group(1)
        if (len(compsOfInterest) == 0 or compId in compsOfInterest):
            competitions.append(Competition(compId, compName, year, date))
    return competitions

def getCompPage(compId):
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
    return loadPage(url, data, True);

def parseHeatLink(tag):
    """
    Gets info from heat link tag.

    :param tag: Tag containing <a> tag with link to heat
    :returns: tuple of (heatName, heatId, heatLink)
    """

    heatName = tag.get_text().lstrip().strip()
    heatLink = tag.find('a')['href']
    m = match('scoresheet\d.asp\?.+&heatid=(\w+)&.+', heatLink)
    heatId = m.group(1)
    heatLink = 'http://results.o2cm.com/' + heatLink
    print(heatName)
    logging.info(heatName)
    return (heatName, heatId, heatLink)

def readCompPage(compId, compPage):
    """
    Reads whole listing of results from competition page.

    :param compId: string id for the competition
    :param compPage: bs4 object of competition results page
    :effects: adds competitors and entries to database
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

    # Initialize loop to go through links
    lastHeatName, lastHeatId, lastHeatLink = parseHeatLink(rows[rowNum])
    rowNum += 1

    # Ignoring combine event, read first event page, read all heats of event
    if ("combine" not in lastHeatName.lower()):
        readHeatPages(compId, lastHeatId, lastHeatLink)

    # Keep finding appropriate links
    # As before, read first event page, read all heats of event
    global db
    while rowNum < len(rows):
        rowText = rows[rowNum].get_text().strip()

        # Don't care about combine events
        if ("combine" in lastHeatName.lower()):
            rowNum += 1
            continue
        # Row is a link. Read event and heats.
        elif (rows[rowNum].find('a') != None):
            lastHeatName, lastHeatId, lastHeadLink = parseHeatLink(rows[rowNum])
            readHeatPages(compId, lastHeatId, lastHeatLink)
        # Blank row
        elif (rowText == '----'):
            pass
        # Row is a couple
        else:
            parseCouple(rowText, compId, lastHeatId)

        rowNum += 1

def parseCouple(rowText, compId, lastHeatId):
    """
    Parses 'rowText' for leader and follower information

    :param rowText: Text from row containing leader and follwer information
    :param compId: id of competition
    :param lastHeatId: id of heat to which to add competitiors
    :effects: Adds competitors and entries to database
    """

    m = match('\d+\) (\d{1,3}) (.+) & (.+) \- (.+)', rowText)
    state = 'N/A'
    if (m != None):
        state = m.group(4).strip()
    else:
        m = match('\d+\) (\d{1,3}) (.+) & (.+)', rowText)
    coupleNumber = m.group(1).strip()
    leaderString = m.group(2).strip()
    leader = competitorName(leaderString)
    followerString = m.group(3).strip()
    follower = competitorName(followerString)

    global newCompetitorId
    global competitors

    # Add leader into database
    if (leader in competitors):
        leaderId = competitors[leader]
    else:
        competitors[leader] = newCompetitorId
        leaderId = newCompetitorId
        newCompetitorId += 1
        try:
            db.insert("competitors",
                      competitor_id=leaderId,
                      first_name=leader[0],
                      last_name=leader[1])
        except IntegrityError as e:
            logging.error(e);

    # Add follower into database
    if (follower in competitors):
        followerId = competitors[follower]
    else:
        competitors[follower] = newCompetitorId
        followerId = newCompetitorId
        newCompetitorId += 1
        try:
            db.insert("competitors",
                      competitor_id=followerId,
                      first_name=follower[0],
                      last_name=follower[1])
        except IntegrityError as e:
            logging.error(e)

    # Add appropriate entry to database
    try:
        db.insert("entries",
                  competition_id=compId,
                  event_id=lastHeatId,
                  lead_id=leaderId,
                  follow_id=followerId,
                  competitor_number=coupleNumber)
    except IntegrityError as e:
        logging.error(e)

def competitorName(name):
    """
    Parses name into first and last name, checking against o2cm if ambiguous

    :param name: string containing full name
    :returns: tuple (firstName, lastName)
    """

    tokens = name.split()
    if (len(tokens) < 2):
        return (name, '')
    elif (len(tokens) == 2):
        return (tokens[0], tokens[1])
    else:
        global competitorToNames
        if (name in competitorToNames):
            return competitorToNames[name]
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
            competitorToNames[name] = (firstName, lastName)
            return (firstName, lastName)
        return (name, '')

def getHeatPages(heatUrl, compId, heatId):
    """
    Returns list of pages for each round in a heat

    :param heatUrl: string url for the event
    :param compId: string competition id
    :param heatId: string id for heat
    :returns: list of bs4 objsts, each a page for a round of heatId of compId
    """

    heatUrlSimple = heatUrl.split("?")[0]
    soup = loadPage(heatUrlSimple, {'event': compId,'heatId': heatId})
    if (soup is None):
        return []

    numRounds = 1
    select = soup.find('select', id='selCount')
    if (select != None):
        numRounds = len(select.find_all('option'))

    heatPageSoups = []
    heatPageSoups.append(soup)
    for i in range(1, numRounds):
        heatPageSoups.append(loadPage(heatUrlSimple, {'event': compId, 'heatId': heatId, 'selCount': i}, True))
    return heatPageSoups

def readHeatPages(compId, heatId, heatLink):
    """
    Read all pages for rounds of 'heatId'

    :param compId: string competition id
    :param heatId: string id for heat
    :param heatLink: string link to heat
    """

    eventHeatPages = getHeatPages(heatLink, compId, heatId)
    for i in range(len(eventHeatPages)):
        readHeatPage(compId, eventHeatPages[i], heatId, i)

def readHeatPage(compId, heatPage, heatId, roundNum):
    """
    Reads page for specified round of heat, adding appropriate data to database

    :param compId: string competition id
    :param heatPage: bs4 object for results page for heat
    :param heatId: string id for heat
    :param roundNum: int round number
    :effects: adds event, results, and placements into database
    """

    tables = heatPage.find_all('table')
    keyTable = tables[len(tables)-2]
    global db
    # Read results
    numResultsTables = len(tables)-3
    # Check dupes
    eventLevel, eventCategory = parseEvent(tables[0]('tr')[2].get_text())
    if ((compId, heatId) not in heats):
        try:
            db.insert("events",
                      competition_id=compId,
                      event_id=heatId,
                      event_level=eventLevel,
                      category=eventCategory)
            heats.add((compId,heatId))
        except IntegrityError as e:
            logging.error(e)

    if (roundNum == 0 and numResultsTables > 1):
        numResultsTables -= 1

    for i in range(1, numResultsTables+1):
        resultRows = tables[i].find_all('tr')
        dance = getDance(resultRows[0].get_text().strip())

        # Determine judges
        headerRow = resultRows[1]
        judgeNumbers = []
        headerRowCells = headerRow('td', 't1b')
        numJudges = len(headerRowCells)-1 if roundNum == 0 else len(headerRowCells)
        for i in range(0, numJudges):
            text = headerRowCells[i].get_text().strip()
            if (len(text) > 0):
                judgeNumbers.append(text)

        for i in range(2, len(resultRows)):
            cells = resultRows[i]('td')
            coupleNumber = cells[0].get_text().strip()
            results = []
            for j in range(len(judgeNumbers)):
                contents = cells[j+1].get_text().strip()
                if (roundNum == 0):
                    results.append(contents)
                else:
                    results.append('t' if contents == 'X' else 'f')
            for j in range(len(judgeNumbers)):
                if (results[j] == "-"):
                    continue;
                if (roundNum == 0):
                    try:
                        db.insert("results",
                                  competition_id=compId,
                                  event_id=heatId,
                                  event_dance=dance,
                                  judge_id=judgeNumbers[j],
                                  competitor_number=coupleNumber,
                                  round=roundNum,
                                  placement=results[j],
                                  callback="f")
                    except IntegrityError as e:
                        logging.error(e)

                else:
                    try:
                        db.insert("results",
                                  competition_id=compId,
                                  event_id=heatId,
                                  event_dance=dance,
                                  judge_id=judgeNumbers[j],
                                  competitor_number=coupleNumber,
                                  round=roundNum,
                                  placement=-1,
                                  callback=results[j])
                    except IntegrityError as e:
                        logging.error(e)

            if (roundNum == 0 and numResultsTables == 1):
                placementString = cells[-2].get_text().strip()
                if (placementString != "-"):
                    eventPlacement = "%d" % int(floor(float(placementString)))
                    try:
                        db.insert("placements",
                                  competition_id=compId,
                                  event_id=heatId,
                                  competitor_number=coupleNumber,
                                  placement=eventPlacement)
                    except IntegrityError as e:
                        logging.error(e)


    if (roundNum == 0 and numResultsTables > 1):
        finalResultsTable = tables[numResultsTables+1]('tr')
        for i in range(2, len(finalResultsTable)):
            resultRow = finalResultsTable[i]('td')
            coupleNumber = resultRow[0].get_text().strip()
            eventPlacement = resultRow[-1].get_text().strip()
            if (eventPlacement != "-"):
                try:
                    db.insert("placements",
                              competition_id=compId,
                              event_id=heatId,
                              competitor_number=coupleNumber,
                              placement=eventPlacement)
                except IntegrityError as e:
                    logging.error(e)


    # Read judges
    keyRows = keyTable('tr')
    judgeRowBeginning = 1
    while (True):
        currRow = keyRows[judgeRowBeginning]
        cells = currRow('td')
        if (len(cells) >= 2 and 'class' in cells[1].attrs and \
            't1b' in cells[1]['class'] and len(cells[1].get_text().strip()) > 0):
            break
        judgeRowBeginning += 1

    for i in range(judgeRowBeginning+1, len(keyRows), 2):
        cells = keyRows[i].find_all('td')
        judgeNum = cells[0].get_text().strip()
        judgeName = cells[1].get_text().strip()
        if ((compId, judgeNum) not in judges):
            judges[(compId, judgeNum)] = judgeName
            try:
                db.insert("judges",
                          competition_id=compId,
                          judge_id=judgeNum,
                          judge_name=judgeName)
            except IntegrityError as e:
                logging.error(e)

class Competition(object):
    def __init__(self, compId, name, year, date):
        self.compId = compId
        self.compName = name
        dateString = "%s %s" % (year, date)
        self.date = dateString

    def __str__(self):
        return "%s (%s), %s" % (self.compName, self.compId, self.date)

if __name__ == '__main__':
    main()
