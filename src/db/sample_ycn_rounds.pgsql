select
    results.comp_id,
    results.comp_name,
    results.comp_date,
    results.event_name,
    results.couple_num,
    results.leader_name,
    results.follower_name,
    results.event_placement,
    event_rounds.num_rounds,
    case when event_placement = 1 then 3 when event_placement = 2 then 2 else 1 end points
from
(
    select
        c.comp_id
        , c.comp_name
        , c.comp_date
        , v.event_id
        , v.event_name
        , e.couple_num
        , e.leader_name
        , e.follower_name
        , e.event_placement
    from o2cm.entry e
    join o2cm.competition c
        on c.comp_id = e.comp_id
    join o2cm.event v
        on v.comp_id = c.comp_id
        and v.event_id = e.event_id
) results
join (
    select
        comp_id,
        event_id,
        max(round_num) + 1 as num_rounds
    from o2cm.round_result
    group by comp_id, event_id
) event_rounds
    on results.comp_id = event_rounds.comp_id
    and results.event_id = event_rounds.event_id
join (
    select
        comp_id,
        event_id,
        couple_num,
        min(round_num) furthest_round
    from o2cm.round_result
    group by comp_id, event_id, couple_num
) couple_progress
    on couple_progress.comp_id = results.comp_id
    and couple_progress.event_id = results.event_id
    and couple_progress.couple_num = results.couple_num
    and couple_progress.furthest_round = 0
where results.leader_name = 'Eric Lam'
    and (
        (
            results.event_placement <= 6
            and event_rounds.num_rounds >= 3
        ) or (
            results.event_placement <= 3
            and event_rounds.num_rounds >= 2
        )
    )
    and (event_name like '%Gold%' or event_name like '%Advance%')
    and event_name like '%Standard%'
order by comp_date;