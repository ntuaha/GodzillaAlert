drop table event_log;
create table event_log(
event_id  bigint,
update_dt  timestamp with time zone,
type  varchar,
status  integer,
address  varchar,
lat  real,
lng  real,
alt  real,
description  varchar,
source  varchar,
provider  varchar,
DATA  json,
primary key(event_id,update_dt)
);
