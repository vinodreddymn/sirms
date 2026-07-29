-- 014_seed_sequences.sql

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab02', 'ASSET_UPS', 'UPS', 20, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, NULL, NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab03', 'LOCATION_POLE', 'POL', 855, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, NULL, NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab05', 'WORK_ORDER', 'WO', 75, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, '2026-07-19 23:10:21.571472', NULL) ON CONFLICT DO NOTHING;

INSERT INTO common.number_sequences VALUES ('abababab-abab-abab-abab-ababababab04', 'INCIDENT', 'INC', 157, 6, 'NEVER', NULL, true, '2026-07-16 23:05:46.411143', NULL, '2026-07-19 23:12:22.075717', NULL) ON CONFLICT DO NOTHING;

