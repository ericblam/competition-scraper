import re

import os
_dir = os.path.dirname(__file__) + "/"

def dbNameToDelimited(name, delimiter="", caps=False):
    tokens = name.split("_")
    if caps:
        return delimiter.join(x.title() for x in tokens)
    return tokens[0] + delimiter.join(x.title() for x in tokens[1:])

def writeDbObject(dboFile, tableName, properties):
    className = dbNameToDelimited(tableName, "", True)
    titleName = dbNameToDelimited(tableName, " ", True)

    dboFile.write('class %s(object):\n'
                       '    """\n'
                       '    %s wrapper class\n'
                       '    """\n'
                       '\n'
                       '    def __init__(self,\n' % (className, titleName))

    dboFile.write(",\n".join('                 ' + x for x in properties))
    dboFile.write('):\n')
    dboFile.write("\n".join('        self.d_%s = %s' % (dbNameToDelimited(x), x) for x in properties))
    dboFile.write("\n\n\n")

def writeDbReset(dbaFile):
    dbaFile.write('def dbReset():\n')
    dbaFile.write('    """\n')
    dbaFile.write('    Resets and reconfigures database\n')
    dbaFile.write('    """\n\n')
    dbaFile.write('    with open(_dir + "schema_setup.sql") as sqlClearing:\n')
    dbaFile.write('        _db.query(sqlClearing.read())\n\n')

def writeDbResetComp(dbaFile):
    dbaFile.write('def dbClearComp(compId):\n')
    dbaFile.write('    """\n')
    dbaFile.write('    Removes data for comp compId\n')
    dbaFile.write('    """\n\n')
    dbaFile.write('    with open(_dir + "reset_comp_data.sql") as queryFile:\n')
    dbaFile.write('        query = ""\n')
    dbaFile.write('        for line in queryFile:\n')
    dbaFile.write('            query += line % compId\n')
    dbaFile.write('        _db.query(query)\n\n')

def writeDbAccessor(dbaFile, tableName, properties):
    objectName = dbNameToDelimited(tableName, "", False)
    className = dbNameToDelimited(tableName, "", True)
    titleName = dbNameToDelimited(tableName, " ", True)
    dbaFile.write('def insert%s(%s):\n' % (className, objectName))
    dbaFile.write('    """\n')
    dbaFile.write('    Function to insert single %s object into database\n' % className)
    dbaFile.write('    """\n\n')
    dbaFile.write('    _db.query("INSERT INTO %s"\n' % tableName)
    dbaFile.write('              "(%s) "\n' % ', '.join(properties))
    dbaFile.write('              "VALUES "\n')
    formatTuple = ', '.join("'%s'" for x in properties)
    spaceString = ',\n' + ' ' * (14 + len(formatTuple) + 8)
    objectTuple = spaceString.join("%s.__dict__['%s']" % (objectName, 'd_' + dbNameToDelimited(x, "", False)) for x in properties)
    dbaFile.write('              "(%s)" %% (%s))\n\n' % (formatTuple, objectTuple))

    dbaFile.write('def insert%sList(%sList):\n' % (className, objectName))
    dbaFile.write('    """\n')
    dbaFile.write('    Function to insert list of %s objects into database\n' % className)
    dbaFile.write('    """\n\n')
    dbaFile.write('    values = []\n')
    dbaFile.write('    for %s in %sList:\n' % (objectName, objectName))
    dbaFile.write('        values.append(')
    formatTuple = ', '.join("'%s'" for x in properties)
    spaceString = ',\n' + ' ' * (22 + len(formatTuple) + 8)
    objectTuple = spaceString.join("%s.__dict__['%s']" % (objectName, 'd_' + dbNameToDelimited(x, "", False)) for x in properties)
    dbaFile.write('"(%s)" %% (%s))\n\n' % (formatTuple, objectTuple))
    dbaFile.write('    _db.query("INSERT INTO %s"\n' % tableName)
    dbaFile.write('              "(%s) "\n' % ', '.join(properties))
    dbaFile.write('              "VALUES "\n')
    dbaFile.write('              "%s" % ",".join(values))\n\n')

    dbaFile.write('def selectFrom%s():\n' % className)
    dbaFile.write('    """\n')
    dbaFile.write('    Does select * from %s\n' % tableName)
    dbaFile.write('    Exercise caution - this retrieves all rows of %s\n' % tableName)
    dbaFile.write('    """\n\n')
    dbaFile.write('    dbRes = _db.query("SELECT * FROM %s")\n' % tableName)
    dbaFile.write('    res = []\n')
    dbaFile.write('    for row in dbRes.dictresult():\n')
    propertyList = ", ".join('row["%s"]' % p for p in properties)
    dbaFile.write('        res.append(%s(%s))\n' % (className, propertyList))
    dbaFile.write('    return res\n\n')

schemaFile = open(_dir + "schema_setup.sql", "r")
dbObjectFile = open(_dir + "dbObjects.py", "w")
dbAccessorFile = open(_dir + "dbAccessor.py", "w")

dbObjectFile.write('""" File automatically generated with generator.py """\n\n')
dbAccessorFile.write('""" File automatically generated with generator.py """\n\n')
dbAccessorFile.write('from dbObjects import *\n\n')
dbAccessorFile.write('from pg import DB, IntegrityError\n\n')
dbAccessorFile.write('import os\n\n_dir = os.path.dirname(__file__) + "/"\n\n')
dbAccessorFile.write("_db = DB(dbname = 'ballroom_competitions',\n")
dbAccessorFile.write("         host   = 'localhost',\n")
dbAccessorFile.write("         port   =  5432,\n")
dbAccessorFile.write("         user   = 'postgres',\n")
dbAccessorFile.write("         passwd = 'postgres')\n\n")
writeDbReset(dbAccessorFile)
writeDbResetComp(dbAccessorFile)

isTable = False
tableName = ""
properties=[]
for line in schemaFile:
    if "create table" in line:
        m = re.match("create table (.*) \(", line)
        tableName = m.group(1)
        isTable = True
        continue

    if isTable and ("primary key" in line or ");" in line):
        writeDbObject(dbObjectFile, tableName, properties)
        writeDbAccessor(dbAccessorFile, tableName, properties)

        isTable = False
        properties = []
        continue

    if isTable:
        m = re.match("\s*,?\s*([^\s]+)", line)
        properties.append(m.group(1))

dbAccessorFile.close()
dbObjectFile.close()
schemaFile.close()
