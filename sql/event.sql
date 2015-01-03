drop table event;

create table event(
  event_id bigserial,
  title varchar,
  start_dt timestamp with time zone,
  end_dt timestamp with time zone,
  update_dt timestamp with time zone,
  predict_time timestamp with time zone,
  type varchar,
  description varchar,
  status integer,
  lat real,
  lng real,
  alt real,
  address varchar,
  primary key(event_id)
);

