-- This schema is meant for "raw" data scraped directly from o2cm with minimal processing

DROP SCHEMA IF EXISTS o2cm CASCADE;
CREATE SCHEMA o2cm;

CREATE TABLE o2cm.competition (
    comp_id     varchar(8)
    , comp_name varchar(256)
    , comp_date date
    , PRIMARY KEY (comp_id)
);

CREATE TABLE o2cm.event (
    comp_id      varchar(8)
    , event_id   varchar(16)
    , event_name varchar(256)
    , event_url  varchar(256)
    , event_num  int
    , PRIMARY KEY (comp_id, event_id)
);

CREATE TABLE o2cm.entry (
    comp_id           varchar(8)
    , event_id        varchar(16)
    , couple_num      int
    , leader_name     varchar(256)
    , follower_name   varchar(256)
    , event_placement numeric(6,3)
    , couple_location varchar(32)
    , PRIMARY KEY (comp_id, event_id, couple_num)
);

CREATE TABLE o2cm.round_placement (
    comp_id        varchar(8)
    , event_id     varchar(16)
    , round_num    int
    , dance        varchar(32)
    , couple_num   int
    , judge_num    int
    , mark         int
    , PRIMARY KEY (comp_id, event_id, round_num, dance, couple_num, judge_num)
);

CREATE TABLE o2cm.round_result (
    comp_id      varchar(8)
    , event_id   varchar(16)
    , round_num  int
    , dance      varchar(32)
    , couple_num int
    , placement  numeric(4,3)
    , PRIMARY KEY (comp_id, event_id, round_num, dance, couple_num)
);

CREATE TABLE o2cm.judge (
    comp_id      varchar(8)
    , event_id   varchar(16)
    , round_num  int
    , judge_num  int
    , judge_name varchar(128)
    , PRIMARY KEY (comp_id, event_id, round_num, judge_num)
);
