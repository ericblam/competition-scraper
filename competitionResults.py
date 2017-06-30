from enum import Enum
from pg import DB
from pprint import pprint

class Page(Enum):
    HOME = 0
    COMP = 1
    EVENT = 2
    ROUND = 3

db = None
active = True
page = Page.HOME
compId = None

def main():
    global db
    db = DB(dbname='ballroom_competitions',
            host='localhost',
            port=5432,
            user='postgres',
            passwd='postgres')

    while (active):
        print()
        handle()

def handle():
    global page
    if (page == Page.HOME):
        handleHome()
    elif (page == Page.COMP):
        handleComp()
    elif (page == Page.EVENT):
        page = Page.HOME
    elif (page == Page.ROUND):
        page = Page.HOME
    else:
        page = Page.HOME

def handleHome():
    menu = "\n".join(['\tls\t\t\t\t- list comps',
                      '\tcomp [compId]\t\t\t- go to comp',
                      '\tycn [firstName] [lastName]\t- calculate points for competitor',
                      '\texit'])
    print("Home menu")
    print(menu)
    print()

    userInput = input().strip().split()
    print()
    
    if (userInput[0] == 'exit' or userInput[0] == 'quit' or userInput[0] == 'q'):
        global active
        active = False
    elif (userInput[0] == 'l' or userInput[0] == 'ls' or userInput[0] == 'lc'):
        global db
        result = db.query("select competition_id, comp_name from competitions").getresult()
        for line in result:
            print(line[0], '\t', line[1])
    elif (userInput[0] == 'c' or userInput[0] == 'comp'):
        if (len(userInput) < 2):
            print("Require competition id")
        else:
            global page
            global compId
            page = Page.COMP
            compId = userInput[1]
    elif (userInput[0] == 'y' or userInput[0] == 'ycn' or userInput[0] == 'p'):
        if (len(userInput) < 3):
            print("Require first AND last name")
        else:
            ycn(userInput[1], userInput[2])
    else:
        print("Invalid input")

def handleComp():
    global db
    global compId
    global page
    result = db.query("select * from competitions where competition_id = '%s'" % compId).getresult()
    if (len(result) == 0):
        print("%s not a valid competition id" % compId)
        page = Page.HOME
        return

    menu = "\n".join(['\tls\t\tlist events',
                      '\tback'])
    print("%s, %s %s" % (result[0][2], result[0][4], result[0][3]))
    print(menu)
    print()

    userInput = input().strip().split()
    print()

    if (userInput[0] == 'b' or userInput[0] == 'back' or userInput[0] == 'q'):
        page = Page.HOME
        compId = None
    elif (userInput[0] == 'l' or userInput[0] == 'ls' or userInput[0] == 'le'):
        result = db.query("select * from events where competition_id = '%s'" % compId).getresult()
        
    else:
        print("Incorrect input")

def ycn(firstName, lastName):
    global db
    
    leadPoints = {}
    with open("ycn_lead.sql") as relevantEventQuery:
        leadResult = db.query(relevantEventQuery.read() % (firstName, lastName))
        leadPoints = ycnResult(leadResult)
        printYcn(leadPoints)

    followPoints = {}
    with open("ycn_follow.sql") as relevantEventQuery:
        followResult = db.query(relevantEventQuery.read() % (firstName, lastName))
        followPoints = ycnResult(followResult)
        printYcn(followPoints)

def ycnResult(databaseResult):
    result = databaseResult.getresult()
    placementToPoints = {1:3, 2:2, 3:1, 4:1, 5:1, 6:1}
    levelToNum = {'Bronze': 0,
                  'Silver': 1,
                  'Gold': 2,
                  'Novice': 3,
                  'Pre-Champ': 4,
                  'Championship': 5}
    numToLevel = dict(zip(levelToNum.values(), levelToNum.keys()))
    
    points = {
        'Smooth': {
            'Waltz': [0,0,0,0,0,0],
            'Tango': [0,0,0,0,0,0],
            'Foxtrot': [0,0,0,0,0,0],
            'V. Waltz': [0,0,0,0,0,0],
            'Peabody': [0,0,0,0,0,0]
        },
        'Standard': {
            'Waltz': [0,0,0,0,0,0],
            'Quickstep': [0,0,0,0,0,0],
            'Tango': [0,0,0,0,0,0],
            'Foxtrot': [0,0,0,0,0,0],
            'V. Waltz': [0,0,0,0,0,0]
        },
        'Rhythm': {
            'Cha Cha': [0,0,0,0,0,0],
            'Rumba': [0,0,0,0,0,0],
            'Swing': [0,0,0,0,0,0],
            'Mambo': [0,0,0,0,0,0],
            'Bolero': [0,0,0,0,0,0]
        },
        'Latin': {
            'Cha Cha': [0,0,0,0,0,0],
            'Rumba': [0,0,0,0,0,0],
            'Samba': [0,0,0,0,0,0],
            'Jive': [0,0,0,0,0,0],
            'Paso Doble': [0,0,0,0,0,0]
        }
    }
    for line in result:
        (compId, eventId, eventLevel, eventCategory, eventDance, eventPlacement) = line
        if (eventCategory not in points):
            points[eventCategory] = {}
        if (eventDance not in points[eventCategory]):
            points[eventCategory][eventDance] = [0,0,0,0,0,0]
        if (eventLevel == 'Syllabus'):
            eventLevel = 'Bronze'
        if (eventLevel == 'Newcomer'):
            continue
            
        eventLevelNum = levelToNum[eventLevel]
        numPoints = placementToPoints[eventPlacement]
        points[eventCategory][eventDance][eventLevelNum] += numPoints

        if (eventLevelNum > 0):
            points[eventCategory][eventDance][eventLevelNum-1] += numPoints * 2
        if (eventLevelNum > 1):
            for i in range(eventLevelNum-1):
                points[eventCategory][eventDance][i] += 7        
    print(databaseResult)
    return points

def printYcn(points):
    orderedCategories = ['Smooth', 'Standard', 'Rhythm', 'Latin']
    orderedDances = {
        'Smooth': ['Waltz', 'Tango', 'Foxtrot', 'V. Waltz', 'Peabody'],
        'Standard': ['Waltz', 'Quickstep', 'Tango', 'Foxtrot', 'V. Waltz'],
        'Rhythm': ['Cha Cha', 'Rumba', 'Swing', 'Mambo', 'Bolero'],
        'Latin': ['Cha Cha', 'Rumba', 'Samba', 'Jive', 'Paso Doble']
    }
    result =  "           |            | Bronze | Silver | Gold \n"
    result += "===========+============+========+========+======\n"
    for category in orderedCategories:
        for dance in orderedDances[category]:
            result += " %9s | %10s |    %3d |    %3d | %3d \n" % (category, dance, points[category][dance][0], points[category][dance][1], points[category][dance][2])
        result += "-----------+------------+--------+--------+------\n"

    print(result)
    

if __name__ == "__main__":
    main()
