
CREATE TABLE scrape_attempts (
	id SERIAL PRIMARY KEY,
    username text not null,
    token text not null,
	when_created timestamp NOT NULL default now(),
    status text not null,
    benefits jsonb,
    transactions jsonb,
    error_category text,
    error_desc text,
  	html_doc text
);

ALTER TABLE scrape_attempts ADD CONSTRAINT unique_token UNIQUE (token);
