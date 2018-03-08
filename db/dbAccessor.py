""" File automatically generated with generator.py """

from pg import DB, IntegrityError

import os

_dir = os.path.dirname(__file__) + "/"

_db = DB(dbname = 'ballroom_competitions',
         host   = 'localhost',
         port   =  5432,
         user   = 'postgres',
         passwd = 'postgres')

def dbReset():
    """
    Resets and reconfigures database
    """

    with open(_dir + "schema_setup.sql") as sqlClearing:
        _db.query(sqlClearing.read())

def dbClearComp(compId):
    """
    Removes data for comp compId
    """

    with open(_dir + "reset_comp_data.sql") as queryFile:
        query = ""
        for line in queryFile:
            query += line % compId
        _db.query(query)

def insertCompetition(competition):
    """
    Function to insert single Competition object into database
    """

    _db.query("INSERT INTO competition"
              "(comp_id, comp_prefix, comp_name, comp_date) "
              "VALUES "
              "('%s', '%s', '%s', '%s')" % (competition.__dict__['d_compId'],
                                            competition.__dict__['d_compPrefix'],
                                            competition.__dict__['d_compName'],
                                            competition.__dict__['d_compDate']))

def insertCompetitionList(competitionList):
    """
    Function to insert list of Competition objects into database
    """

    values = []
    for competition in competitionList:
        values.append("('%s', '%s', '%s', '%s')" % (competition.__dict__['d_compId'],
                                                    competition.__dict__['d_compPrefix'],
                                                    competition.__dict__['d_compName'],
                                                    competition.__dict__['d_compDate']))

    _db.query("INSERT INTO competition"
              "(comp_id, comp_prefix, comp_name, comp_date) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionEvent(competitionEvent):
    """
    Function to insert single CompetitionEvent object into database
    """

    _db.query("INSERT INTO competition_event"
              "(comp_id, event_id, event_level, category) "
              "VALUES "
              "('%s', '%s', '%s', '%s')" % (competitionEvent.__dict__['d_compId'],
                                            competitionEvent.__dict__['d_eventId'],
                                            competitionEvent.__dict__['d_eventLevel'],
                                            competitionEvent.__dict__['d_category']))

def insertCompetitionEventList(competitionEventList):
    """
    Function to insert list of CompetitionEvent objects into database
    """

    values = []
    for competitionEvent in competitionEventList:
        values.append("('%s', '%s', '%s', '%s')" % (competitionEvent.__dict__['d_compId'],
                                                    competitionEvent.__dict__['d_eventId'],
                                                    competitionEvent.__dict__['d_eventLevel'],
                                                    competitionEvent.__dict__['d_category']))

    _db.query("INSERT INTO competition_event"
              "(comp_id, event_id, event_level, category) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionEventDance(competitionEventDance):
    """
    Function to insert single CompetitionEventDance object into database
    """

    _db.query("INSERT INTO competition_event_dance"
              "(comp_id, event_id, dance) "
              "VALUES "
              "('%s', '%s', '%s')" % (competitionEventDance.__dict__['d_compId'],
                                      competitionEventDance.__dict__['d_eventId'],
                                      competitionEventDance.__dict__['d_dance']))

def insertCompetitionEventDanceList(competitionEventDanceList):
    """
    Function to insert list of CompetitionEventDance objects into database
    """

    values = []
    for competitionEventDance in competitionEventDanceList:
        values.append("('%s', '%s', '%s')" % (competitionEventDance.__dict__['d_compId'],
                                              competitionEventDance.__dict__['d_eventId'],
                                              competitionEventDance.__dict__['d_dance']))

    _db.query("INSERT INTO competition_event_dance"
              "(comp_id, event_id, dance) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionEntry(competitionEntry):
    """
    Function to insert single CompetitionEntry object into database
    """

    _db.query("INSERT INTO competition_entry"
              "(comp_id, event_id, competitor_number, leader, follwer) "
              "VALUES "
              "('%s', '%s', '%s', '%s', '%s')" % (competitionEntry.__dict__['d_compId'],
                                                  competitionEntry.__dict__['d_eventId'],
                                                  competitionEntry.__dict__['d_competitorNumber'],
                                                  competitionEntry.__dict__['d_leader'],
                                                  competitionEntry.__dict__['d_follwer']))

def insertCompetitionEntryList(competitionEntryList):
    """
    Function to insert list of CompetitionEntry objects into database
    """

    values = []
    for competitionEntry in competitionEntryList:
        values.append("('%s', '%s', '%s', '%s', '%s')" % (competitionEntry.__dict__['d_compId'],
                                                          competitionEntry.__dict__['d_eventId'],
                                                          competitionEntry.__dict__['d_competitorNumber'],
                                                          competitionEntry.__dict__['d_leader'],
                                                          competitionEntry.__dict__['d_follwer']))

    _db.query("INSERT INTO competition_entry"
              "(comp_id, event_id, competitor_number, leader, follwer) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitor(competitor):
    """
    Function to insert single Competitor object into database
    """

    _db.query("INSERT INTO competitor"
              "(competitor_id, first_name, last_name) "
              "VALUES "
              "('%s', '%s', '%s')" % (competitor.__dict__['d_competitorId'],
                                      competitor.__dict__['d_firstName'],
                                      competitor.__dict__['d_lastName']))

def insertCompetitorList(competitorList):
    """
    Function to insert list of Competitor objects into database
    """

    values = []
    for competitor in competitorList:
        values.append("('%s', '%s', '%s')" % (competitor.__dict__['d_competitorId'],
                                              competitor.__dict__['d_firstName'],
                                              competitor.__dict__['d_lastName']))

    _db.query("INSERT INTO competitor"
              "(competitor_id, first_name, last_name) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionEventPlacement(competitionEventPlacement):
    """
    Function to insert single CompetitionEventPlacement object into database
    """

    _db.query("INSERT INTO competition_event_placement"
              "(comp_id, event_id, competitor_number, placement) "
              "VALUES "
              "('%s', '%s', '%s', '%s')" % (competitionEventPlacement.__dict__['d_compId'],
                                            competitionEventPlacement.__dict__['d_eventId'],
                                            competitionEventPlacement.__dict__['d_competitorNumber'],
                                            competitionEventPlacement.__dict__['d_placement']))

def insertCompetitionEventPlacementList(competitionEventPlacementList):
    """
    Function to insert list of CompetitionEventPlacement objects into database
    """

    values = []
    for competitionEventPlacement in competitionEventPlacementList:
        values.append("('%s', '%s', '%s', '%s')" % (competitionEventPlacement.__dict__['d_compId'],
                                                    competitionEventPlacement.__dict__['d_eventId'],
                                                    competitionEventPlacement.__dict__['d_competitorNumber'],
                                                    competitionEventPlacement.__dict__['d_placement']))

    _db.query("INSERT INTO competition_event_placement"
              "(comp_id, event_id, competitor_number, placement) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionDancePlacement(competitionDancePlacement):
    """
    Function to insert single CompetitionDancePlacement object into database
    """

    _db.query("INSERT INTO competition_dance_placement"
              "(comp_id, event_id, competitor_number, placement) "
              "VALUES "
              "('%s', '%s', '%s', '%s')" % (competitionDancePlacement.__dict__['d_compId'],
                                            competitionDancePlacement.__dict__['d_eventId'],
                                            competitionDancePlacement.__dict__['d_competitorNumber'],
                                            competitionDancePlacement.__dict__['d_placement']))

def insertCompetitionDancePlacementList(competitionDancePlacementList):
    """
    Function to insert list of CompetitionDancePlacement objects into database
    """

    values = []
    for competitionDancePlacement in competitionDancePlacementList:
        values.append("('%s', '%s', '%s', '%s')" % (competitionDancePlacement.__dict__['d_compId'],
                                                    competitionDancePlacement.__dict__['d_eventId'],
                                                    competitionDancePlacement.__dict__['d_competitorNumber'],
                                                    competitionDancePlacement.__dict__['d_placement']))

    _db.query("INSERT INTO competition_dance_placement"
              "(comp_id, event_id, competitor_number, placement) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionEventResult(competitionEventResult):
    """
    Function to insert single CompetitionEventResult object into database
    """

    _db.query("INSERT INTO competition_event_result"
              "(comp_id, event_id, event_dance, judge_id, competitor_number, round, placement, callback) "
              "VALUES "
              "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (competitionEventResult.__dict__['d_compId'],
                                                                    competitionEventResult.__dict__['d_eventId'],
                                                                    competitionEventResult.__dict__['d_eventDance'],
                                                                    competitionEventResult.__dict__['d_judgeId'],
                                                                    competitionEventResult.__dict__['d_competitorNumber'],
                                                                    competitionEventResult.__dict__['d_round'],
                                                                    competitionEventResult.__dict__['d_placement'],
                                                                    competitionEventResult.__dict__['d_callback']))

def insertCompetitionEventResultList(competitionEventResultList):
    """
    Function to insert list of CompetitionEventResult objects into database
    """

    values = []
    for competitionEventResult in competitionEventResultList:
        values.append("('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (competitionEventResult.__dict__['d_compId'],
                                                                            competitionEventResult.__dict__['d_eventId'],
                                                                            competitionEventResult.__dict__['d_eventDance'],
                                                                            competitionEventResult.__dict__['d_judgeId'],
                                                                            competitionEventResult.__dict__['d_competitorNumber'],
                                                                            competitionEventResult.__dict__['d_round'],
                                                                            competitionEventResult.__dict__['d_placement'],
                                                                            competitionEventResult.__dict__['d_callback']))

    _db.query("INSERT INTO competition_event_result"
              "(comp_id, event_id, event_dance, judge_id, competitor_number, round, placement, callback) "
              "VALUES "
              "%s" % ",".join(values))

def insertCompetitionEventJudge(competitionEventJudge):
    """
    Function to insert single CompetitionEventJudge object into database
    """

    _db.query("INSERT INTO competition_event_judge"
              "(comp_id, judge_id, judge_name) "
              "VALUES "
              "('%s', '%s', '%s')" % (competitionEventJudge.__dict__['d_compId'],
                                      competitionEventJudge.__dict__['d_judgeId'],
                                      competitionEventJudge.__dict__['d_judgeName']))

def insertCompetitionEventJudgeList(competitionEventJudgeList):
    """
    Function to insert list of CompetitionEventJudge objects into database
    """

    values = []
    for competitionEventJudge in competitionEventJudgeList:
        values.append("('%s', '%s', '%s')" % (competitionEventJudge.__dict__['d_compId'],
                                              competitionEventJudge.__dict__['d_judgeId'],
                                              competitionEventJudge.__dict__['d_judgeName']))

    _db.query("INSERT INTO competition_event_judge"
              "(comp_id, judge_id, judge_name) "
              "VALUES "
              "%s" % ",".join(values))

