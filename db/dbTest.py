import datetime
import os
import unittest

from pg import DB

from dbObjects import *
from dbAccessor import *

_dir = os.path.dirname(__file__) + "/"

db = DB(dbname = 'ballroom_competitions',
        host   = 'localhost',
        port   =  5432,
        user   = 'postgres',
        passwd = 'postgres')

class TestInserts(unittest.TestCase):

    def test_competition_insert(self):
        with open(_dir + 'schema_setup.sql', "r") as schemaFile:
            db.query(schemaFile.read())

        val = ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 4, 2))
        queryVal = val[0:len(val)-1] + (str(val[len(val)-1]),)

        x = Competition(*queryVal)
        insertCompetition(x)

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(val, res[0])

    def test_competition_list_insert(self):
        with open(_dir + 'schema_setup.sql', "r") as schemaFile:
            db.query(schemaFile.read())

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(Competition(*v))
        insertCompetitionList(comps)

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), len(vals))
        self.assertEqual(vals[0], res[0])
        self.assertEqual(vals[1], res[1])

    def test_full_reset(self):
        with open(_dir + 'schema_setup.sql', "r") as schemaFile:
            db.query(schemaFile.read())

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(Competition(*v))
        insertCompetitionList(comps)

        dbReset()

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 0)

    def test_single_reset(self):
        with open(_dir + 'schema_setup.sql', "r") as schemaFile:
            db.query(schemaFile.read())

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(Competition(*v))
        insertCompetitionList(comps)

        dbClearComp("rpi17")
        
        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(vals[0], res[0])
        
if __name__ == '__main__':
    unittest.main()
