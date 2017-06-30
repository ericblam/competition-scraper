drop table entries;
drop table results;
drop table placements;
drop table judges;
drop table competitions;
drop table competitors;
drop table competitor_affiliations;
drop table events;
-- drop table event_dances;

create table entries (
       competition_id       varchar(8)
       , event_id           varchar(8)
       , lead_id            int
       , follow_id          int
       , competitor_number  int
       , primary key (competition_id, event_id, lead_id, follow_id)
);

create table results (
       competition_id       varchar(8)
       , event_id           varchar(8)
       , event_dance	    varchar(255)
       , judge_id           int
       , competitor_number  int
       , round              int
       , placement          int
       , callback           boolean
       , primary key (competition_id, event_id, event_dance, judge_id, competitor_number, round)
);

create table placements (
       competition_id       varchar(8)
       , event_id           varchar(8)
       , competitor_number  int
       , placement          int
       , primary key (competition_id, event_id, competitor_number)
);

create table judges (
       competition_id       varchar(8)
       , judge_id           int
       , judge_name         varchar(255)
       , primary key (competition_id, judge_id)
);

create table competitions (
       competition_id       varchar(8) primary key
       , comp_host          varchar(255)
       , comp_name          varchar(255)
       , comp_year          int
       , comp_date          varchar(255)
);

create table competitors (
       competitor_id        int primary key
       , first_name         varchar(255)
       , last_name          varchar(255)
);

create table competitor_affiliations (
       competitor_id        int
       , competition_id     int
       , affiliation        varchar(255)
       , location           varchar(255)
       , primary key (competitor_id, competition_id)
);

create table events (
       competition_id       varchar(8)
       , event_id           varchar(255)
       , event_level        varchar(255)
       , category           varchar(255)
       , primary key (competition_id, event_id)
);

-- create table event_dances (
--        competition_id       varchar(8)
--        , event_id           int
--        , dance              varchar(255)
--        , primary key (competition_id, event_id, dance)
-- );

