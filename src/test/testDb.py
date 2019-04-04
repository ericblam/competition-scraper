#!/usr/bin/python3
# Run with python3 -m unittest test.testDb

import datetime
import os
import unittest

import db.dbobjects
import db.dbaccessor

dbConn = db.dbaccessor.createConn({
    'dbname': 'ballroom_competitions',
    'host'  : 'localhost',
    'port'  :  5432,
    'user'  : 'postgres',
    'password': 'postgres'
})

def resetDb():
    with open('db/comp_schema.sql', "r") as schemaFile:
        dbConn.query(schemaFile.read())


class TestInserts(unittest.TestCase):

    def test_competition_insert(self):
        resetDb()

        val = ('rpi17', 'RPI Dancesport Competition', datetime.date(2017, 4, 2))
        queryVal = val[0:len(val)-1] + (str(val[len(val)-1]),)
        x = db.dbobjects.Competition(*queryVal)
        db.dbaccessor.insertCompetition(dbConn, x)

        res = dbConn.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(val, res[0])

        resetDb()

    def test_competition_list_insert(self):
        resetDb()

        vals = [('rpi16', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(db.dbobjects.Competition(*v))
        db.dbaccessor.insertCompetitionList(dbConn, comps)

        res = dbConn.query('select * from competition').getresult()
        self.assertEqual(len(res), len(vals))
        self.assertEqual(vals[0], res[0])
        self.assertEqual(vals[1], res[1])

        resetDb()

    def test_full_reset(self):
        resetDb()

        vals = [('rpi16', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(db.dbobjects.Competition(*v))
        db.dbaccessor.insertCompetitionList(dbConn, comps)

        db.dbaccessor.dbReset(dbConn)

        res = dbConn.query('select * from competition').getresult()
        self.assertEqual(len(res), 0)

        resetDb()

    def test_single_reset(self):
        resetDb()

        vals = [('rpi16', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(db.dbobjects.Competition(*v))
        db.dbaccessor.insertCompetitionList(dbConn, comps)

        db.dbaccessor.dbClearComp(dbConn, "rpi17")

        res = dbConn.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(vals[0], res[0])

        resetDb()

    def test_select_single(self):
        resetDb()

        vals = [('rpi16', 'RPI Dancesport Competition', datetime.date(2016, 4, 2))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(db.dbobjects.Competition(*v))
        db.dbaccessor.insertCompetitionList(dbConn, comps)

        res = db.dbaccessor.selectFromCompetition(dbConn)
        self.assertEqual(len(res), 1)
        self.assertTrue(isinstance(res[0], db.dbobjects.Competition))
        self.assertEqual(res[0].d_compId, "rpi16")

        resetDb()

    def test_select_two(self):
        resetDb()

        vals = [('rpi16', 'RPI Dancesport Competition', datetime.date(2016, 4, 2)),
                ('rpi17', 'RPI Dancesport Competition', datetime.date(2017, 3, 25))]
        queryVals = [val[0:len(val)-1] + (str(val[len(val)-1]),) for val in vals]

        comps = []
        for v in vals:
            comps.append(db.dbobjects.Competition(*v))
        db.dbaccessor.insertCompetitionList(dbConn, comps)

        res = db.dbaccessor.selectFromCompetition(dbConn)
        self.assertEqual(len(res), 2)
        self.assertTrue(isinstance(res[0], db.dbobjects.Competition))
        self.assertTrue(isinstance(res[1], db.dbobjects.Competition))
        self.assertEqual(res[0].d_compId, "rpi16")
        self.assertEqual(res[1].d_compId, "rpi17")

        resetDb()


if __name__ == '__main__':
    unittest.main()
