import argparse
import math
import re
import time
import urllib
from bs4 import BeautifulSoup
from pg import DB, IntegrityError
from tidylib import tidy_document

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
    comps = getComps(compsOfInterest)
    for comp in comps:
        try:
            db.insert("competitions",
                      competition_id=comp.compId,
                      comp_host="",
                      comp_name=comp.compName,
                      comp_year=comp.year,
                      comp_date=comp.date)
            compPage = getCompPage(comp.compId)
            print(">>>   ", comp, "   <<<")
            readCompPage(comp.compId, compPage)
        except IntegrityError as e:
            print(e)

"""
Initializes state from database
"""
def initialize():
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
    args = parser.parse_args()
    
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
        
"""
Returns list of Competition objects of interest
"""
def getComps(compsOfInterest=[]):
    url = 'http://results.o2cm.com/'
    soup = loadPage(url)
    compLinks = soup.find_all('a')
    competitions = []
    for tag in compLinks:
        year = tag.find_previous('td', 'h3').get_text().strip()
        date = tag.parent.previous_sibling.previous_sibling.string.strip()
        compName = tag.get_text()
        link = tag['href']
        m = re.match('event[23].asp\?event=([a-zA-Z]{0,4}\d{0,5}[a-zA-Z]?)&.*', link)
        compId = m.group(1)
        if (len(compsOfInterest) == 0 or compId in compsOfInterest):
            competitions.append(Competition(compId, compName, year, date))
    return competitions

"""
Loads and parses page for competition
"""
def getCompPage(compId):
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

"""
Reads whole listing of results from competition page
"""
def readCompPage(compId, compPage):
    tables = compPage.find_all('table')
    mainTable = tables[1]
    rows = mainTable.find_all('tr')

    r = 0
    while r < len(rows):
        if (rows[r].find('a') != None):
            break
        r += 1

    lastEventName = rows[r].get_text().lstrip().strip()
    lastEventLink = rows[r].find('a')['href']
    m = re.match('scoresheet\d.asp\?.+&heatid=(\w+)&.+', lastEventLink)
    lastEventId = m.group(1)
    lastEventLink = 'http://results.o2cm.com/' + lastEventLink
    r += 1
    print(lastEventName)
    if ("combine" not in lastEventName.lower()):
        eventHeatPages = getHeatPages(lastEventLink, compId, lastEventId)
        for i in range(len(eventHeatPages)):
            readHeatPage(compId, eventHeatPages[i], lastEventId, i)
    global db
    while r < len(rows):
        rowText = rows[r].get_text().strip()
        if (rows[r].find('a') != None):
            lastEventName = rowText
            lastEventLink = rows[r].find('a')['href']
            m = re.match('scoresheet\d.asp\?.+&heatid=(\w+)&.+', lastEventLink)
            lastEventId = m.group(1)
            lastEventLink = 'http://results.o2cm.com/' + lastEventLink
            print(lastEventName)
            if ("combine" in lastEventName.lower()):
                r += 1
                continue
            eventHeatPages = getHeatPages(lastEventLink, compId, lastEventId)
            for i in range(len(eventHeatPages)):
                readHeatPage(compId, eventHeatPages[i], lastEventId, i)
        elif (rowText == '----'):
            pass
        else:
            if ("combine" in lastEventName.lower()):
                r += 1
                continue
            m = re.match('\d+\) (\d{1,3}) (.+) & (.+) \- (.+)', rowText)
            state = 'N/A'
            if (m != None):
                state = m.group(4).strip()
            else:
                m = re.match('\d+\) (\d{1,3}) (.+) & (.+)', rowText)
            coupleNumber = m.group(1).strip()
            leaderString = m.group(2).strip()
            leader = competitorName(leaderString)
            followerString = m.group(3).strip()
            follower = competitorName(followerString)
            # print('%s - %s & %s from %s' % (coupleNumber, leader, follower, state))

            global newCompetitorId
            global competitors
            
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
                    print(e)

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
                    print(e)


            # Add appropriate entry to database
            try:
                db.insert("entries",
                          competition_id=compId,
                          event_id=lastEventId,
                          lead_id=leaderId,
                          follow_id=followerId,
                          competitor_number=coupleNumber)
            except IntegrityError as e:
                print(e)

        r += 1

"""
Returns (hopefully) correctly-parsed (firstName, lastName) from name
"""
def competitorName(name):
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
                    print("WARNING: multiple people named %s" % name)
                found = True
        if (found):
            competitorToNames[name] = (firstName, lastName)
            return (firstName, lastName)
        return (name, '')

"""
Returns list of pages for each round in a heat
"""
def getHeatPages(heatUrl, compId, heatId):
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

"""
Reads page for specified round of heat, adding appropriate data to database
"""
def readHeatPage(compId, heatPage, eventId, heatNum):
    tables = heatPage.find_all('table')
    keyTable = tables[len(tables)-2]
    global db
    # Read results
    numResultsTables = len(tables)-3
    # Check dupes
    eventLevel, eventCategory = parseEvent(tables[0]('tr')[2].get_text())
    if ((compId, eventId) not in heats):
        try:
            db.insert("events",
                      competition_id=compId,
                      event_id=eventId,
                      event_level=eventLevel,
                      category=eventCategory)
            heats.add((compId,eventId))
        except IntegrityError as e:
            print(e)
        
    if (heatNum == 0 and numResultsTables > 1):
        numResultsTables -= 1
        
    for i in range(1, numResultsTables+1):
        resultRows = tables[i].find_all('tr')
        dance = getDance(resultRows[0].get_text().strip())

        # Determine judges
        headerRow = resultRows[1]
        judgeNumbers = []
        headerRowCells = headerRow('td', 't1b')
        numJudges = len(headerRowCells)-1 if heatNum == 0 else len(headerRowCells)
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
                if (heatNum == 0):
                    results.append(contents)
                else:
                    results.append('t' if contents == 'X' else 'f')
            for j in range(len(judgeNumbers)):
                if (results[j] == "-"):
                    continue;
                if (heatNum == 0):
                    try:
                        db.insert("results",
                                  competition_id=compId,
                                  event_id=eventId,
                                  event_dance=dance,
                                  judge_id=judgeNumbers[j],
                                  competitor_number=coupleNumber,
                                  round=heatNum,
                                  placement=results[j],
                                  callback="f")
                    except IntegrityError as e:
                        print(e)

                else:
                    try:
                        db.insert("results",
                                  competition_id=compId,
                                  event_id=eventId,
                                  event_dance=dance,
                                  judge_id=judgeNumbers[j],
                                  competitor_number=coupleNumber,
                                  round=heatNum,
                                  placement=-1,
                                  callback=results[j])
                    except IntegrityError as e:
                        print(e)

            if (heatNum == 0 and numResultsTables == 1):
                placementString = cells[-2].get_text().strip()
                if (placementString != "-"):
                    eventPlacement = "%d" % int(math.floor(float(placementString)))
                    try:
                        db.insert("placements",
                                  competition_id=compId,
                                  event_id=eventId,
                                  competitor_number=coupleNumber,
                                  placement=eventPlacement)
                    except IntegrityError as e:
                        print(e)

                
    if (heatNum == 0 and numResultsTables > 1):
        finalResultsTable = tables[numResultsTables+1]('tr')
        for i in range(2, len(finalResultsTable)):
            resultRow = finalResultsTable[i]('td')
            coupleNumber = resultRow[0].get_text().strip()
            eventPlacement = resultRow[-1].get_text().strip()
            if (eventPlacement != "-"):
                try:
                    db.insert("placements",
                              competition_id=compId,
                              event_id=eventId,
                              competitor_number=coupleNumber,
                              placement=eventPlacement)
                except IntegrityError as e:
                    print(e)


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
                print(e)


def parseEvent(str):
    cleanString = str.lower().strip()
    level = ""
    category = ""
    if "newcomer" in cleanString:
        level = "Newcomer"
    elif "bronze" in cleanString or "beginner" in cleanString:
        level = "Bronze"
    elif "silver" in cleanString or "intermediate" in cleanString:
        level = "Silver"
    elif "gold" in cleanString or "advanced" in cleanString:
        level = "Gold"
    elif "syllabus" in cleanString:
        level = "Syllabus"
    elif "open" in cleanString:
        level = "Open"
    elif "novice" in cleanString:
        level = "Novice"
    elif "pre-champ" in cleanString:
        level = "Pre-Champ"
    elif "champ" in cleanString:
        level = "Championship"

    if "standard" in cleanString:
        category = "Standard"
    elif "smooth" in cleanString:
        category = "Smooth"
    elif "rhythm" in cleanString:
        category = "Rhythm"
    elif "latin" in cleanString:
        category = "Latin"
    elif "am." in cleanString and ("waltz" in cleanString or "tango" in cleanString or "foxtrot" in cleanString or "peabody" in cleanString):
        category = "Smooth"
    elif "am." in cleanString and ("cha cha" in cleanString or "rumba" in cleanString or "swing" in cleanString or "mambo" in cleanString or "bolero" in cleanString):
        category = "Rhythm"
    elif "intl." in cleanString and ("cha cha" in cleanString or "rumba" in cleanString or "samba" in cleanString or "jive" in cleanString or "paso" in cleanString):
        category = "Latin"
    elif "intl." in cleanString and ("waltz" in cleanString or "tango" in cleanString or "foxtrot" in cleanString or "quickstep" in cleanString):
        category = "Standard"

    return level, category

def getDance(str):
    if ("v. waltz" in str.lower() or "viennese waltz" in str.lower()):
        return "V. Waltz"
    if ("paso doble" in str.lower()):
        return "Paso Doble"
    if ("cha cha" in str.lower()):
        return "Cha Cha"
    tokens = str.split()
    return tokens[len(tokens)-1].replace("*", "")

"""
Loads a page from a url with data (uses GET if !post, else uses POST)
"""
def loadPage(url, data={}, post=False):
    request = urllib.parse.urlencode(data)
    try:
        if (not post):
            getUrl = url + ('?' if len(data) != 0 else '') + request
            response = urllib.request.urlopen(getUrl)
        else:
            response = urllib.request.urlopen(url, request.encode('ascii'))
        html_response = response.read()
        encoding = response.headers.get_content_charset('utf-8')
        decoded_html = html_response.decode(encoding)
        tidiedPage, pageErrors = tidy_document(decoded_html)
        return BeautifulSoup(tidiedPage, 'html.parser')
    except urllib.error.HTTPError:
        print("Failed to fetch %s with request: %s" % (url, request))
        return None
    # return BeautifulSoup(u, 'html.parser')

class Competition(object):
    def __init__(self, compId, name, year, date):
        self.compId = compId
        self.compName = name
        self.year = year
        self.date = date

    def __str__(self):
        return "%s (%s), %s %s" % (self.compName, self.compId, self.date, self.year)

if __name__ == '__main__':
    main()
