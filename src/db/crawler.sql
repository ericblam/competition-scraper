-- This schema is meant for crawler-related data

DROP SCHEMA IF EXISTS crawler CASCADE;
CREATE SCHEMA crawler;

CREATE TABLE crawler.error (
    error_id            SERIAL
    , task              bytea
    , error_description varchar(1024)
);
