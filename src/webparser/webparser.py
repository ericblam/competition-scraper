from enum import Enum
from webparser.o2cm_main import O2cmMainParser

class ParserType(Enum):
    O2CM_MAIN = 1
    O2CM_COMP = 2
    O2CM_EVENTS = 3
    O2CM_HEAT = 4

_PARSERS = {
    ParserType.O2CM_MAIN: O2cmMainParser,
    ParserType.O2CM_COMP: None,
    ParserType.O2CM_EVENTS: None,
    ParserType.O2CM_HEAT: None
}

# TODO: IMPLEMENT THIS
def getParserHint(request):
    return ParserType.O2CM_MAIN

"""
Returns a WebParser object
"""
def ParserFactory(q, conn, parserType):
    try:
        return _PARSERS[parserType](q, conn)
    except KeyError:
        return None
