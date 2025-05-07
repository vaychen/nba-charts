-- create table teams.sql
create table if not exists stats.teams (
    id bigint primary key,
    full_name varchar(256) not null,
    abbreviation varchar(256),
    nickname varchar(256),
    city varchar(256),
    state varchar(256),
    year_founded int,
    updated_at timestamp default current_timestamp
);
