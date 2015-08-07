-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players ( id SERIAL,
                       name TEXT,
                       wins INTEGER,
                       matches INTEGER,
                       bye INTEGER );

CREATE TABLE matches ( matchid SERIAL,
                       winner INTEGER,
                       loser INTEGER );
