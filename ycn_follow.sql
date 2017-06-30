select distinct
	p.competition_id,
	p.event_id,
	ev.event_level,
	ev.category,
	r.event_dance,
	p.placement
from
	(
	select
	       r1.competition_id,
	       r1.event_id,
	       p.placement,
	       p.competitor_number
	from
	       placements as p,
	       results as r1
	where
	       r1.competition_id = p.competition_id
	       and r1.event_id = p.event_id
	       and r1.competitor_number = p.competitor_number
	       and p.placement <= 3
	       and r1.round = 1
        union
	select
	       r1.competition_id,
	       r1.event_id,
	       p.placement,
	       p.competitor_number
	from
	       placements as p,
	       results as r1
        where
	       r1.competition_id = p.competition_id
	       and r1.event_id = p.event_id
	       and r1.competitor_number = p.competitor_number
	       and p.placement <= 6
	       and p.placement > 3
	       and r1.round = 2
	) as p,
	competitors as c,
	entries as en,
	events as ev,
	results as r
where
	p.competition_id = en.competition_id
	and p.event_id = en.event_id
	and p.competition_id = ev.competition_id
	and p.event_id = ev.event_id
	and c.competitor_id = en.follow_id
	and en.competitor_number = p.competitor_number
	and r.competition_id = p.competition_id
	and r.event_id = p.event_id
	and lower(c.first_name) = lower('%s')
	and lower(c.last_name) = lower('%s')
-- order by p.competition_id, p.event_id
;
