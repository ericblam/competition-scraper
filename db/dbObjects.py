""" File automatically generated with generator.py """

class Competition(object):
    """
    Competition wrapper class
    """

    def __init__(self,
             compId,
             compPrefix,
             compName,
             compDate):
    self.d_compId = compId
    self.d_compPrefix = compPrefix
    self.d_compName = compName
    self.d_compDate = compDate


class CompetitionEvent(object):
    """
    Competition Event wrapper class
    """

    def __init__(self,
             compId,
             eventId,
             eventLevel,
             category):
    self.d_compId = compId
    self.d_eventId = eventId
    self.d_eventLevel = eventLevel
    self.d_category = category


class CompetitionEventDance(object):
    """
    Competition Event Dance wrapper class
    """

    def __init__(self,
             compId,
             eventId,
             dance):
    self.d_compId = compId
    self.d_eventId = eventId
    self.d_dance = dance


class CompetitionEntry(object):
    """
    Competition Entry wrapper class
    """

    def __init__(self,
             compId,
             eventId,
             competitorNumber,
             leader,
             follwer):
    self.d_compId = compId
    self.d_eventId = eventId
    self.d_competitorNumber = competitorNumber
    self.d_leader = leader
    self.d_follwer = follwer


class Competitor(object):
    """
    Competitor wrapper class
    """

    def __init__(self,
             competitorId,
             firstName,
             lastName):
    self.d_competitorId = competitorId
    self.d_firstName = firstName
    self.d_lastName = lastName


class CompetitionEventPlacement(object):
    """
    Competition Event Placement wrapper class
    """

    def __init__(self,
             compId,
             eventId,
             competitorNumber,
             placement):
    self.d_compId = compId
    self.d_eventId = eventId
    self.d_competitorNumber = competitorNumber
    self.d_placement = placement


class CompetitionDancePlacement(object):
    """
    Competition Dance Placement wrapper class
    """

    def __init__(self,
             compId,
             eventId,
             competitorNumber,
             placement):
    self.d_compId = compId
    self.d_eventId = eventId
    self.d_competitorNumber = competitorNumber
    self.d_placement = placement


class CompetitionEventResult(object):
    """
    Competition Event Result wrapper class
    """

    def __init__(self,
             compId,
             eventId,
             eventDance,
             judgeId,
             competitorNumber,
             round,
             placement,
             callback):
    self.d_compId = compId
    self.d_eventId = eventId
    self.d_eventDance = eventDance
    self.d_judgeId = judgeId
    self.d_competitorNumber = competitorNumber
    self.d_round = round
    self.d_placement = placement
    self.d_callback = callback


class CompetitionEventJudge(object):
    """
    Competition Event Judge wrapper class
    """

    def __init__(self,
             compId,
             judgeId,
             judgeName):
    self.d_compId = compId
    self.d_judgeId = judgeId
    self.d_judgeName = judgeName


