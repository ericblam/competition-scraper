import datetime
import unittest

from pg import DB

from dbObjects import *
from dbAccessor import *

db = DB(dbname = 'ballroom_competitions',
        host   = 'localhost',
        port   =  5432,
        user   = 'postgres',
        passwd = 'postgres')

class TestInserts(unittest.TestCase):

    def test_competition_insert(self):
        with open('schema_setup.sql', "r") as schemaFile:
            db.query(schemaFile.read())

        val = ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 4, 2))
        queryVal = val[0:len(val)-1] + (str(val[len(val)-1]),)

        x = Competition(*queryVal)
        insertCompetition(x)

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], val)        

    def test_competition_list_insert(self):
        with open('schema_setup.sql', "r") as schemaFile:
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
        self.assertEqual(res[0], val[0])
        self.assertEqual(res[1], val[1])

if __name__ == '__main__':
    unittest.main()
