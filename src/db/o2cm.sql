-- This schema is meant for "raw" data scraped directly from o2cm with minimal processing

DROP SCHEMA IF EXISTS o2cm CASCADE;
CREATE SCHEMA o2cm;

CREATE TABLE o2cm.competition (
    comp_id     varchar(8)
    , comp_name varchar(256)
    , comp_date date
);

CREATE TABLE o2cm.event (
    comp_id      varchar(8)
    , event_id   varchar(16)
    , event_name varchar(256)
    , event_url  varchar(256)
);

CREATE TABLE o2cm.event_couples (
    comp_id           varchar(8)
    , event_id        varchar(16)
    , couple_num      int
    , leader_name     varchar(256)
    , follower_name   varchar(256)
    , event_placement int
);

CREATE TABLE o2cm.round_placement (
    comp_id        varchar(8)
    , event_id     varchar(16)
    , round_number int
    , dance        varchar(32)
    , couple_num   int
    , judge_num    int
    , mark         int
);

CREATE TABLE o2cm.judge (
    comp_id      varchar(8)
    , judge_num  int
    , judge_name varchar(16)
);
