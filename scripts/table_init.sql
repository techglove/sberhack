DROP TABLE test_places;
DROP TABLE tests;
DROP TABLE med_organisations;
DROP TABLE cities;
DROP TABLE test_type;

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

CREATE TABLE test_type (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    type  varchar(1000)
);

CREATE TABLE tests (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    type_id integer,
    org_id integer,
    price varchar(1000),
    is_urgent boolean,
    options varchar(1000),
    CONSTRAINT fk_org_id
        FOREIGN KEY(org_id)
	    REFERENCES med_organisations(id),

    CONSTRAINT fk_type_id
        FOREIGN KEY(type_id)
	    REFERENCES test_type(id)
);
