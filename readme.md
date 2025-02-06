## api command
uvicorn api:app --reload --port 8181 --host 0.0.0.0

## sql scrip
create table agv_table (
	job_data varchar(50),
	rfid_data varchar(50),
	req_code varchar(50),
	status varchar(2),
	loc_1 varchar(50),
	loc_2 varchar(50),
	register datetime
);

create table location_table (
	rfid_code varchar(50),
	stgbin_code varchar(50),
	location_name varchar(50)
);

## docker 
docker compose build\
docker compose up -d