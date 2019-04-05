from webparser.o2cm_main import O2cmMainParser
from webparser.o2cm_comp import O2cmCompParser
from webparser.parsertype import ParserType

_PARSERS = {
    ParserType.O2CM_MAIN: O2cmMainParser,
    ParserType.O2CM_COMP: O2cmCompParser,
    ParserType.O2CM_EVENTS: None,
    ParserType.O2CM_HEAT: None
}

# TODO: IMPLEMENT THIS
def getParserHint(request):
    return ParserType.O2CM_MAIN

"""
Returns a WebParser object
"""
def ParserFactory(q, conn, config, parserType):
    try:
        return _PARSERS[parserType](q, conn, config)
    except KeyError:
        return None
