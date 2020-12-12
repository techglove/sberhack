DROP TABLE test_places;
DROP TABLE med_organisations;
DROP TABLE cities;

CREATE TABLE med_organisations (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(256) NOT NULL
);

CREATE TABLE cities (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(256) NOT NULL
);

CREATE TABLE test_places (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    org_id integer,
    city_id integer,
    address varchar(1000),
    coord geography(POINT),
    price varchar(1000),
    url varchar(1000),
    is_urgent boolean,
    CONSTRAINT fk_org_id
        FOREIGN KEY(org_id)
	    REFERENCES med_organisations(id),

    CONSTRAINT fk_city_id
        FOREIGN KEY(city_id)
	    REFERENCES cities(id)
);
