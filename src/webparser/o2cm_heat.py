from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmHeatParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmHeatParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):
        print("Scraping " + data["compId"] + ", " + data["eventId"] + " Round " + str(data["roundNum"]))

        # find all tables
        # last table will be for listing competitors and judges
        # if it is a final with multiple dances, there will also be a table for the summary
        compId = data["compId"]
        eventId = data["eventId"]
        roundNum = data["roundNum"]
        isFinal = roundNum == 0

        tables = htmlDOM.find_all('table', class_='t1n')
        numResultTables = len(tables) - 1
        resultTables = tables[:numResultTables]
        summaryTable = None
        coupleAndJudgesTable = tables[-1]

        if isFinal and numResultTables > 1: # multi-dance final
            resultTables = tables[:numResultTables-1]
            summaryTable = tables[numResultTables-1]

        for table in resultTables:
            self.parseTable(compId, eventId, roundNum, table, isFinal)

        # TODO: Store judge information

    def parseTable(self, compId, eventId, roundNum, table, isFinal = True):
        rows = table.find_all('tr')
        titleRow = rows[0]
        headerRow = rows[1]
        resultRows = rows[2:]

        danceName = titleRow.find('td').get_text().strip()
        headers = cleanRow(headerRow)

        conn = self.conn

        # everything before first space is judge numbers, after is scoring-related
        # skip first column because it is blank
        spaceIndex = headers[1:].index('') + 1
        judgeHeaders = headers[1:spaceIndex]

        # this can theoretically be tossed away, since it is calculated and placement is in the last column
        scoringHeaders = headers[spaceIndex+1:]
        for r in resultRows:
            row = cleanRow(r)
            coupleNum = row.pop(0)
            for j in range(len(judgeHeaders)):
                judgeMark = row[j]
                if row[j] == 'X':
                    judgeMark = 1
                conn.insert("o2cm.round_placement",
                            comp_id=compId,
                            event_id=eventId,
                            round_num=roundNum,
                            dance=danceName,
                            couple_num=coupleNum,
                            judge_num=judgeHeaders[j],
                            mark=judgeMark)

            placement = 0
            if isFinal:
                placement = row[-2]
            else:
                placement = 1 if row[-1] == 'R' else 0

            conn.insert("o2cm.round_result",
                        comp_id=compId,
                        event_id=eventId,
                        round_num=roundNum,
                        dance=danceName,
                        couple_num=coupleNum,
                        placement=placement)

def cleanRow(row):
    return list(map(lambda td: td.get_text().strip(), row.find_all('td')))
