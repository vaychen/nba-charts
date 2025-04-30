-- create database nba_charts in postgres
create database nba_charts;

-- create schema stats
create schema stats;

-- create table players
create table stats.players (
    player_index_id int primary key,
    player_index_last_name varchar(256) not null,
    player_index_first_name varchar(256),
    player_index_full_name varchar(256),
    player_index_is_active boolean,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
