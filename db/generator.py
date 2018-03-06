import re

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
    dbaFile.write('    pass\n\n')

schemaFile = open("schema_setup.sql", "r")
dbObjectFile = open("dbObjects.py", "w")
dbAccessorFile = open("dbAccessor.py", "w")

dbObjectFile.write('""" File automatically generated with generator.py """\n\n')
dbAccessorFile.write('""" File automatically generated with generator.py """\n\n')
dbAccessorFile.write('from pg import DB, IntegrityError\n\n')
dbAccessorFile.write("_db = DB(dbname = 'ballroom_competitions',\n")
dbAccessorFile.write("         host   = 'localhost',\n")
dbAccessorFile.write("         port   =  5432,\n")
dbAccessorFile.write("         user   = 'postgres',\n")
dbAccessorFile.write("         passwd = 'postgres')\n\n")

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
