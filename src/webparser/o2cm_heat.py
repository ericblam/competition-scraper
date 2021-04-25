import logging
from collections import namedtuple
from typing import List, Tuple

from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils
import util.textutils
from util.dbutils import createConnFromConfig, convertDataToFileLike
from util.logutils import LogTimer, TimerType

RoundPlacement = namedtuple('RoundPlacement', ['comp_id', 'event_id', 'round_num', 'dance', 'couple_num', 'judge_num', 'mark'])
RoundResult = namedtuple('RoundResult', ['comp_id', 'event_id', 'round_num', 'dance', 'couple_num', 'placement'])
JudgeInfo = namedtuple('JudgeInfo', ['comp_id', 'event_id', 'round_num', 'judge_num', 'judge_name'])

class O2cmHeatParser(AbstractWebParser):

    def __init__(self, q, config):
        super(O2cmHeatParser, self).__init__(q, config)

    def parse(self, htmlDOM, data):
        compId = data["compId"]
        eventId = data["eventId"]
        roundNum = data["roundNum"]

        logging.info("Scraping {}, {} Round {}".format(compId, eventId, roundNum))
        with LogTimer('Parsed {}, {} Round {}'.format(compId, eventId, roundNum), TimerType.PARSE):
            # find all tables
            # last table will be for listing competitors and judges
            # if it is a final with multiple dances, there will also be a table for the summary
            isFinal = roundNum == 0

            tables = htmlDOM.find_all('table', class_='t1n')
            numResultTables = len(tables) - 1
            resultTables = tables[:numResultTables]
            summaryTable = None
            coupleAndJudgesTable = tables[-1]

            if isFinal and numResultTables > 1: # multi-dance final
                resultTables = tables[:numResultTables-1]
                summaryTable = tables[numResultTables-1]

            placements: List[RoundPlacement] = []
            results: List[RoundResult] = []
            for table in resultTables:
                tablePlacements, tableResults = self.parseTable(compId, eventId, roundNum, table, isFinal)
                placements += tablePlacements
                results += tableResults

            judges: List[JudgeInfo] = self.parseJudgeTable(compId, eventId, roundNum, coupleAndJudgesTable, len(getJudgeHeaders(resultTables[0])))

        with LogTimer('Saving {}, {} Round {}'.format(compId, eventId, roundNum), TimerType.DB):
            self.storePlacements(placements)
            self.storeResults(results)
            self.storeJudges(judges)

    def parseTable(self, compId, eventId, roundNum, table, isFinal = True) -> Tuple[List[RoundPlacement], List[RoundResult]]:
        rows = table.find_all('tr')
        titleRow = rows[0]
        headerRow = rows[1]
        resultRows = rows[2:]

        danceName = titleRow.find('td').get_text().strip()
        headers = cleanRow(headerRow)

        placements: List[RoundPlacement] = []
        results: List[RoundResult] = []
        judgeHeaders = getJudgeHeaders(table)

        # this can theoretically be tossed away, since it is calculated and placement is in the last column
        for r in resultRows:
            row = cleanRow(r)
            coupleNum = row.pop(0)
            for j in range(len(judgeHeaders)):
                judgeMark = util.textutils.convert(row[j], int)
                if row[j] == 'X':
                    judgeMark = 1
                placements.append(RoundPlacement(compId, eventId, roundNum, danceName, coupleNum, judgeHeaders[j], judgeMark))

            placement = 0
            if isFinal:
                placement = util.textutils.convert(row[-2], float)
            else:
                placement = 1 if row[-1] == 'R' else 0

            results.append(RoundResult(compId, eventId, roundNum, danceName, coupleNum, placement))
        return placements, results

    def parseJudgeTable(self, compId, eventId, roundNum, table, numJudges) -> List[JudgeInfo]:
        rows = table.find_all('tr')
        judgeRows = rows[-2*(numJudges)+1:]

        judges: List[JudgeInfo] = []
        for row in judgeRows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            judgeNum = cells[0].get_text().strip()
            judgeName = cells[1].get_text().strip()
            judges.append(JudgeInfo(compId, eventId, roundNum, judgeNum, judgeName))
        return judges

    def storePlacements(self, placements: List[RoundPlacement]):
        with createConnFromConfig(self.config) as conn, conn.cursor() as cursor:
            cursor.copy_from(
                convertDataToFileLike(placements),
                'o2cm.round_placement',
                columns=('comp_id', 'event_id', 'round_num', 'dance', 'couple_num', 'judge_num', 'mark'),
                null='')

    def storeResults(self, results: List[RoundResult]):
        with createConnFromConfig(self.config) as conn, conn.cursor() as cursor:
            cursor.copy_from(
                convertDataToFileLike(results),
                'o2cm.round_result',
                columns=('comp_id', 'event_id', 'round_num', 'dance', 'couple_num', 'placement'))

    def storeJudges(self, judges: List[JudgeInfo]):
        with createConnFromConfig(self.config) as conn, conn.cursor() as cursor:
            cursor.copy_from(
                convertDataToFileLike(judges),
                'o2cm.judge',
                columns=('comp_id', 'event_id', 'round_num', 'judge_num', 'judge_name'))

def cleanRow(row):
    return list(map(lambda td: td.get_text().strip(), row.find_all('td')))

def getJudgeHeaders(table):
    rows = table.find_all('tr')
    headerRow = rows[1]
    headers = cleanRow(headerRow)

    # everything before first space is judge numbers, after is scoring-related
    # skip first column because it is blank
    spaceIndex = headers[1:].index('') + 1
    judgeHeaders = headers[1:spaceIndex]
    return judgeHeaders
