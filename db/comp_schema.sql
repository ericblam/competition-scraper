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
