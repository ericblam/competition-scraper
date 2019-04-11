from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils

class O2cmHeatParser(AbstractWebParser):

    def __init__(self, q, conn, config=None):
        super(O2cmHeatParser, self).__init__(q, conn, config)

    def parse(self, htmlDOM, data):

        # find all tables
        # last table will be for listing competitors and judges
        # if it is a final with multiple dances, there will also be a table for the summary

        tables = htmlDOM.find_all('table', class_='t1n')
        numResultTables = len(tables) - 1
        resultTables = tables[:numResultTables]
        summaryTable = None
        coupleAndJudgesTable = tables[-1]
        if data["roundNum"] == 0 and numResultTables > 1: # multi-dance final
            resultTables = tables[:numResultTables-1]
            summaryTable = tables[numResultTables-1]

        for table in resultTables:
            parseTable(table)

def parseTable(table):
    rows = table.find_all('tr')
    titleRow = rows[0]
    headerRow = rows[1]
    resultRows = rows[2:]

    title = titleRow.find('td').get_text().strip()
    headers = cleanRow(headerRow)

    # everything before first space is judge numbers, after is scoring-related
    # skip first column because it is blank
    spaceIndex = headers[1:].index('') + 1
    judgeHeaders = headers[1:spaceIndex]
    scoringHeaders = headers[spaceIndex+1:]

    for r in resultRows:
        row = cleanRow(r)


def cleanRow(row):
    return list(map(lambda td: td.get_text().strip(), row.find_all('td')))
