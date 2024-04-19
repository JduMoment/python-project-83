CREATE DATABASE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255),
    created_at DATE
);

CREATE DATABASE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls(id),
    status_code smallint,
    h1 VARCHAR(255),
    description VARCHAR(1000),
    title VARCHAR(255),
    created_at DATE
);