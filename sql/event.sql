drop table event;
drop table event_log;

create table event(
  event_id bigserial,
  start_dt timestamp with time zone ,
  end_dt timestamp with time zone,
  update_dt timestamp with time zone,
  predict_time timestamp with time zone,
  name varchar,
  type varchar,
  status varchar,
  source varchar,
  provider varchar,
  position_desc varchar,
  lat real,
  lng real,
  alt real,
  address varchar,
  description varchar,
  primary key (event_id)
);

create table event_log(
  event_id bigint,
  status varchar,
  log_dt timestamp with time zone
);

