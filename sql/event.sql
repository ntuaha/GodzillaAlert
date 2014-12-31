drop table event;

create table event(
  event_id bigserial,
  start_dt timestamp,
  end_dt timestamp,
  update_dt timestamp,
  predict_time timestamp,
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

