import datetime
import unittest

from pg import DB

from dbObjects import *
from dbAccessor import *

_db = DB(dbname = 'ballroom_competitions',
        host   = 'localhost',
        port   =  5432,
        user   = 'postgres',
        passwd = 'postgres')

class TestInserts(unittest.TestCase):

    def test_competition_insert(self):
        with open('schema_setup.sql', "r") as schemaFile:
            _db.query(schemaFile.read())

        val = ('rpi17', 'rpi', 'RPI Dancesport Competition', datetime.date(2017, 4, 2))
        queryVal = ('rpi17', 'rpi', 'RPI Dancesport Competition', str(datetime.date(2017, 4, 2)))

        x = Competition(*queryVal)
        insertCompetition(x)

        res = db.query('select * from competition').getresult()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], val)        

if __name__ == '__main__':
    unittest.main()
