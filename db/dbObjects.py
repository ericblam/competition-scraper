""" File automatically generated with generator.py """

class Competition(object):
    """
    Competition wrapper class
    """

    def __init__(self,
                 comp_id,
                 comp_prefix,
                 comp_name,
                 comp_date):
        self.d_compId = comp_id
        self.d_compPrefix = comp_prefix
        self.d_compName = comp_name
        self.d_compDate = comp_date


class CompetitionEvent(object):
    """
    Competition Event wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 event_level,
                 category):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_eventLevel = event_level
        self.d_category = category


class CompetitionEventDance(object):
    """
    Competition Event Dance wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 dance):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_dance = dance


class CompetitionEntry(object):
    """
    Competition Entry wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 competitor_number,
                 leader,
                 follwer):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_competitorNumber = competitor_number
        self.d_leader = leader
        self.d_follwer = follwer


class Competitor(object):
    """
    Competitor wrapper class
    """

    def __init__(self,
                 competitor_id,
                 first_name,
                 last_name):
        self.d_competitorId = competitor_id
        self.d_firstName = first_name
        self.d_lastName = last_name


class CompetitionEventPlacement(object):
    """
    Competition Event Placement wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 competitor_number,
                 placement):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_competitorNumber = competitor_number
        self.d_placement = placement


class CompetitionDancePlacement(object):
    """
    Competition Dance Placement wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 competitor_number,
                 placement):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_competitorNumber = competitor_number
        self.d_placement = placement


class CompetitionEventResult(object):
    """
    Competition Event Result wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 event_dance,
                 judge_id,
                 competitor_number,
                 round,
                 placement,
                 callback):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_eventDance = event_dance
        self.d_judgeId = judge_id
        self.d_competitorNumber = competitor_number
        self.d_round = round
        self.d_placement = placement
        self.d_callback = callback


class CompetitionEventJudge(object):
    """
    Competition Event Judge wrapper class
    """

    def __init__(self,
                 comp_id,
                 judge_id,
                 judge_name):
        self.d_compId = comp_id
        self.d_judgeId = judge_id
        self.d_judgeName = judge_name


