import re

def dbNameConvert(name, delimiter="", caps=False):
    tokens = name.split("_")
    if caps:
        return delimiter.join(x.title() for x in tokens)
    return tokens[0] + delimiter.join(x.title() for x in tokens[1:])

schemaFile = open("schema_setup.sql", "r")
dbFile = open("dbObjects.py", "w")

dbFile.write('""" File automatically generated with generator.py """\n\n')
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
        objectName = dbNameConvert(tableName, "", True)
        titleName = dbNameConvert(tableName, " ", True)

        dbFile.write('class %s(object):\n'
        '    """\n'
        '    %s wrapper class\n'
        '    """\n'
        '\n'
        '    def __init__(self,\n' % (objectName, titleName))
        
        dbFile.write(",\n".join('                 ' + x for x in properties))
        dbFile.write('):\n')
        dbFile.write("\n".join('        self.d_%s = %s' % ((dbNameConvert(x),) * 2) for x in properties))
        dbFile.write("\n\n\n")
        
        isTable = False
        properties = []
        continue

    if isTable:
        m = re.match("\s*,?\s*([^\s]+)", line)
        properties.append(m.group(1))

        
dbFile.close()
schemaFile.close()
