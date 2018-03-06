""" File automatically generated with generator.py """

from pg import DB, IntegrityError

db = DB(dbname = 'ballroom_competitions',
        host   = 'localhost',
        port   =  5432,
        user   = 'postgres',
        passwd = 'postgres')

def insertCompetition(competition):
    """
    Function to insert single Competition object into database
    """

    db.query("INSERT INTO competition"
             "(comp_id, comp_prefix, comp_name, comp_date) "
             "VALUES "
             "('%s', '%s', '%s', '%s')" % (competition.__dict__['d_compId'],
                                           competition.__dict__['d_compPrefix'],
                                           competition.__dict__['d_compName'],
                                           competition.__dict__['d_compDate'])
    )

def insertCompetitionList(competitionList):
    """
    Function to insert list of Competition objects into database
    """

    pass

def insertCompetitionEvent(competitionEvent):
    """
    Function to insert single CompetitionEvent object into database
    """

    db.query("INSERT INTO competition_event"
             "(comp_id, event_id, event_level, category) "
             "VALUES "
             "('%s', '%s', '%s', '%s')" % (competitionEvent.__dict__['d_compId'],
                                           competitionEvent.__dict__['d_eventId'],
                                           competitionEvent.__dict__['d_eventLevel'],
                                           competitionEvent.__dict__['d_category'])
    )

def insertCompetitionEventList(competitionEventList):
    """
    Function to insert list of CompetitionEvent objects into database
    """

    pass

def insertCompetitionEventDance(competitionEventDance):
    """
    Function to insert single CompetitionEventDance object into database
    """

    db.query("INSERT INTO competition_event_dance"
             "(comp_id, event_id, dance) "
             "VALUES "
             "('%s', '%s', '%s')" % (competitionEventDance.__dict__['d_compId'],
                                     competitionEventDance.__dict__['d_eventId'],
                                     competitionEventDance.__dict__['d_dance'])
    )

def insertCompetitionEventDanceList(competitionEventDanceList):
    """
    Function to insert list of CompetitionEventDance objects into database
    """

    pass

def insertCompetitionEntry(competitionEntry):
    """
    Function to insert single CompetitionEntry object into database
    """

    db.query("INSERT INTO competition_entry"
             "(comp_id, event_id, competitor_number, leader, follwer) "
             "VALUES "
             "('%s', '%s', '%s', '%s', '%s')" % (competitionEntry.__dict__['d_compId'],
                                                 competitionEntry.__dict__['d_eventId'],
                                                 competitionEntry.__dict__['d_competitorNumber'],
                                                 competitionEntry.__dict__['d_leader'],
                                                 competitionEntry.__dict__['d_follwer'])
    )

def insertCompetitionEntryList(competitionEntryList):
    """
    Function to insert list of CompetitionEntry objects into database
    """

    pass

def insertCompetitor(competitor):
    """
    Function to insert single Competitor object into database
    """

    db.query("INSERT INTO competitor"
             "(competitor_id, first_name, last_name) "
             "VALUES "
             "('%s', '%s', '%s')" % (competitor.__dict__['d_competitorId'],
                                     competitor.__dict__['d_firstName'],
                                     competitor.__dict__['d_lastName'])
    )

def insertCompetitorList(competitorList):
    """
    Function to insert list of Competitor objects into database
    """

    pass

def insertCompetitionEventPlacement(competitionEventPlacement):
    """
    Function to insert single CompetitionEventPlacement object into database
    """

    db.query("INSERT INTO competition_event_placement"
             "(comp_id, event_id, competitor_number, placement) "
             "VALUES "
             "('%s', '%s', '%s', '%s')" % (competitionEventPlacement.__dict__['d_compId'],
                                           competitionEventPlacement.__dict__['d_eventId'],
                                           competitionEventPlacement.__dict__['d_competitorNumber'],
                                           competitionEventPlacement.__dict__['d_placement'])
    )

def insertCompetitionEventPlacementList(competitionEventPlacementList):
    """
    Function to insert list of CompetitionEventPlacement objects into database
    """

    pass

def insertCompetitionDancePlacement(competitionDancePlacement):
    """
    Function to insert single CompetitionDancePlacement object into database
    """

    db.query("INSERT INTO competition_dance_placement"
             "(comp_id, event_id, competitor_number, placement) "
             "VALUES "
             "('%s', '%s', '%s', '%s')" % (competitionDancePlacement.__dict__['d_compId'],
                                           competitionDancePlacement.__dict__['d_eventId'],
                                           competitionDancePlacement.__dict__['d_competitorNumber'],
                                           competitionDancePlacement.__dict__['d_placement'])
    )

def insertCompetitionDancePlacementList(competitionDancePlacementList):
    """
    Function to insert list of CompetitionDancePlacement objects into database
    """

    pass

def insertCompetitionEventResult(competitionEventResult):
    """
    Function to insert single CompetitionEventResult object into database
    """

    db.query("INSERT INTO competition_event_result"
             "(comp_id, event_id, event_dance, judge_id, competitor_number, round, placement, callback) "
             "VALUES "
             "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (competitionEventResult.__dict__['d_compId'],
                                                                   competitionEventResult.__dict__['d_eventId'],
                                                                   competitionEventResult.__dict__['d_eventDance'],
                                                                   competitionEventResult.__dict__['d_judgeId'],
                                                                   competitionEventResult.__dict__['d_competitorNumber'],
                                                                   competitionEventResult.__dict__['d_round'],
                                                                   competitionEventResult.__dict__['d_placement'],
                                                                   competitionEventResult.__dict__['d_callback'])
    )

def insertCompetitionEventResultList(competitionEventResultList):
    """
    Function to insert list of CompetitionEventResult objects into database
    """

    pass

def insertCompetitionEventJudge(competitionEventJudge):
    """
    Function to insert single CompetitionEventJudge object into database
    """

    db.query("INSERT INTO competition_event_judge"
             "(comp_id, judge_id, judge_name) "
             "VALUES "
             "('%s', '%s', '%s')" % (competitionEventJudge.__dict__['d_compId'],
                                     competitionEventJudge.__dict__['d_judgeId'],
                                     competitionEventJudge.__dict__['d_judgeName'])
    )

def insertCompetitionEventJudgeList(competitionEventJudgeList):
    """
    Function to insert list of CompetitionEventJudge objects into database
    """

    pass

