import logging
import re

from webparser.abstractparser import AbstractWebParser
from webparser.parsertype import ParserType
import util.webutils
import util.crawlerutils
from util.configutils import getConfigProperty
from util.dbutils import createConnFromConfig
from util.logutils import LogTimer, TimerType

class O2cmMainParser(AbstractWebParser):

    def __init__(self, q, config):
        super(O2cmMainParser, self).__init__(q, config)

    def parse(self, htmlDOM, data):
        with LogTimer('Parsing main', TimerType.PARSE):
            compsOfInterest = getConfigProperty(self.config, 'scraper', 'o2cm', 'comps', default=[])

            compLinks = htmlDOM.find_all('a')
            yearInput = htmlDOM.find_all('input', id='inyear')[0]
            year = int(yearInput['value'])
            monthInput = htmlDOM.find_all('input', id='inmonth')[0]
            month = int(monthInput['value'])

            logging.info("Scraping o2cm: %d %d" % (year, month))

            minYear = int(yearInput['min'])
            month -= 1

            if month < 1:
                month = 12
                year -= 1

            if year >= minYear:
                self._createNextMainPageRequest(year, month)

            for tag in compLinks:
                date = tag.parent.previous_sibling.previous_sibling.string.strip()
                compName = tag.get_text()
                link = tag['href']
                m = re.match(r'event[23].asp\?event=([a-zA-Z]{0,4}\d{0,5}[a-zA-Z]?)&.*', link)
                compId = m.group(1).lower()

                if (len(compsOfInterest) == 0 or compId in compsOfInterest):
                    m = re.match(r'([a-z]+)\d+.*', compId)
                    # compCode = m.group(1)
                    fullDate = date + " " + str(year)

                    self._resetData(compId)

                    self._storeData(compId, compName, fullDate)
                    self._createCompPageRequest(compId, compName)

    def _resetData(self, compId):
        with createConnFromConfig(self.config) as conn, LogTimer("Cleaning {}".format(compId), TimerType.DB):
            conn.query("DELETE FROM o2cm.judge WHERE comp_id = $1", compId)
            conn.query("DELETE FROM o2cm.round_result WHERE comp_id = $1", compId)
            conn.query("DELETE FROM o2cm.round_placement WHERE comp_id = $1", compId)
            conn.query("DELETE FROM o2cm.entry WHERE comp_id = $1", compId)
            conn.query("DELETE FROM o2cm.event WHERE comp_id = $1", compId)
            conn.query("DELETE FROM o2cm.competition WHERE comp_id = $1", compId)

    def _storeData(self, compId, compName, compDate):
        with createConnFromConfig(self.config) as conn, LogTimer("Saving {}".format(compId), TimerType.DB):
            conn.insert("o2cm.competition",
                        comp_id=compId,
                        comp_name=compName,
                        comp_date=compDate)

    def _createNextMainPageRequest(self, year, month):
        url = 'http://results.o2cm.com'
        requestData = {
            'inyear': year,
            'inmonth': month
        }
        nextRequest = util.webutils.WebRequest(url, 'POST', requestData)
        newTask = util.crawlerutils.ScraperTask(
            nextRequest,
            None,
            ParserType.O2CM_MAIN)
        self.q.put(newTask)

    def _createCompPageRequest(self, compId, compName=""):
        url = 'http://results.o2cm.com/event3.asp'
        requestData = {
            'selDiv': '',
            'selAge': '',
            'selSkl': '',
            'selSty': '',
            'selEnt': '',
            'submit': 'OK',
            'event': compId
        }
        nextRequest = util.webutils.WebRequest(url, 'POST', requestData)
        nextData = {
            "compId": compId
        }
        newTask = util.crawlerutils.ScraperTask(
            nextRequest,
            nextData,
            ParserType.O2CM_COMP)
        self.q.put(newTask)
