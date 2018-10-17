""" File automatically generated with generator.py """

class Competition(object):
    """
    Competition wrapper class
    """

    def __init__(self,
                 comp_id,
                 comp_name,
                 comp_date):
        self.d_compId = comp_id
        self.d_compName = comp_name
        self.d_compDate = comp_date

    def __str__(self):
        return "{Competition: d_compId='%s', d_compName='%s', d_compDate='%s'}" % (self.d_compId, self.d_compName, self.d_compDate)



class CompetitionEvent(object):
    """
    Competition Event wrapper class
    """

    def __init__(self,
                 event_id,
                 comp_id,
                 event_code,
                 event_level,
                 category,
                 url):
        self.d_eventId = event_id
        self.d_compId = comp_id
        self.d_eventCode = event_code
        self.d_eventLevel = event_level
        self.d_category = category
        self.d_url = url

    def __str__(self):
        return "{CompetitionEvent: d_eventId='%s', d_compId='%s', d_eventCode='%s', d_eventLevel='%s', d_category='%s', d_url='%s'}" % (self.d_eventId, self.d_compId, self.d_eventCode, self.d_eventLevel, self.d_category, self.d_url)



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

    def __str__(self):
        return "{CompetitionEventDance: d_compId='%s', d_eventId='%s', d_dance='%s'}" % (self.d_compId, self.d_eventId, self.d_dance)



class CompetitionEntry(object):
    """
    Competition Entry wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 competitor_number,
                 leader_id,
                 follower_id):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_competitorNumber = competitor_number
        self.d_leaderId = leader_id
        self.d_followerId = follower_id

    def __str__(self):
        return "{CompetitionEntry: d_compId='%s', d_eventId='%s', d_competitorNumber='%s', d_leaderId='%s', d_followerId='%s'}" % (self.d_compId, self.d_eventId, self.d_competitorNumber, self.d_leaderId, self.d_followerId)



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

    def __str__(self):
        return "{Competitor: d_competitorId='%s', d_firstName='%s', d_lastName='%s'}" % (self.d_competitorId, self.d_firstName, self.d_lastName)



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

    def __str__(self):
        return "{CompetitionEventPlacement: d_compId='%s', d_eventId='%s', d_competitorNumber='%s', d_placement='%s'}" % (self.d_compId, self.d_eventId, self.d_competitorNumber, self.d_placement)



class CompetitionDancePlacement(object):
    """
    Competition Dance Placement wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 event_dance,
                 competitor_number,
                 placement):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_eventDance = event_dance
        self.d_competitorNumber = competitor_number
        self.d_placement = placement

    def __str__(self):
        return "{CompetitionDancePlacement: d_compId='%s', d_eventId='%s', d_eventDance='%s', d_competitorNumber='%s', d_placement='%s'}" % (self.d_compId, self.d_eventId, self.d_eventDance, self.d_competitorNumber, self.d_placement)



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

    def __str__(self):
        return "{CompetitionEventResult: d_compId='%s', d_eventId='%s', d_eventDance='%s', d_judgeId='%s', d_competitorNumber='%s', d_round='%s', d_placement='%s', d_callback='%s'}" % (self.d_compId, self.d_eventId, self.d_eventDance, self.d_judgeId, self.d_competitorNumber, self.d_round, self.d_placement, self.d_callback)



class CompetitionEventJudge(object):
    """
    Competition Event Judge wrapper class
    """

    def __init__(self,
                 comp_id,
                 event_id,
                 judge_id,
                 judge_name):
        self.d_compId = comp_id
        self.d_eventId = event_id
        self.d_judgeId = judge_id
        self.d_judgeName = judge_name

    def __str__(self):
        return "{CompetitionEventJudge: d_compId='%s', d_eventId='%s', d_judgeId='%s', d_judgeName='%s'}" % (self.d_compId, self.d_eventId, self.d_judgeId, self.d_judgeName)



