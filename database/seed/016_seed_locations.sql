CALL infrastructure.add_location(
    'NAISS-INS-RAJALI',
    'BUILDING',
    'BLD-C2',
    'C2 Building',
    'Main Control Building'
);

CALL infrastructure.add_floor(
    'BLD-C2',
    'GF',
    'Ground Floor'
);

CALL infrastructure.add_room(
    'GF',
    'CONFERENCE',
    'Conference Room'
);