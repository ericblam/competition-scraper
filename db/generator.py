import re

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
        tableNameTokens = tableName.split("_")
        objectName = "".join(x.title() for x in tableNameTokens)
        titleName = " ".join(x.title() for x in tableNameTokens)
        
        dbFile.write('class %s(object):\n'
        '    """\n'
        '    %s wrapper class\n'
        '    """\n'
        '\n'
        '    def __init__(self,\n' % (objectName, titleName))
        
        dbFile.write(",\n".join('             ' + x for x in properties))
        dbFile.write('):\n')
        dbFile.write("\n".join('    self.d_%s = %s' % (x, x) for x in properties))
        dbFile.write("\n\n\n")
        
        isTable = False
        properties = []
        continue

    if isTable:
        m = re.match("\s*,?\s*([^\s]+)", line)
        propertyTokens = m.group(1).split("_")
        property = propertyTokens[0] + "".join(x.title() for x in propertyTokens[1:])
        properties.append(property)

        
dbFile.close()
schemaFile.close()
