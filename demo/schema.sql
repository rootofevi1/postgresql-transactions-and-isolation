-- Independently written portfolio fixture, inferred from solution queries.
-- Run once in a NEW disposable database. No school database dump is used.
CREATE TABLE person (
    id bigint PRIMARY KEY,
    name text NOT NULL,
    age integer NOT NULL CHECK (age > 0),
    gender text NOT NULL CHECK (gender IN ('female', 'male')),
    address text NOT NULL
);
CREATE TABLE pizzeria (
    id bigint PRIMARY KEY,
    name text NOT NULL UNIQUE,
    rating numeric(3,2) NOT NULL CHECK (rating BETWEEN 0 AND 5)
);
CREATE TABLE menu (
    id bigint PRIMARY KEY,
    pizzeria_id bigint NOT NULL REFERENCES pizzeria(id),
    pizza_name text NOT NULL,
    price numeric(10,2) NOT NULL CHECK (price >= 0)
);
CREATE TABLE person_visits (
    id bigint PRIMARY KEY,
    person_id bigint NOT NULL REFERENCES person(id),
    pizzeria_id bigint NOT NULL REFERENCES pizzeria(id),
    visit_date date NOT NULL
);
CREATE TABLE person_order (
    id bigint PRIMARY KEY,
    person_id bigint NOT NULL REFERENCES person(id),
    menu_id bigint NOT NULL REFERENCES menu(id),
    order_date date NOT NULL
);
