-- 014_seed_sequences.sql

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab02', 'ASSET_UPS', 'UPS', 20, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, NULL, NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab03', 'LOCATION_POLE', 'POL', 855, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, NULL, NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab05', 'WORK_ORDER', 'WO', 75, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, '2026-07-19 23:10:21.571472', NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab06', 'PREVENTIVE_MAINTENANCE', 'PM', 0, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, NULL, NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab04', 'INCIDENT', 'INC', 157, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, '2026-07-19 23:12:22.075717', NULL) ON CONFLICT DO NOTHING;

-- Work-type sequences for all codes introduced in migration 008
-- (INSTALLATION, BREAKDOWN_MAINTENANCE, etc. were missing, causing 422 errors)
INSERT INTO common.number_sequences (entity_name, prefix, current_value, number_length, reset_policy)
VALUES
    ('INSTALLATION',           'INS', 0, 6, 'NEVER'),
    ('BREAKDOWN_MAINTENANCE',  'BM',  0, 6, 'NEVER'),
    ('CORRECTIVE_MAINTENANCE', 'CM',  0, 6, 'NEVER'),
    ('INSPECTION',             'INP', 0, 6, 'NEVER'),
    ('RELOCATION',             'REL', 0, 6, 'NEVER'),
    ('VENDOR_REPAIR',          'VR',  0, 6, 'NEVER'),
    ('CALIBRATION',            'CAL', 0, 6, 'NEVER'),
    ('GENERAL_TASK',           'GT',  0, 6, 'NEVER'),
    ('WARRANTY',               'WAR', 0, 6, 'NEVER'),
    ('UPGRADE',                'UPG', 0, 6, 'NEVER'),
    ('DECOMMISSION',           'DEC', 0, 6, 'NEVER')
ON CONFLICT (entity_name) DO NOTHING;

