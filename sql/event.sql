drop table event;

create table event(
  event_id bigint,
  data_dt timestamp,
  predict_time timestamp,
  event_name varchar,
  gov_unit varchar,
  event_type varchar,
  status varchar,
  lat real,
  lng real,
  alt real,
  address varchar,
  description varchar,
  primary key (event_id,data_dt)
);

