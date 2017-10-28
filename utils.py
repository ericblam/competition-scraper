import logging

def sigintHandler(signal, frame):
    """
    Handles SIGINT by closing log and exiting
    """

    logging.info("SIGINT Handled")
    exit(0)

def parseEvent(str):
    """
    Normalizes event name
    """

    cleanString = str.lower().strip()
    level = ""
    category = ""
    if "newcomer" in cleanString:
        level = "Newcomer"
    elif "bronze" in cleanString or "beginner" in cleanString:
        level = "Bronze"
    elif "silver" in cleanString or "intermediate" in cleanString:
        level = "Silver"
    elif "gold" in cleanString or "advanced" in cleanString:
        level = "Gold"
    elif "syllabus" in cleanString:
        level = "Syllabus"
    elif "open" in cleanString:
        level = "Open"
    elif "novice" in cleanString:
        level = "Novice"
    elif "pre-champ" in cleanString:
        level = "Pre-Champ"
    elif "champ" in cleanString:
        level = "Championship"

    if "standard" in cleanString:
        category = "Standard"
    elif "smooth" in cleanString:
        category = "Smooth"
    elif "rhythm" in cleanString:
        category = "Rhythm"
    elif "latin" in cleanString:
        category = "Latin"
    elif "am." in cleanString and ("waltz" in cleanString or "tango" in cleanString or "foxtrot" in cleanString or "peabody" in cleanString):
        category = "Smooth"
    elif "am." in cleanString and ("cha cha" in cleanString or "rumba" in cleanString or "swing" in cleanString or "mambo" in cleanString or "bolero" in cleanString):
        category = "Rhythm"
    elif "intl." in cleanString and ("cha cha" in cleanString or "rumba" in cleanString or "samba" in cleanString or "jive" in cleanString or "paso" in cleanString):
        category = "Latin"
    elif "intl." in cleanString and ("waltz" in cleanString or "tango" in cleanString or "foxtrot" in cleanString or "quickstep" in cleanString):
        category = "Standard"

    return level, category

def getDance(str):
    """
    Normalizes dance name
    """

    if ("v. waltz" in str.lower() or "viennese waltz" in str.lower()):
        return "V. Waltz"
    if ("paso doble" in str.lower()):
        return "Paso Doble"
    if ("cha cha" in str.lower()):
        return "Cha Cha"
    tokens = str.split()
    return tokens[len(tokens)-1].replace("*", "")
