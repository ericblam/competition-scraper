import datetime
import os
import unittest

from pg import DB

import db.dbObjects as dbObjects
import db.dbAccessor as dbAccessor

db = DB(dbname = 'ballroom_competitions',
        host   = 'localhost',
        port   =  5432,
        user   = 'postgres',
        passwd = 'postgres')

def resetDb():
    with open('db/schema_setup.sql', "r") as schemaFile:
        db.query(schemaFile.read())


class TestInserts(unittest.TestCase):

    def test_competition_insert(self):
        resetDb()

        val = ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 4, 2))
        queryVal = val[0:len(val)-1] + (str(val[len(val)-1]),)

        x = dbObjects.Competition(*queryVal)
        dbAccessor.insertCompetition(x)

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(val, res[0])

        resetDb()

    def test_competition_list_insert(self):
        resetDb()

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(dbObjects.Competition(*v))
        dbAccessor.insertCompetitionList(comps)

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), len(vals))
        self.assertEqual(vals[0], res[0])
        self.assertEqual(vals[1], res[1])

        resetDb()

    def test_full_reset(self):
        resetDb()

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(dbObjects.Competition(*v))
        dbAccessor.insertCompetitionList(comps)

        dbAccessor.dbReset()

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 0)

        resetDb()

    def test_single_reset(self):
        resetDb()

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(dbObjects.Competition(*v))
        dbAccessor.insertCompetitionList(comps)

        dbAccessor.dbClearComp("rpi17")

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(vals[0], res[0])

        resetDb()

    def test_select_single(self):
        resetDb()

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(dbObjects.Competition(*v))
        dbAccessor.insertCompetitionList(comps)

        res = dbAccessor.selectFromCompetition()
        self.assertEqual(len(res), 1)
        self.assertTrue(isinstance(res[0], dbObjects.Competition))
        self.assertEqual(res[0].d_compId, "rpi16")

        resetDb()

    def test_select_two(self):
        resetDb()

        vals = [('rpi16', 'rpi', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(dbObjects.Competition(*v))
        dbAccessor.insertCompetitionList(comps)

        res = dbAccessor.selectFromCompetition()
        self.assertEqual(len(res), 2)
        self.assertTrue(isinstance(res[0], dbObjects.Competition))
        self.assertTrue(isinstance(res[1], dbObjects.Competition))
        self.assertEqual(res[0].d_compId, "rpi16")
        self.assertEqual(res[1].d_compId, "rpi17")

        resetDb()


if __name__ == '__main__':
    unittest.main()
