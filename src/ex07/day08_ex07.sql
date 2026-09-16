BEGIN;
UPDATE pizzeria
SET rating = 5
WHERE name = 'Pizza Hut';
UPDATE pizzeria
SET rating = 5
WHERE name = 'Dominos';
COMMIT;
SELECT sum(rating) FROM pizzeria;
BEGIN;
UPDATE pizzeria
SET rating = 4
WHERE name = 'Dominos';
UPDATE pizzeria
SET rating = 4
WHERE name = 'Pizza Hut';
COMMIT;
SELECT sum(rating) FROM pizzeria;
