DO $$ BEGIN
IF (SELECT count(*) FROM pizzeria) <> 5 THEN RAISE EXCEPTION 'Isolation fixture mismatch'; END IF;
END $$;
