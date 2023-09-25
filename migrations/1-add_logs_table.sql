CREATE TABLE endpoint_logs (
	id SERIAL PRIMARY KEY,
    username text not null,
	when_created timestamp NOT NULL default now(),
    endpoint text not null,
  	status text not null,
    error_desc text,
  	html_doc text
);