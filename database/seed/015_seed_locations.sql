
-- 015_seed_locations.sql
-- SIRMS Location Seed (Starter Template)
-- PostgreSQL 17

BEGIN;

DO $$
DECLARE
    v_root uuid;
    v_parent uuid;
    v_ps uuid;
    i int;
BEGIN
    SELECT id INTO v_root
    FROM infrastructure.locations
    WHERE code='NAISS-INS-RAJALI';

    IF v_root IS NULL THEN
        RAISE EXCEPTION 'Root location NAISS-INS-RAJALI not found';
    END IF;

    -- Buildings container
    INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
    SELECT v_root,2,'BLD-C2','C2 Building'
    WHERE NOT EXISTS (SELECT 1 FROM infrastructure.locations WHERE code='BLD-C2');

    SELECT id INTO v_parent FROM infrastructure.locations WHERE code='BLD-C2';

    -- Floors
    FOREACH i IN ARRAY ARRAY[1,2,3]
    LOOP
        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_parent,3,
               CASE i WHEN 1 THEN 'GF' WHEN 2 THEN 'FF' ELSE 'SF' END,
               CASE i WHEN 1 THEN 'Ground Floor'
                      WHEN 2 THEN 'First Floor'
                      ELSE 'Second Floor' END
        WHERE NOT EXISTS(
            SELECT 1 FROM infrastructure.locations
            WHERE code=CASE i WHEN 1 THEN 'GF' WHEN 2 THEN 'FF' ELSE 'SF' END);
    END LOOP;

    -- Power Stations parent
    INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
    SELECT v_root,14,'POWER-STATIONS','Power Stations'
    WHERE NOT EXISTS (SELECT 1 FROM infrastructure.locations WHERE code='POWER-STATIONS');

    SELECT id INTO v_parent FROM infrastructure.locations WHERE code='POWER-STATIONS';

    FOR i IN 1..9 LOOP
        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_parent,5,
               format('PS-%02s',i),
               format('Power Station %02s',i)
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('PS-%02s',i));

        SELECT id INTO v_ps
        FROM infrastructure.locations
        WHERE code=format('PS-%02s',i);

        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_ps,6,format('EQP_ROOM_PS_%02s',i),'Equipment Room'
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('EQP_ROOM_PS_%02s',i));

        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_ps,6,format('UPS_ROOM_PS_%02s',i),'UPS Room'
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('UPS_ROOM_PS_%02s',i));

        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_ps,6,format('OUTDOOR_PS_%02s',i),'Outdoor Area'
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('OUTDOOR_PS_%02s',i));

        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_ps,6,format('BATTERY_PS_%02s',i),'Battery Bank'
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('BATTERY_PS_%02s',i));

        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_ps,6,format('DG_PS_%02s',i),'DG Area'
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('DG_PS_%02s',i));
    END LOOP;

    -- Watch towers
    INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
    SELECT v_root,8,'WATCH-TOWERS','Watch Towers'
    WHERE NOT EXISTS (SELECT 1 FROM infrastructure.locations WHERE code='WATCH-TOWERS');

    SELECT id INTO v_parent FROM infrastructure.locations WHERE code='WATCH-TOWERS';

    FOR i IN 1..40 LOOP
        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_parent,8,
               format('WT-%02s',i),
               format('Watch Tower %02s',i)
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('WT-%02s',i));
    END LOOP;

    -- Poles
    INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
    SELECT v_root,7,'POLES','Perimeter Poles'
    WHERE NOT EXISTS (SELECT 1 FROM infrastructure.locations WHERE code='POLES');

    SELECT id INTO v_parent FROM infrastructure.locations WHERE code='POLES';

    FOR i IN 1..180 LOOP
        INSERT INTO infrastructure.locations(parent_location_id,location_type_id,code,name)
        SELECT v_parent,7,
               format('P-%03s',i),
               format('Pole %03s',i)
        WHERE NOT EXISTS (
            SELECT 1 FROM infrastructure.locations
            WHERE code=format('P-%03s',i));
    END LOOP;

END $$;

COMMIT;
