-- New synthetic dataset, NOT a copy of the School 21 dataset.
-- A few names/dates/IDs are compatibility literals used by the solution queries.
INSERT INTO person (id,name,age,gender,address) VALUES
 (1,'Anna',28,'female','Kazan'), (2,'Denis',33,'male','Moscow'),
 (3,'Dmitriy',26,'male','Samara'), (4,'Irina',42,'female','Kazan'),
 (5,'Kate',19,'female','Moscow'), (6,'Andrey',24,'male','Samara'),
 (7,'Nina',31,'female','Perm'), (8,'Roman',23,'male','Perm'),
 (9,'Vera',20,'female','Kazan'), (10,'Lev',45,'male','Moscow'),
 (11,'Olga',22,'female','Samara'), (12,'Pavel',18,'male','Omsk');
INSERT INTO pizzeria (id,name,rating) VALUES
 (1,'Pizza Hut',4.15), (2,'Dominos',3.85), (3,'Papa Johns',4.55),
 (4,'Orchard Pizza',4.35), (5,'Metro Slice',3.25);
INSERT INTO menu (id,pizzeria_id,pizza_name,price)
SELECT n, 1 + (n-1)/6,
       (ARRAY['cheese pizza','pepperoni pizza','mushroom pizza',
              'supreme pizza','vegetable pizza','pumpkin pizza'])[1+(n-1)%6],
       560 + ((n-1)%6)*85
FROM generate_series(1,18) AS n;
INSERT INTO person_visits (id,person_id,pizzeria_id,visit_date)
SELECT n, 1+(n-1)%11, 1+(n-1)%4, DATE '2022-01-01'+((n*3)%10)
FROM generate_series(1,35) AS n;
INSERT INTO person_visits (id,person_id,pizzeria_id,visit_date)
VALUES (36,3,3,'2022-01-08'), (37,5,2,'2022-01-08');
INSERT INTO person_order (id,person_id,menu_id,order_date)
SELECT n, 1+(n-1)%11, 1+(n*5)%16, DATE '2022-01-01'+((n*2)%9)
FROM generate_series(1,48) AS n;
ANALYZE;
