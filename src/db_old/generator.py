import argparse
import json
import os

OBJECTS_FILE_NAME = 'dbobjects'
ACCESSOR_FILE_NAME = 'dbaccessor'

_dir = os.path.dirname(__file__) + "/"

TABLE_NAME = 'name'
TABLE_COLUMNS = 'columns'
TABLE_PK = 'primaryKeys'
TABLE_FK = 'foreignKeys'
TABLE_COL_NAME = 'name'
TABLE_COL_TYPE = 'type'

def fileWrite(f, s):
    if f is not None:
        f.write(s)
    else:
        print(s)

def dbNameToDelimited(name, delimiter="", caps=False):
    tokens = name.split("_")
    if caps:
        return delimiter.join(x.title() for x in tokens)
    return tokens[0] + delimiter.join(x.title() for x in tokens[1:])

def writeDboHeader(dbObjectFile):
    fileWrite(dbObjectFile, '""" File automatically generated with generator.py """\n\n')

def writeDbaHeader(dbAccessorFile):
    s = ""
    s += '""" File automatically generated with generator.py """\n\n'
    s += 'from db.' + OBJECTS_FILE_NAME +' import *\n\n'
    s += 'from pg import DB, IntegrityError\n\n'
    s += 'import os\n\n_dir = os.path.dirname(__file__) + "/"\n\n'
    s += "def createConn(config):\n"
    s += "    return DB(dbname = config['dbname'],\n"
    s += "              host   = config['host'],\n"
    s += "              port   = config['port'],\n"
    s += "              user   = config['user'],\n"
    s += "              passwd = config['password'])\n\n"
    fileWrite(dbAccessorFile, s)

def writeDropsToSchema(schemaFile, table):
    s = "drop table %s;\n" % table[TABLE_NAME]
    fileWrite(schemaFile, s)

    return s

def writeTableToSchema(schemafile, table):
    s = "\n"
    s += "create table %s (\n" % table[TABLE_NAME]
    tab = "        "
    for column in table[TABLE_COLUMNS]:
        s += "%s%-20s %s\n" % (tab, column[TABLE_COL_NAME], column[TABLE_COL_TYPE])
        tab = "      , "
    if len(table[TABLE_PK]) > 0:
        s += "%sprimary key (%s)\n" % (tab, ", ".join(table[TABLE_PK]))
    s += ");\n"

    fileWrite(schemafile, s)

    return s

def writeDbReset(dbAccessorFile, sql):
    s = ""
    s += 'def dbReset(conn):\n'
    s += '    """\n'
    s += '    Resets and reconfigures database\n'
    s += '    """\n\n'
    s += '    conn.query("""\n%s\n    """)\n\n' % sql

    dbAccessorFile.write(s)

    return s

def writeDbResetComp(dbAccessorFile, tables):
    tab = "        "
    sql = ""
    numCompTables = 0
    for table in tables:
        for col in table[TABLE_COLUMNS]:
            if col[TABLE_COL_NAME] == 'comp_id':
                sql += tab + "delete from %s where comp_id = '%%s';\n" % table[TABLE_NAME]
                numCompTables += 1
                break
    s = ""
    s += 'def dbClearComp(conn, compId):\n'
    s += '    """\n'
    s += '    Removes data for comp compId\n'
    s += '    """\n\n'
    s += '    conn.query("""\n%s    """ %% (%s))\n\n' % (sql, ",".join(['compId'] * numCompTables))

    dbAccessorFile.write(s)

    return s

def writeDbObject(f, table):
    className = dbNameToDelimited(table[TABLE_NAME], "", True)
    titleName = dbNameToDelimited(table[TABLE_NAME], " ", True)

    columns = table[TABLE_COLUMNS]
    columnNames = [col[TABLE_COL_NAME] for col in columns]

    s = ""
    s += "class %s(object):\n" % className
    s += '    """\n'
    s += '    %s wrapper class\n' % titleName
    s += '    """\n\n'
    s += '    def __init__(self,\n'
    s += ',\n'.join('                 ' + colName for colName in columnNames)
    s += '):\n'
    s += '\n'.join('        self.d_%s = %s' % (dbNameToDelimited(colName), colName) for colName in columnNames)
    s += '\n\n'
    s += '    def __str__(self):\n'

    toStringFormat = ", ".join("d_%s='%%s'" % dbNameToDelimited(colName) for colName in columnNames)
    formatTuple =    ", ".join("self.d_%s" % dbNameToDelimited(colName) for colName in columnNames)

    s += '        return \"{%s: %s}\" %% (%s)\n' % (className, toStringFormat, formatTuple)
    s += '\n\n\n'

    f.write(s)

    return s

def writeDbAccessor(f, table):
    tableName = table[TABLE_NAME]
    objectName = dbNameToDelimited(tableName, "", False)
    className = dbNameToDelimited(tableName, "", True)
    titleName = dbNameToDelimited(tableName, " ", True)
    columns = table[TABLE_COLUMNS]
    columnNames = [col[TABLE_COL_NAME] for col in columns]

    s = ""

    s += 'def insert%s(conn, %s):\n' % (className, objectName)
    s += '    """\n'
    s += '    Function to insert single %s object into database\n' % className
    s += '    """\n\n'
    s += '    conn.query("INSERT INTO %s"\n' % tableName
    s += '               "(%s) "\n' % ', '.join(columnNames)
    s += '               "VALUES "\n'
    formatTuple = ', '.join("'%s'" for col in columnNames)
    spaceString = ',\n' + ' ' * (14 + len(formatTuple) + 8)
    objectTuple = spaceString.join("%s.__dict__['%s']" % (objectName, 'd_' + dbNameToDelimited(col, "", False)) for col in columnNames)

    s += '               "(%s)" %% (%s))\n\n' % (formatTuple, objectTuple)

    s += 'def insert%sList(conn, %sList):\n' % (className, objectName)
    s += '    """\n'
    s += '    Function to insert list of %s objects into database\n' % className
    s += '    """\n\n'
    s += '    values = []\n'
    s += '    for %s in %sList:\n' % (objectName, objectName)
    s += '        values.append('
    formatTuple = ', '.join("'%s'" for col in columnNames)
    spaceString = ',\n' + ' ' * (22 + len(formatTuple) + 8)
    objectTuple = spaceString.join("%s.__dict__['%s']" % (objectName, 'd_' + dbNameToDelimited(col, "", False)) for col in columnNames)
    s += '"(%s)" %% (%s))\n\n' % (formatTuple, objectTuple)
    s += '    conn.query("INSERT INTO %s"\n' % tableName
    s += '               "(%s) "\n' % ', '.join(columnNames)
    s += '               "VALUES "\n'
    s += '               "%s" % ",".join(values))\n\n'

    s += 'def selectFrom%s(conn):\n' % className
    s += '    """\n'
    s += '    Does select * from %s\n' % tableName
    s += '    Exercise caution - this retrieves all rows of %s\n' % tableName
    s += '    """\n\n'
    s += '    dbRes = conn.query("SELECT * FROM %s")\n' % tableName
    s += '    res = []\n'
    s += '    for row in dbRes.dictresult():\n'
    columnList = ", ".join('row["%s"]' % p for p in columnNames)
    s += '        res.append(%s(%s))\n' % (className, columnList)
    s += '    return res\n\n'

    f.write(s)
    return s

def writeDbObjectWrapper(f, tables):
    s = ""
    s += 'class DbObjectContainer(object):\n'
    s += '    """\n'
    s += '    Container Class to contain all DbObject\n'
    s += '    """\n\n'
    s += "    def __init__(self):\n"
    for table in tables:
        s += "        self.d_%s = []\n" % table[TABLE_NAME]
    s += "\n"

    for table in tables:
        tableName = table[TABLE_NAME]
        className = dbNameToDelimited(tableName, "", True)
        objectName = dbNameToDelimited(tableName, "", False)
        s += "    def add%s(self, %s):\n" % (className, objectName)
        s += "        self.d_%s.append(%s)\n" % (tableName, objectName)
        s += "\n"

    s += "    def dumpToDb(self, conn):\n"
    for table in tables:
        tableName = table[TABLE_NAME]
        className = dbNameToDelimited(tableName, "", True)
        s += "        if len(self.d_%s) > 0:\n" % tableName
        s += "            insert%sList(conn, self.d_%s)\n" % (className, tableName)
    s += "\n\n"

    f.write(s)
    return s



def main():
    with open(_dir + "schema.json", "r") as jsonSchemaFile, \
         open(_dir + "comp_schema.sql", "w") as schemaFile, \
         open(_dir + OBJECTS_FILE_NAME + ".py", "w") as dbObjectFile, \
         open(_dir + ACCESSOR_FILE_NAME + ".py", "w") as dbAccessorFile:

        writeDboHeader(dbObjectFile)
        writeDbaHeader(dbAccessorFile)

        schema = json.loads(jsonSchemaFile.read())
        schemaSql = ""
        for table in schema:
            schemaSql += writeDropsToSchema(schemaFile, table)

        for table in schema:
            schemaSql += writeTableToSchema(schemaFile, table)

        writeDbReset(dbAccessorFile, schemaSql)
        writeDbResetComp(dbAccessorFile, schema)

        for table in schema:
            writeDbObject(dbObjectFile, table)
            writeDbAccessor(dbAccessorFile, table)

        writeDbObjectWrapper(dbAccessorFile, schema)

if __name__ == "__main__":
    main()
