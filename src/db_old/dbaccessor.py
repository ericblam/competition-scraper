""" File automatically generated with generator.py """

from db.dbobjects import *

from pg import DB, IntegrityError

import os

_dir = os.path.dirname(__file__) + "/"

def createConn(config):
    return DB(dbname = config['dbname'],
              host   = config['host'],
              port   = config['port'],
              user   = config['user'],
              passwd = config['password'])

def dbReset(conn):
    """
    Resets and reconfigures database
    """

    conn.query("""
drop table competition;
drop table competition_event;
drop table competition_event_dance;
drop table competition_entry;
drop table competitor;
drop table competition_event_placement;
drop table competition_dance_placement;
drop table competition_event_result;
drop table competition_event_judge;

create table competition (
        comp_id              varchar(8)
      , comp_name            varchar(255)
      , comp_date            date
      , primary key (comp_id)
);

create table competition_event (
        event_id             varchar(16)
      , comp_id              varchar(8)
      , event_code           varchar(8)
      , event_age            varchar(255)
      , event_level          varchar(255)
      , category             varchar(255)
      , url                  varchar(2084)
      , primary key (event_id)
);

create table competition_event_dance (
        comp_id              varchar(8)
      , event_id             varchar(16)
      , dance                varchar(255)
);

create table competition_entry (
        comp_id              varchar(8)
      , event_id             varchar(16)
      , competitor_number    int
      , leader_id            int
      , follower_id          int
);

create table competitor (
        competitor_id        int
      , first_name           varchar(255)
      , last_name            varchar(255)
);

create table competition_event_placement (
        comp_id              varchar(8)
      , event_id             varchar(16)
      , competitor_number    int
      , placement            int
);

create table competition_dance_placement (
        comp_id              varchar(8)
      , event_id             varchar(16)
      , event_dance          varchar(255)
      , competitor_number    int
      , placement            int
);

create table competition_event_result (
        comp_id              varchar(8)
      , event_id             varchar(16)
      , event_dance          varchar(255)
      , judge_id             int
      , competitor_number    int
      , round                int
      , placement            int
      , callback             boolean
);

create table competition_event_judge (
        comp_id              varchar(8)
      , event_id             varchar(16)
      , judge_id             int
      , judge_name           varchar(255)
);

    """)

def dbClearComp(conn, compId):
    """
    Removes data for comp compId
    """

    conn.query("""
        delete from competition where comp_id = '%s';
        delete from competition_event where comp_id = '%s';
        delete from competition_event_dance where comp_id = '%s';
        delete from competition_entry where comp_id = '%s';
        delete from competition_event_placement where comp_id = '%s';
        delete from competition_dance_placement where comp_id = '%s';
        delete from competition_event_result where comp_id = '%s';
        delete from competition_event_judge where comp_id = '%s';
    """ % (compId,compId,compId,compId,compId,compId,compId,compId))

def insertCompetition(conn, competition):
    """
    Function to insert single Competition object into database
    """

    conn.query("INSERT INTO competition"
               "(comp_id, comp_name, comp_date) "
               "VALUES "
               "('%s', '%s', '%s')" % (competition.__dict__['d_compId'],
                                      competition.__dict__['d_compName'],
                                      competition.__dict__['d_compDate']))

def insertCompetitionList(conn, competitionList):
    """
    Function to insert list of Competition objects into database
    """

    values = []
    for competition in competitionList:
        values.append("('%s', '%s', '%s')" % (competition.__dict__['d_compId'],
                                              competition.__dict__['d_compName'],
                                              competition.__dict__['d_compDate']))

    conn.query("INSERT INTO competition"
               "(comp_id, comp_name, comp_date) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetition(conn):
    """
    Does select * from competition
    Exercise caution - this retrieves all rows of competition
    """

    dbRes = conn.query("SELECT * FROM competition")
    res = []
    for row in dbRes.dictresult():
        res.append(Competition(row["comp_id"], row["comp_name"], row["comp_date"]))
    return res

def insertCompetitionEvent(conn, competitionEvent):
    """
    Function to insert single CompetitionEvent object into database
    """

    conn.query("INSERT INTO competition_event"
               "(event_id, comp_id, event_code, event_age, event_level, category, url) "
               "VALUES "
               "('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (competitionEvent.__dict__['d_eventId'],
                                                              competitionEvent.__dict__['d_compId'],
                                                              competitionEvent.__dict__['d_eventCode'],
                                                              competitionEvent.__dict__['d_eventAge'],
                                                              competitionEvent.__dict__['d_eventLevel'],
                                                              competitionEvent.__dict__['d_category'],
                                                              competitionEvent.__dict__['d_url']))

def insertCompetitionEventList(conn, competitionEventList):
    """
    Function to insert list of CompetitionEvent objects into database
    """

    values = []
    for competitionEvent in competitionEventList:
        values.append("('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (competitionEvent.__dict__['d_eventId'],
                                                                      competitionEvent.__dict__['d_compId'],
                                                                      competitionEvent.__dict__['d_eventCode'],
                                                                      competitionEvent.__dict__['d_eventAge'],
                                                                      competitionEvent.__dict__['d_eventLevel'],
                                                                      competitionEvent.__dict__['d_category'],
                                                                      competitionEvent.__dict__['d_url']))

    conn.query("INSERT INTO competition_event"
               "(event_id, comp_id, event_code, event_age, event_level, category, url) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionEvent(conn):
    """
    Does select * from competition_event
    Exercise caution - this retrieves all rows of competition_event
    """

    dbRes = conn.query("SELECT * FROM competition_event")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionEvent(row["event_id"], row["comp_id"], row["event_code"], row["event_age"], row["event_level"], row["category"], row["url"]))
    return res

def insertCompetitionEventDance(conn, competitionEventDance):
    """
    Function to insert single CompetitionEventDance object into database
    """

    conn.query("INSERT INTO competition_event_dance"
               "(comp_id, event_id, dance) "
               "VALUES "
               "('%s', '%s', '%s')" % (competitionEventDance.__dict__['d_compId'],
                                      competitionEventDance.__dict__['d_eventId'],
                                      competitionEventDance.__dict__['d_dance']))

def insertCompetitionEventDanceList(conn, competitionEventDanceList):
    """
    Function to insert list of CompetitionEventDance objects into database
    """

    values = []
    for competitionEventDance in competitionEventDanceList:
        values.append("('%s', '%s', '%s')" % (competitionEventDance.__dict__['d_compId'],
                                              competitionEventDance.__dict__['d_eventId'],
                                              competitionEventDance.__dict__['d_dance']))

    conn.query("INSERT INTO competition_event_dance"
               "(comp_id, event_id, dance) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionEventDance(conn):
    """
    Does select * from competition_event_dance
    Exercise caution - this retrieves all rows of competition_event_dance
    """

    dbRes = conn.query("SELECT * FROM competition_event_dance")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionEventDance(row["comp_id"], row["event_id"], row["dance"]))
    return res

def insertCompetitionEntry(conn, competitionEntry):
    """
    Function to insert single CompetitionEntry object into database
    """

    conn.query("INSERT INTO competition_entry"
               "(comp_id, event_id, competitor_number, leader_id, follower_id) "
               "VALUES "
               "('%s', '%s', '%s', '%s', '%s')" % (competitionEntry.__dict__['d_compId'],
                                                  competitionEntry.__dict__['d_eventId'],
                                                  competitionEntry.__dict__['d_competitorNumber'],
                                                  competitionEntry.__dict__['d_leaderId'],
                                                  competitionEntry.__dict__['d_followerId']))

def insertCompetitionEntryList(conn, competitionEntryList):
    """
    Function to insert list of CompetitionEntry objects into database
    """

    values = []
    for competitionEntry in competitionEntryList:
        values.append("('%s', '%s', '%s', '%s', '%s')" % (competitionEntry.__dict__['d_compId'],
                                                          competitionEntry.__dict__['d_eventId'],
                                                          competitionEntry.__dict__['d_competitorNumber'],
                                                          competitionEntry.__dict__['d_leaderId'],
                                                          competitionEntry.__dict__['d_followerId']))

    conn.query("INSERT INTO competition_entry"
               "(comp_id, event_id, competitor_number, leader_id, follower_id) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionEntry(conn):
    """
    Does select * from competition_entry
    Exercise caution - this retrieves all rows of competition_entry
    """

    dbRes = conn.query("SELECT * FROM competition_entry")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionEntry(row["comp_id"], row["event_id"], row["competitor_number"], row["leader_id"], row["follower_id"]))
    return res

def insertCompetitor(conn, competitor):
    """
    Function to insert single Competitor object into database
    """

    conn.query("INSERT INTO competitor"
               "(competitor_id, first_name, last_name) "
               "VALUES "
               "('%s', '%s', '%s')" % (competitor.__dict__['d_competitorId'],
                                      competitor.__dict__['d_firstName'],
                                      competitor.__dict__['d_lastName']))

def insertCompetitorList(conn, competitorList):
    """
    Function to insert list of Competitor objects into database
    """

    values = []
    for competitor in competitorList:
        values.append("('%s', '%s', '%s')" % (competitor.__dict__['d_competitorId'],
                                              competitor.__dict__['d_firstName'],
                                              competitor.__dict__['d_lastName']))

    conn.query("INSERT INTO competitor"
               "(competitor_id, first_name, last_name) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitor(conn):
    """
    Does select * from competitor
    Exercise caution - this retrieves all rows of competitor
    """

    dbRes = conn.query("SELECT * FROM competitor")
    res = []
    for row in dbRes.dictresult():
        res.append(Competitor(row["competitor_id"], row["first_name"], row["last_name"]))
    return res

def insertCompetitionEventPlacement(conn, competitionEventPlacement):
    """
    Function to insert single CompetitionEventPlacement object into database
    """

    conn.query("INSERT INTO competition_event_placement"
               "(comp_id, event_id, competitor_number, placement) "
               "VALUES "
               "('%s', '%s', '%s', '%s')" % (competitionEventPlacement.__dict__['d_compId'],
                                            competitionEventPlacement.__dict__['d_eventId'],
                                            competitionEventPlacement.__dict__['d_competitorNumber'],
                                            competitionEventPlacement.__dict__['d_placement']))

def insertCompetitionEventPlacementList(conn, competitionEventPlacementList):
    """
    Function to insert list of CompetitionEventPlacement objects into database
    """

    values = []
    for competitionEventPlacement in competitionEventPlacementList:
        values.append("('%s', '%s', '%s', '%s')" % (competitionEventPlacement.__dict__['d_compId'],
                                                    competitionEventPlacement.__dict__['d_eventId'],
                                                    competitionEventPlacement.__dict__['d_competitorNumber'],
                                                    competitionEventPlacement.__dict__['d_placement']))

    conn.query("INSERT INTO competition_event_placement"
               "(comp_id, event_id, competitor_number, placement) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionEventPlacement(conn):
    """
    Does select * from competition_event_placement
    Exercise caution - this retrieves all rows of competition_event_placement
    """

    dbRes = conn.query("SELECT * FROM competition_event_placement")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionEventPlacement(row["comp_id"], row["event_id"], row["competitor_number"], row["placement"]))
    return res

def insertCompetitionDancePlacement(conn, competitionDancePlacement):
    """
    Function to insert single CompetitionDancePlacement object into database
    """

    conn.query("INSERT INTO competition_dance_placement"
               "(comp_id, event_id, event_dance, competitor_number, placement) "
               "VALUES "
               "('%s', '%s', '%s', '%s', '%s')" % (competitionDancePlacement.__dict__['d_compId'],
                                                  competitionDancePlacement.__dict__['d_eventId'],
                                                  competitionDancePlacement.__dict__['d_eventDance'],
                                                  competitionDancePlacement.__dict__['d_competitorNumber'],
                                                  competitionDancePlacement.__dict__['d_placement']))

def insertCompetitionDancePlacementList(conn, competitionDancePlacementList):
    """
    Function to insert list of CompetitionDancePlacement objects into database
    """

    values = []
    for competitionDancePlacement in competitionDancePlacementList:
        values.append("('%s', '%s', '%s', '%s', '%s')" % (competitionDancePlacement.__dict__['d_compId'],
                                                          competitionDancePlacement.__dict__['d_eventId'],
                                                          competitionDancePlacement.__dict__['d_eventDance'],
                                                          competitionDancePlacement.__dict__['d_competitorNumber'],
                                                          competitionDancePlacement.__dict__['d_placement']))

    conn.query("INSERT INTO competition_dance_placement"
               "(comp_id, event_id, event_dance, competitor_number, placement) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionDancePlacement(conn):
    """
    Does select * from competition_dance_placement
    Exercise caution - this retrieves all rows of competition_dance_placement
    """

    dbRes = conn.query("SELECT * FROM competition_dance_placement")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionDancePlacement(row["comp_id"], row["event_id"], row["event_dance"], row["competitor_number"], row["placement"]))
    return res

def insertCompetitionEventResult(conn, competitionEventResult):
    """
    Function to insert single CompetitionEventResult object into database
    """

    conn.query("INSERT INTO competition_event_result"
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

def insertCompetitionEventResultList(conn, competitionEventResultList):
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

    conn.query("INSERT INTO competition_event_result"
               "(comp_id, event_id, event_dance, judge_id, competitor_number, round, placement, callback) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionEventResult(conn):
    """
    Does select * from competition_event_result
    Exercise caution - this retrieves all rows of competition_event_result
    """

    dbRes = conn.query("SELECT * FROM competition_event_result")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionEventResult(row["comp_id"], row["event_id"], row["event_dance"], row["judge_id"], row["competitor_number"], row["round"], row["placement"], row["callback"]))
    return res

def insertCompetitionEventJudge(conn, competitionEventJudge):
    """
    Function to insert single CompetitionEventJudge object into database
    """

    conn.query("INSERT INTO competition_event_judge"
               "(comp_id, event_id, judge_id, judge_name) "
               "VALUES "
               "('%s', '%s', '%s', '%s')" % (competitionEventJudge.__dict__['d_compId'],
                                            competitionEventJudge.__dict__['d_eventId'],
                                            competitionEventJudge.__dict__['d_judgeId'],
                                            competitionEventJudge.__dict__['d_judgeName']))

def insertCompetitionEventJudgeList(conn, competitionEventJudgeList):
    """
    Function to insert list of CompetitionEventJudge objects into database
    """

    values = []
    for competitionEventJudge in competitionEventJudgeList:
        values.append("('%s', '%s', '%s', '%s')" % (competitionEventJudge.__dict__['d_compId'],
                                                    competitionEventJudge.__dict__['d_eventId'],
                                                    competitionEventJudge.__dict__['d_judgeId'],
                                                    competitionEventJudge.__dict__['d_judgeName']))

    conn.query("INSERT INTO competition_event_judge"
               "(comp_id, event_id, judge_id, judge_name) "
               "VALUES "
               "%s" % ",".join(values))

def selectFromCompetitionEventJudge(conn):
    """
    Does select * from competition_event_judge
    Exercise caution - this retrieves all rows of competition_event_judge
    """

    dbRes = conn.query("SELECT * FROM competition_event_judge")
    res = []
    for row in dbRes.dictresult():
        res.append(CompetitionEventJudge(row["comp_id"], row["event_id"], row["judge_id"], row["judge_name"]))
    return res

class DbObjectContainer(object):
    """
    Container Class to contain all DbObject
    """

    def __init__(self):
        self.d_competition = []
        self.d_competition_event = []
        self.d_competition_event_dance = []
        self.d_competition_entry = []
        self.d_competitor = []
        self.d_competition_event_placement = []
        self.d_competition_dance_placement = []
        self.d_competition_event_result = []
        self.d_competition_event_judge = []

    def addCompetition(self, competition):
        self.d_competition.append(competition)

    def addCompetitionEvent(self, competitionEvent):
        self.d_competition_event.append(competitionEvent)

    def addCompetitionEventDance(self, competitionEventDance):
        self.d_competition_event_dance.append(competitionEventDance)

    def addCompetitionEntry(self, competitionEntry):
        self.d_competition_entry.append(competitionEntry)

    def addCompetitor(self, competitor):
        self.d_competitor.append(competitor)

    def addCompetitionEventPlacement(self, competitionEventPlacement):
        self.d_competition_event_placement.append(competitionEventPlacement)

    def addCompetitionDancePlacement(self, competitionDancePlacement):
        self.d_competition_dance_placement.append(competitionDancePlacement)

    def addCompetitionEventResult(self, competitionEventResult):
        self.d_competition_event_result.append(competitionEventResult)

    def addCompetitionEventJudge(self, competitionEventJudge):
        self.d_competition_event_judge.append(competitionEventJudge)

    def dumpToDb(self, conn):
        if len(self.d_competition) > 0:
            insertCompetitionList(conn, self.d_competition)
        if len(self.d_competition_event) > 0:
            insertCompetitionEventList(conn, self.d_competition_event)
        if len(self.d_competition_event_dance) > 0:
            insertCompetitionEventDanceList(conn, self.d_competition_event_dance)
        if len(self.d_competition_entry) > 0:
            insertCompetitionEntryList(conn, self.d_competition_entry)
        if len(self.d_competitor) > 0:
            insertCompetitorList(conn, self.d_competitor)
        if len(self.d_competition_event_placement) > 0:
            insertCompetitionEventPlacementList(conn, self.d_competition_event_placement)
        if len(self.d_competition_dance_placement) > 0:
            insertCompetitionDancePlacementList(conn, self.d_competition_dance_placement)
        if len(self.d_competition_event_result) > 0:
            insertCompetitionEventResultList(conn, self.d_competition_event_result)
        if len(self.d_competition_event_judge) > 0:
            insertCompetitionEventJudgeList(conn, self.d_competition_event_judge)


