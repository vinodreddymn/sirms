-- ============================================================================
-- SURVEILLANCE
-- ============================================================================

------------------------------------------------------------------------------
-- FIXED CAMERA
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code = 'SURVEILLANCE'
      AND s.code = 'FIXED_CAMERA'
)
INSERT INTO master.specification_definitions
(asset_category_id, asset_subcategory_id, code, name, data_type, unit_of_measure,
 required_flag, display_order, is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('IP_ADDRESS','IP Address','TEXT',NULL,TRUE,1),
('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,2),
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,3),
('MODEL','Model','TEXT',NULL,TRUE,4),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,5),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,6),
('HARDWARE_VERSION','Hardware Version','TEXT',NULL,FALSE,7),
('HOSTNAME','Hostname','TEXT',NULL,FALSE,8),
('RESOLUTION','Resolution','TEXT',NULL,TRUE,9),
('FRAME_RATE','Frame Rate','NUMBER','FPS',FALSE,10),
('VIDEO_COMPRESSION','Video Compression','TEXT',NULL,FALSE,11),
('IMAGE_SENSOR','Image Sensor','TEXT',NULL,FALSE,12),
('LENS_SIZE','Lens Size','NUMBER','mm',FALSE,13),
('IR_RANGE','IR Range','NUMBER','m',FALSE,14),
('DAY_NIGHT_MODE','Day/Night Mode','BOOLEAN',NULL,FALSE,15),
('WDR','Wide Dynamic Range','BOOLEAN',NULL,FALSE,16),
('ONVIF_VERSION','ONVIF Version','TEXT',NULL,FALSE,17),
('POWER_TYPE','Power Type','TEXT',NULL,FALSE,18),
('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,19),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,20),
('IP_RATING','Ingress Protection Rating','TEXT',NULL,FALSE,21),
('INSTALLATION_HEIGHT','Installation Height','NUMBER','m',FALSE,22),
('FIELD_OF_VIEW','Field of View','NUMBER','Degree',FALSE,23),
('STREAM_URL','Primary Stream URL','TEXT',NULL,FALSE,24),
('NOTES','Remarks','TEXT',NULL,FALSE,25)
) AS v(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- PTZ CAMERA
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='SURVEILLANCE'
      AND s.code='PTZ_CAMERA'
)
INSERT INTO master.specification_definitions
(asset_category_id,asset_subcategory_id,code,name,data_type,unit_of_measure,
required_flag,display_order,is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('IP_ADDRESS','IP Address','TEXT',NULL,TRUE,1),
('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,2),
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,3),
('MODEL','Model','TEXT',NULL,TRUE,4),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,5),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,6),
('HOSTNAME','Hostname','TEXT',NULL,FALSE,7),
('RESOLUTION','Resolution','TEXT',NULL,TRUE,8),
('OPTICAL_ZOOM','Optical Zoom','NUMBER','X',TRUE,9),
('DIGITAL_ZOOM','Digital Zoom','NUMBER','X',FALSE,10),
('PAN_RANGE','Pan Range','NUMBER','Degree',TRUE,11),
('TILT_RANGE','Tilt Range','NUMBER','Degree',TRUE,12),
('PAN_SPEED','Pan Speed','NUMBER','Degree/Sec',FALSE,13),
('TILT_SPEED','Tilt Speed','NUMBER','Degree/Sec',FALSE,14),
('PRESET_COUNT','Preset Count','NUMBER',NULL,FALSE,15),
('PATROL_SUPPORTED','Patrol Supported','BOOLEAN',NULL,FALSE,16),
('AUTO_TRACKING','Auto Tracking','BOOLEAN',NULL,FALSE,17),
('IR_RANGE','IR Range','NUMBER','m',FALSE,18),
('ONVIF_VERSION','ONVIF Version','TEXT',NULL,FALSE,19),
('POWER_TYPE','Power Type','TEXT',NULL,FALSE,20),
('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,21),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,22),
('IP_RATING','Ingress Protection Rating','TEXT',NULL,FALSE,23),
('STREAM_URL','Primary Stream URL','TEXT',NULL,FALSE,24),
('NOTES','Remarks','TEXT',NULL,FALSE,25)
) AS v(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- THERMAL CAMERA
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='SURVEILLANCE'
      AND s.code='THERMAL_CAMERA'
)
INSERT INTO master.specification_definitions
(asset_category_id,asset_subcategory_id,code,name,data_type,unit_of_measure,
required_flag,display_order,is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('IP_ADDRESS','IP Address','TEXT',NULL,TRUE,1),
('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,2),
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,3),
('MODEL','Model','TEXT',NULL,TRUE,4),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,5),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,6),
('THERMAL_RESOLUTION','Thermal Resolution','TEXT',NULL,TRUE,7),
('VISIBLE_RESOLUTION','Visible Resolution','TEXT',NULL,FALSE,8),
('SPECTRAL_RANGE','Spectral Range','TEXT',NULL,FALSE,9),
('TEMPERATURE_RANGE','Temperature Range','TEXT',NULL,FALSE,10),
('DETECTION_DISTANCE','Detection Distance','NUMBER','m',FALSE,11),
('LENS_SIZE','Lens Size','NUMBER','mm',FALSE,12),
('FRAME_RATE','Frame Rate','NUMBER','FPS',FALSE,13),
('ONVIF_VERSION','ONVIF Version','TEXT',NULL,FALSE,14),
('POWER_TYPE','Power Type','TEXT',NULL,FALSE,15),
('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,16),
('IP_RATING','Ingress Protection Rating','TEXT',NULL,FALSE,17),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,18),
('STREAM_URL','Primary Stream URL','TEXT',NULL,FALSE,19),
('NOTES','Remarks','TEXT',NULL,FALSE,20)
) AS v(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;


-- ============================================================================
-- NETWORK
-- ============================================================================

------------------------------------------------------------------------------
-- ACCESS SWITCH
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='NETWORK'
      AND s.code='ACCESS_SWITCH'
)
INSERT INTO master.specification_definitions
(asset_category_id, asset_subcategory_id, code, name, data_type,
 unit_of_measure, required_flag, display_order, is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('MGMT_IP','Management IP','TEXT',NULL,TRUE,1),
('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,2),
('HOSTNAME','Hostname','TEXT',NULL,FALSE,3),
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,4),
('MODEL','Model','TEXT',NULL,TRUE,5),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,6),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,7),
('PORT_COUNT','Number of Ports','NUMBER',NULL,TRUE,8),
('POE_PORTS','PoE Ports','NUMBER',NULL,FALSE,9),
('SFP_PORTS','SFP Ports','NUMBER',NULL,FALSE,10),
('SFP_PLUS_PORTS','SFP+ Ports','NUMBER',NULL,FALSE,11),
('UPLINK_PORTS','Uplink Ports','NUMBER',NULL,FALSE,12),
('STACKABLE','Stackable','BOOLEAN',NULL,FALSE,13),
('STACK_ID','Stack ID','TEXT',NULL,FALSE,14),
('SWITCHING_CAPACITY','Switching Capacity','NUMBER','Gbps',FALSE,15),
('FORWARDING_RATE','Forwarding Rate','NUMBER','Mpps',FALSE,16),
('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,17),
('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,18),
('INPUT_VOLTAGE','Input Voltage','NUMBER','V',FALSE,19),
('SUPPORTED_VLANS','Supported VLANs','NUMBER',NULL,FALSE,20),
('MAX_MAC_ENTRIES','MAC Address Table Size','NUMBER',NULL,FALSE,21),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,22),
('RACK_UNITS','Rack Size','NUMBER','U',FALSE,23),
('LOCATION_RACK','Rack Position','TEXT',NULL,FALSE,24),
('NOTES','Remarks','TEXT',NULL,FALSE,25)
) AS v(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- DISTRIBUTION SWITCH
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='NETWORK'
      AND s.code='DISTRIBUTION_SWITCH'
)
INSERT INTO master.specification_definitions
(asset_category_id, asset_subcategory_id, code, name, data_type,
 unit_of_measure, required_flag, display_order, is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('MGMT_IP','Management IP','TEXT',NULL,TRUE,1),
('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,2),
('HOSTNAME','Hostname','TEXT',NULL,FALSE,3),
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,4),
('MODEL','Model','TEXT',NULL,TRUE,5),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,6),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,7),
('PORT_COUNT','Number of Ports','NUMBER',NULL,TRUE,8),
('POE_PORTS','PoE Ports','NUMBER',NULL,FALSE,9),
('SFP_PORTS','SFP Ports','NUMBER',NULL,FALSE,10),
('SFP_PLUS_PORTS','SFP+ Ports','NUMBER',NULL,FALSE,11),
('STACKABLE','Stackable','BOOLEAN',NULL,FALSE,12),
('SWITCHING_CAPACITY','Switching Capacity','NUMBER','Gbps',FALSE,13),
('FORWARDING_RATE','Forwarding Rate','NUMBER','Mpps',FALSE,14),
('SUPPORTED_VLANS','Supported VLANs','NUMBER',NULL,FALSE,15),
('ROUTING_SUPPORTED','Layer-3 Routing','BOOLEAN',NULL,FALSE,16),
('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,17),
('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,18),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,19),
('RACK_UNITS','Rack Size','NUMBER','U',FALSE,20),
('LOCATION_RACK','Rack Position','TEXT',NULL,FALSE,21),
('NOTES','Remarks','TEXT',NULL,FALSE,22)
) AS v(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- CORE SWITCH
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='NETWORK'
      AND s.code='CORE_SWITCH'
)
INSERT INTO master.specification_definitions
(asset_category_id, asset_subcategory_id, code, name, data_type,
 unit_of_measure, required_flag, display_order, is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('MGMT_IP','Management IP','TEXT',NULL,TRUE,1),
('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,2),
('HOSTNAME','Hostname','TEXT',NULL,FALSE,3),
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,4),
('MODEL','Model','TEXT',NULL,TRUE,5),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,6),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,7),
('PORT_COUNT','Number of Ports','NUMBER',NULL,TRUE,8),
('SFP_PORTS','SFP Ports','NUMBER',NULL,FALSE,9),
('SFP_PLUS_PORTS','SFP+ Ports','NUMBER',NULL,FALSE,10),
('QSFP_PORTS','QSFP Ports','NUMBER',NULL,FALSE,11),
('STACKABLE','Stackable','BOOLEAN',NULL,FALSE,12),
('SWITCHING_CAPACITY','Switching Capacity','NUMBER','Tbps',FALSE,13),
('FORWARDING_RATE','Forwarding Rate','NUMBER','Mpps',FALSE,14),
('ROUTING_SUPPORTED','Layer-3 Routing','BOOLEAN',NULL,FALSE,15),
('REDUNDANT_POWER','Redundant Power Supply','BOOLEAN',NULL,FALSE,16),
('REDUNDANT_SUPERVISOR','Redundant Supervisor','BOOLEAN',NULL,FALSE,17),
('SUPPORTED_VLANS','Supported VLANs','NUMBER',NULL,FALSE,18),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,19),
('RACK_UNITS','Rack Size','NUMBER','U',FALSE,20),
('LOCATION_RACK','Rack Position','TEXT',NULL,FALSE,21),
('NOTES','Remarks','TEXT',NULL,FALSE,22)
) AS v(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- POWER
-- ============================================================================

------------------------------------------------------------------------------
-- UPS
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='POWER'
      AND s.code='UPS'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,4),

('CAPACITY_KVA','Capacity','NUMBER','kVA',TRUE,5),
('OUTPUT_POWER_KW','Output Power','NUMBER','kW',FALSE,6),

('INPUT_VOLTAGE','Input Voltage','NUMBER','V',TRUE,7),
('OUTPUT_VOLTAGE','Output Voltage','NUMBER','V',TRUE,8),
('INPUT_FREQUENCY','Input Frequency','NUMBER','Hz',FALSE,9),
('OUTPUT_FREQUENCY','Output Frequency','NUMBER','Hz',FALSE,10),

('INPUT_PHASE','Input Phase','TEXT',NULL,FALSE,11),
('OUTPUT_PHASE','Output Phase','TEXT',NULL,FALSE,12),

('EFFICIENCY','Efficiency','NUMBER','%',FALSE,13),

('BATTERY_TYPE','Battery Type','TEXT',NULL,FALSE,14),
('BATTERY_QUANTITY','Battery Quantity','NUMBER',NULL,FALSE,15),
('BATTERY_VOLTAGE','Battery Voltage','NUMBER','V',FALSE,16),
('BATTERY_CAPACITY','Battery Capacity','NUMBER','Ah',FALSE,17),

('BACKUP_TIME','Backup Time','NUMBER','Minutes',FALSE,18),
('RECHARGE_TIME','Recharge Time','NUMBER','Hours',FALSE,19),

('BYPASS_AVAILABLE','Static Bypass','BOOLEAN',NULL,FALSE,20),
('MANUAL_BYPASS','Manual Bypass','BOOLEAN',NULL,FALSE,21),

('SNMP_SUPPORTED','SNMP Supported','BOOLEAN',NULL,FALSE,22),
('NETWORK_CARD','Network Management Card','BOOLEAN',NULL,FALSE,23),

('LCD_DISPLAY','LCD Display','BOOLEAN',NULL,FALSE,24),
('ALARMS_SUPPORTED','Alarm Support','BOOLEAN',NULL,FALSE,25),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,26),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,27),
('HUMIDITY','Operating Humidity','TEXT',NULL,FALSE,28),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,29),

('RACK_MOUNTABLE','Rack Mountable','BOOLEAN',NULL,FALSE,30),
('RACK_SIZE','Rack Size','NUMBER','U',FALSE,31),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,32),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,33),
('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,34),

('AMC_AVAILABLE','AMC Available','BOOLEAN',NULL,FALSE,35),

('NOTES','Remarks','TEXT',NULL,FALSE,36)

) AS v(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- BATTERY BANK
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id, s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='POWER'
      AND s.code='BATTERY_BANK'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('BATTERY_TYPE','Battery Type','TEXT',NULL,TRUE,4),
('CHEMISTRY','Battery Chemistry','TEXT',NULL,FALSE,5),

('CELL_COUNT','Number of Cells','NUMBER',NULL,FALSE,6),
('BATTERY_COUNT','Number of Batteries','NUMBER',NULL,TRUE,7),

('CAPACITY_AH','Capacity','NUMBER','Ah',TRUE,8),
('VOLTAGE','Voltage','NUMBER','V',TRUE,9),

('FLOAT_VOLTAGE','Float Voltage','NUMBER','V',FALSE,10),
('BOOST_VOLTAGE','Boost Voltage','NUMBER','V',FALSE,11),

('CHARGE_CURRENT','Charge Current','NUMBER','A',FALSE,12),
('DISCHARGE_CURRENT','Discharge Current','NUMBER','A',FALSE,13),

('BACKUP_TIME','Expected Backup','NUMBER','Minutes',FALSE,14),

('INTERNAL_RESISTANCE','Internal Resistance','NUMBER','mΩ',FALSE,15),

('DESIGN_LIFE','Design Life','NUMBER','Years',FALSE,16),

('MANUFACTURING_DATE','Manufacturing Date','DATE',NULL,FALSE,17),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,18),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,19),

('NEXT_REPLACEMENT_DATE','Replacement Due','DATE',NULL,FALSE,20),

('TERMINAL_TYPE','Terminal Type','TEXT',NULL,FALSE,21),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,22),

('LOCATION','Battery Bank Location','TEXT',NULL,FALSE,23),

('RACK_NUMBER','Rack Number','TEXT',NULL,FALSE,24),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,25),

('NOTES','Remarks','TEXT',NULL,FALSE,26)

) AS v(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- DIESEL GENERATOR
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='POWER'
      AND s.code='DIESEL_GENERATOR'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('ENGINE_MODEL','Engine Model','TEXT',NULL,FALSE,4),
('ENGINE_NUMBER','Engine Number','TEXT',NULL,FALSE,5),
('ALTERNATOR_MODEL','Alternator Model','TEXT',NULL,FALSE,6),

('CAPACITY_KVA','Rated Capacity','NUMBER','kVA',TRUE,7),
('CAPACITY_KW','Rated Capacity','NUMBER','kW',FALSE,8),

('RATED_VOLTAGE','Rated Voltage','NUMBER','V',TRUE,9),
('RATED_CURRENT','Rated Current','NUMBER','A',FALSE,10),
('FREQUENCY','Frequency','NUMBER','Hz',TRUE,11),
('PHASE','Phase','TEXT',NULL,FALSE,12),
('POWER_FACTOR','Power Factor','NUMBER',NULL,FALSE,13),

('RPM','Engine Speed','NUMBER','RPM',FALSE,14),

('STARTING_METHOD','Starting Method','TEXT',NULL,FALSE,15),

('FUEL_TYPE','Fuel Type','TEXT',NULL,FALSE,16),
('FUEL_TANK_CAPACITY','Fuel Tank Capacity','NUMBER','L',FALSE,17),
('FUEL_CONSUMPTION','Fuel Consumption','NUMBER','L/hr',FALSE,18),

('COOLING_TYPE','Cooling Type','TEXT',NULL,FALSE,19),

('ENGINE_OIL_CAPACITY','Engine Oil Capacity','NUMBER','L',FALSE,20),

('BATTERY_VOLTAGE','Starting Battery Voltage','NUMBER','V',FALSE,21),

('EXHAUST_TYPE','Exhaust Type','TEXT',NULL,FALSE,22),

('NOISE_LEVEL','Noise Level','NUMBER','dB',FALSE,23),

('CONTROL_PANEL','Control Panel Model','TEXT',NULL,FALSE,24),

('AUTO_START','Auto Start','BOOLEAN',NULL,FALSE,25),
('AMF_SUPPORTED','AMF Supported','BOOLEAN',NULL,FALSE,26),

('RUNNING_HOURS','Running Hours','NUMBER','Hours',FALSE,27),

('LAST_SERVICE_HOURS','Last Service Hours','NUMBER','Hours',FALSE,28),

('NEXT_SERVICE_HOURS','Next Service Hours','NUMBER','Hours',FALSE,29),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,30),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,31),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,32),

('NOTES','Remarks','TEXT',NULL,FALSE,33)

) AS v
(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- TRANSFORMER
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='POWER'
      AND s.code='TRANSFORMER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('CAPACITY_KVA','Rated Capacity','NUMBER','kVA',TRUE,4),

('PRIMARY_VOLTAGE','Primary Voltage','NUMBER','V',TRUE,5),

('SECONDARY_VOLTAGE','Secondary Voltage','NUMBER','V',TRUE,6),

('PRIMARY_CURRENT','Primary Current','NUMBER','A',FALSE,7),

('SECONDARY_CURRENT','Secondary Current','NUMBER','A',FALSE,8),

('FREQUENCY','Frequency','NUMBER','Hz',TRUE,9),

('PHASE','Phase','TEXT',NULL,FALSE,10),

('VECTOR_GROUP','Vector Group','TEXT',NULL,FALSE,11),

('IMPEDANCE','Impedance','NUMBER','%',FALSE,12),

('INSULATION_CLASS','Insulation Class','TEXT',NULL,FALSE,13),

('COOLING_TYPE','Cooling Type','TEXT',NULL,FALSE,14),

('OIL_TYPE','Transformer Oil Type','TEXT',NULL,FALSE,15),

('OIL_CAPACITY','Oil Capacity','NUMBER','L',FALSE,16),

('TAP_CHANGER','Tap Changer','BOOLEAN',NULL,FALSE,17),

('TAP_RANGE','Tap Range','TEXT',NULL,FALSE,18),

('SHORT_CIRCUIT_LEVEL','Short Circuit Rating','NUMBER','kA',FALSE,19),

('TEMPERATURE_RISE','Temperature Rise','NUMBER','°C',FALSE,20),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,21),

('INSTALLATION_TYPE','Installation Type','TEXT',NULL,FALSE,22),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,23),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,24),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,25),

('NOTES','Remarks','TEXT',NULL,FALSE,26)

) AS v
(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;


------------------------------------------------------------------------------
-- ISOLATION TRANSFORMER
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='POWER'
      AND s.code='ISOLATION_TRANSFORMER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('CAPACITY_KVA','Capacity','NUMBER','kVA',TRUE,4),
('PRIMARY_VOLTAGE','Primary Voltage','NUMBER','V',TRUE,5),
('SECONDARY_VOLTAGE','Secondary Voltage','NUMBER','V',TRUE,6),
('PRIMARY_CURRENT','Primary Current','NUMBER','A',FALSE,7),
('SECONDARY_CURRENT','Secondary Current','NUMBER','A',FALSE,8),
('FREQUENCY','Frequency','NUMBER','Hz',TRUE,9),
('PHASE','Phase','TEXT',NULL,FALSE,10),
('INSULATION_CLASS','Insulation Class','TEXT',NULL,FALSE,11),
('COOLING_TYPE','Cooling Type','TEXT',NULL,FALSE,12),
('IMPEDANCE','Impedance','NUMBER','%',FALSE,13),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,14),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,15),
('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,16),
('NOTES','Remarks','TEXT',NULL,FALSE,17)
) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- HT PANEL
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='POWER'
AND s.code='HT_PANEL'
)
INSERT INTO master.specification_definitions
(asset_category_id,asset_subcategory_id,code,name,data_type,
unit_of_measure,required_flag,display_order,is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('RATED_VOLTAGE','Rated Voltage','NUMBER','kV',TRUE,4),
('RATED_CURRENT','Rated Current','NUMBER','A',TRUE,5),
('BUSBAR_RATING','Busbar Rating','NUMBER','A',FALSE,6),
('SHORT_CIRCUIT_RATING','Short Circuit Rating','NUMBER','kA',FALSE,7),
('BREAKER_TYPE','Breaker Type','TEXT',NULL,FALSE,8),
('BREAKER_COUNT','Breaker Count','NUMBER',NULL,FALSE,9),
('PROTECTION_RELAY','Protection Relay','TEXT',NULL,FALSE,10),
('METERING','Metering Available','BOOLEAN',NULL,FALSE,11),
('IP_RATING','IP Rating','TEXT',NULL,FALSE,12),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,13),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,14),
('NOTES','Remarks','TEXT',NULL,FALSE,15)
) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- LT PANEL
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='POWER'
AND s.code='LT_PANEL'
)
INSERT INTO master.specification_definitions
(asset_category_id,asset_subcategory_id,code,name,data_type,
unit_of_measure,required_flag,display_order,is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('RATED_VOLTAGE','Rated Voltage','NUMBER','V',TRUE,4),
('RATED_CURRENT','Rated Current','NUMBER','A',TRUE,5),
('BUSBAR_RATING','Busbar Rating','NUMBER','A',FALSE,6),
('INCOMING_BREAKERS','Incoming Breakers','NUMBER',NULL,FALSE,7),
('OUTGOING_BREAKERS','Outgoing Breakers','NUMBER',NULL,FALSE,8),
('METERING','Metering Available','BOOLEAN',NULL,FALSE,9),
('PF_METER','Power Factor Meter','BOOLEAN',NULL,FALSE,10),
('ENERGY_METER','Energy Meter','BOOLEAN',NULL,FALSE,11),
('IP_RATING','IP Rating','TEXT',NULL,FALSE,12),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,13),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,14),
('NOTES','Remarks','TEXT',NULL,FALSE,15)
) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- VOLTAGE REGULATOR
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='POWER'
AND s.code='VOLTAGE_REGULATOR'
)
INSERT INTO master.specification_definitions
(asset_category_id,asset_subcategory_id,code,name,data_type,
unit_of_measure,required_flag,display_order,is_active)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES
('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('CAPACITY_KVA','Capacity','NUMBER','kVA',TRUE,4),
('INPUT_VOLTAGE','Input Voltage','NUMBER','V',TRUE,5),
('OUTPUT_VOLTAGE','Output Voltage','NUMBER','V',TRUE,6),
('INPUT_RANGE','Input Range','TEXT',NULL,FALSE,7),
('OUTPUT_ACCURACY','Output Accuracy','NUMBER','%',FALSE,8),
('PHASE','Phase','TEXT',NULL,FALSE,9),
('EFFICIENCY','Efficiency','NUMBER','%',FALSE,10),
('COOLING_TYPE','Cooling Type','TEXT',NULL,FALSE,11),
('BYPASS_AVAILABLE','Bypass Available','BOOLEAN',NULL,FALSE,12),
('DISPLAY_TYPE','Display Type','TEXT',NULL,FALSE,13),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,14),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,15),
('NOTES','Remarks','TEXT',NULL,FALSE,16)
) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- ACCESS CONTROL
-- ============================================================================

------------------------------------------------------------------------------
-- K12 GATE
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='ACCESS'
      AND s.code='K12_GATE'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('GATE_TYPE','Gate Type','TEXT',NULL,TRUE,4),

('CRASH_RATING','Crash Rating','TEXT',NULL,TRUE,5),

('CLEAR_OPENING','Clear Opening Width','NUMBER','m',TRUE,6),

('GATE_HEIGHT','Gate Height','NUMBER','m',FALSE,7),

('GATE_WEIGHT','Gate Weight','NUMBER','kg',FALSE,8),

('MOTOR_TYPE','Motor Type','TEXT',NULL,FALSE,9),

('MOTOR_POWER','Motor Power','NUMBER','kW',FALSE,10),

('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,11),

('CONTROL_VOLTAGE','Control Voltage','NUMBER','V',FALSE,12),

('OPERATING_SPEED','Opening Speed','NUMBER','m/min',FALSE,13),

('OPENING_TIME','Opening Time','NUMBER','sec',FALSE,14),

('CLOSING_TIME','Closing Time','NUMBER','sec',FALSE,15),

('HYDRAULIC_SYSTEM','Hydraulic System','BOOLEAN',NULL,FALSE,16),

('LIMIT_SWITCH_TYPE','Limit Switch Type','TEXT',NULL,FALSE,17),

('ENCODER_AVAILABLE','Encoder Available','BOOLEAN',NULL,FALSE,18),

('SAFETY_LOOP','Safety Loop Detector','BOOLEAN',NULL,FALSE,19),

('PHOTO_SENSOR','Photo Sensor','BOOLEAN',NULL,FALSE,20),

('EMERGENCY_STOP','Emergency Stop','BOOLEAN',NULL,FALSE,21),

('MANUAL_OVERRIDE','Manual Override','BOOLEAN',NULL,FALSE,22),

('PLC_MODEL','PLC Model','TEXT',NULL,FALSE,23),

('HMI_MODEL','HMI Model','TEXT',NULL,FALSE,24),

('CONTROL_PANEL_MODEL','Control Panel','TEXT',NULL,FALSE,25),

('REMOTE_OPERATION','Remote Operation','BOOLEAN',NULL,FALSE,26),

('LOCAL_OPERATION','Local Operation','BOOLEAN',NULL,FALSE,27),

('UPS_BACKUP','UPS Backup','BOOLEAN',NULL,FALSE,28),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,29),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,30),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,31),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,32),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,33),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,34),

('AMC_AVAILABLE','AMC Available','BOOLEAN',NULL,FALSE,35),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,36),

('NOTES','Remarks','TEXT',NULL,FALSE,37)

) AS v
(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- K12 BOLLARD
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='ACCESS'
      AND s.code='K12_BOLLARD'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('CRASH_RATING','Crash Rating','TEXT',NULL,TRUE,4),

('BOLLARD_DIAMETER','Bollard Diameter','NUMBER','mm',FALSE,5),

('BOLLARD_HEIGHT','Bollard Height','NUMBER','mm',FALSE,6),

('BOLLARD_TRAVEL','Travel Distance','NUMBER','mm',FALSE,7),

('MATERIAL','Material','TEXT',NULL,FALSE,8),

('FINISH','Surface Finish','TEXT',NULL,FALSE,9),

('MOTOR_TYPE','Motor Type','TEXT',NULL,FALSE,10),

('HYDRAULIC_POWERPACK','Hydraulic Power Pack','BOOLEAN',NULL,FALSE,11),

('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,12),

('CONTROL_VOLTAGE','Control Voltage','NUMBER','V',FALSE,13),

('RAISE_TIME','Raise Time','NUMBER','sec',FALSE,14),

('LOWER_TIME','Lower Time','NUMBER','sec',FALSE,15),

('LIMIT_SWITCH','Limit Switch','BOOLEAN',NULL,FALSE,16),

('PHOTO_SENSOR','Photo Sensor','BOOLEAN',NULL,FALSE,17),

('LOOP_DETECTOR','Loop Detector','BOOLEAN',NULL,FALSE,18),

('EMERGENCY_STOP','Emergency Stop','BOOLEAN',NULL,FALSE,19),

('MANUAL_OVERRIDE','Manual Override','BOOLEAN',NULL,FALSE,20),

('PLC_MODEL','PLC Model','TEXT',NULL,FALSE,21),

('HMI_MODEL','HMI Model','TEXT',NULL,FALSE,22),

('REMOTE_OPERATION','Remote Operation','BOOLEAN',NULL,FALSE,23),

('LOCAL_OPERATION','Local Operation','BOOLEAN',NULL,FALSE,24),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,25),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,26),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,27),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,28),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,29),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,30),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,31),

('NOTES','Remarks','TEXT',NULL,FALSE,32)

) AS v
(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;


------------------------------------------------------------------------------
-- SLIDING GATE
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='ACCESS'
      AND s.code='SLIDING_GATE'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('GATE_LENGTH','Gate Length','NUMBER','m',TRUE,4),
('GATE_HEIGHT','Gate Height','NUMBER','m',FALSE,5),
('GATE_WEIGHT','Gate Weight','NUMBER','kg',FALSE,6),
('MATERIAL','Material','TEXT',NULL,FALSE,7),
('MOTOR_TYPE','Motor Type','TEXT',NULL,FALSE,8),
('MOTOR_POWER','Motor Power','NUMBER','kW',FALSE,9),
('GEARBOX_RATIO','Gearbox Ratio','TEXT',NULL,FALSE,10),
('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,11),
('CONTROL_VOLTAGE','Control Voltage','NUMBER','V',FALSE,12),
('OPENING_SPEED','Opening Speed','NUMBER','m/min',FALSE,13),
('OPENING_TIME','Opening Time','NUMBER','sec',FALSE,14),
('CLOSING_TIME','Closing Time','NUMBER','sec',FALSE,15),
('LIMIT_SWITCH_TYPE','Limit Switch Type','TEXT',NULL,FALSE,16),
('ENCODER_AVAILABLE','Encoder Available','BOOLEAN',NULL,FALSE,17),
('PHOTO_SENSOR','Photo Sensor','BOOLEAN',NULL,FALSE,18),
('SAFETY_EDGE','Safety Edge','BOOLEAN',NULL,FALSE,19),
('LOOP_DETECTOR','Loop Detector','BOOLEAN',NULL,FALSE,20),
('FLASHING_LAMP','Warning Lamp','BOOLEAN',NULL,FALSE,21),
('EMERGENCY_STOP','Emergency Stop','BOOLEAN',NULL,FALSE,22),
('MANUAL_RELEASE','Manual Release','BOOLEAN',NULL,FALSE,23),
('VFD_MODEL','VFD Model','TEXT',NULL,FALSE,24),
('PLC_MODEL','PLC Model','TEXT',NULL,FALSE,25),
('HMI_MODEL','HMI Model','TEXT',NULL,FALSE,26),
('CONTROL_PANEL_MODEL','Control Panel','TEXT',NULL,FALSE,27),
('REMOTE_OPERATION','Remote Operation','BOOLEAN',NULL,FALSE,28),
('LOCAL_OPERATION','Local Operation','BOOLEAN',NULL,FALSE,29),
('IP_RATING','IP Rating','TEXT',NULL,FALSE,30),
('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,31),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,32),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,33),
('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,34),
('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,35),
('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,36),
('NOTES','Remarks','TEXT',NULL,FALSE,37)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- ACF SLIDING GATE
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='ACCESS'
      AND s.code='ACF_SLIDING_GATE'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('GATE_LENGTH','Gate Length','NUMBER','m',TRUE,4),
('GATE_HEIGHT','Gate Height','NUMBER','m',FALSE,5),
('GATE_WEIGHT','Gate Weight','NUMBER','kg',FALSE,6),
('MATERIAL','Material','TEXT',NULL,FALSE,7),
('MOTOR_TYPE','Motor Type','TEXT',NULL,FALSE,8),
('MOTOR_POWER','Motor Power','NUMBER','kW',FALSE,9),
('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,10),
('CONTROL_VOLTAGE','Control Voltage','NUMBER','V',FALSE,11),
('LIMIT_SWITCH_TYPE','Limit Switch Type','TEXT',NULL,FALSE,12),
('ENCODER_AVAILABLE','Encoder Available','BOOLEAN',NULL,FALSE,13),
('PHOTO_SENSOR','Photo Sensor','BOOLEAN',NULL,FALSE,14),
('LOOP_DETECTOR','Loop Detector','BOOLEAN',NULL,FALSE,15),
('EMERGENCY_STOP','Emergency Stop','BOOLEAN',NULL,FALSE,16),
('PLC_MODEL','PLC Model','TEXT',NULL,FALSE,17),
('HMI_MODEL','HMI Model','TEXT',NULL,FALSE,18),
('REMOTE_OPERATION','Remote Operation','BOOLEAN',NULL,FALSE,19),
('LOCAL_OPERATION','Local Operation','BOOLEAN',NULL,FALSE,20),
('IP_RATING','IP Rating','TEXT',NULL,FALSE,21),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,22),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,23),
('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,24),
('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,25),
('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,26),
('NOTES','Remarks','TEXT',NULL,FALSE,27)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- ACF SWING GATE
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='ACCESS'
      AND s.code='ACF_SWING_GATE'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),
('LEAF_LENGTH','Leaf Length','NUMBER','m',TRUE,4),
('LEAF_WEIGHT','Leaf Weight','NUMBER','kg',FALSE,5),
('OPENING_ANGLE','Opening Angle','NUMBER','Degree',FALSE,6),
('MOTOR_TYPE','Motor Type','TEXT',NULL,FALSE,7),
('MOTOR_POWER','Motor Power','NUMBER','kW',FALSE,8),
('ACTUATOR_TYPE','Actuator Type','TEXT',NULL,FALSE,9),
('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,10),
('CONTROL_VOLTAGE','Control Voltage','NUMBER','V',FALSE,11),
('LIMIT_SWITCH_TYPE','Limit Switch Type','TEXT',NULL,FALSE,12),
('PHOTO_SENSOR','Photo Sensor','BOOLEAN',NULL,FALSE,13),
('LOOP_DETECTOR','Loop Detector','BOOLEAN',NULL,FALSE,14),
('EMERGENCY_STOP','Emergency Stop','BOOLEAN',NULL,FALSE,15),
('MANUAL_RELEASE','Manual Release','BOOLEAN',NULL,FALSE,16),
('PLC_MODEL','PLC Model','TEXT',NULL,FALSE,17),
('HMI_MODEL','HMI Model','TEXT',NULL,FALSE,18),
('REMOTE_OPERATION','Remote Operation','BOOLEAN',NULL,FALSE,19),
('LOCAL_OPERATION','Local Operation','BOOLEAN',NULL,FALSE,20),
('IP_RATING','IP Rating','TEXT',NULL,FALSE,21),
('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,22),
('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,23),
('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,24),
('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,25),
('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,26),
('NOTES','Remarks','TEXT',NULL,FALSE,27)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;


------------------------------------------------------------------------------
-- TYRE SHREDDER
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='ACCESS'
      AND s.code='TYRE_SHREDDER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('SHREDDER_TYPE','Shredder Type','TEXT',NULL,TRUE,4),
('NUMBER_OF_BLADES','Number of Blades','NUMBER',NULL,FALSE,5),
('BLADE_MATERIAL','Blade Material','TEXT',NULL,FALSE,6),
('BLADE_LENGTH','Blade Length','NUMBER','mm',FALSE,7),
('BLADE_THICKNESS','Blade Thickness','NUMBER','mm',FALSE,8),

('OPERATING_WIDTH','Operating Width','NUMBER','mm',FALSE,9),

('MAX_AXLE_LOAD','Maximum Axle Load','NUMBER','Ton',FALSE,10),

('DRIVE_TYPE','Drive Type','TEXT',NULL,FALSE,11),

('MOTOR_TYPE','Motor Type','TEXT',NULL,FALSE,12),
('MOTOR_POWER','Motor Power','NUMBER','kW',FALSE,13),

('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,14),
('CONTROL_VOLTAGE','Control Voltage','NUMBER','V',FALSE,15),

('HYDRAULIC_SYSTEM','Hydraulic System','BOOLEAN',NULL,FALSE,16),

('OPERATING_SPEED','Operating Speed','NUMBER','m/min',FALSE,17),

('LIMIT_SWITCH','Limit Switch','BOOLEAN',NULL,FALSE,18),

('EMERGENCY_STOP','Emergency Stop','BOOLEAN',NULL,FALSE,19),

('PLC_MODEL','PLC Model','TEXT',NULL,FALSE,20),

('HMI_MODEL','HMI Model','TEXT',NULL,FALSE,21),

('REMOTE_OPERATION','Remote Operation','BOOLEAN',NULL,FALSE,22),

('LOCAL_OPERATION','Local Operation','BOOLEAN',NULL,FALSE,23),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,24),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,25),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,26),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,27),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,28),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,29),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,30),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,31),

('NOTES','Remarks','TEXT',NULL,FALSE,32)

) AS v
(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- UVSS (UNDER VEHICLE SURVEILLANCE SYSTEM)
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='ACCESS'
      AND s.code='UVSS'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('CAMERA_COUNT','Camera Count','NUMBER',NULL,FALSE,4),

('CAMERA_RESOLUTION','Camera Resolution','TEXT',NULL,FALSE,5),

('SCAN_SPEED','Scan Speed','NUMBER','km/h',FALSE,6),

('IMAGE_RESOLUTION','Image Resolution','TEXT',NULL,FALSE,7),

('LINE_SCAN_CAMERA','Line Scan Camera','BOOLEAN',NULL,FALSE,8),

('COLOUR_CAMERA','Colour Camera','BOOLEAN',NULL,FALSE,9),

('ANPR_SUPPORTED','ANPR Supported','BOOLEAN',NULL,FALSE,10),

('OCR_SUPPORTED','OCR Supported','BOOLEAN',NULL,FALSE,11),

('UNDERBODY_IMAGING','Underbody Imaging','BOOLEAN',NULL,FALSE,12),

('IMAGE_STITCHING','Image Stitching','BOOLEAN',NULL,FALSE,13),

('DATABASE_STORAGE','Database Storage','TEXT',NULL,FALSE,14),

('NETWORK_INTERFACE','Network Interface','TEXT',NULL,FALSE,15),

('IP_ADDRESS','IP Address','TEXT',NULL,FALSE,16),

('MAC_ADDRESS','MAC Address','TEXT',NULL,FALSE,17),

('HOSTNAME','Hostname','TEXT',NULL,FALSE,18),

('SOFTWARE_VERSION','Software Version','TEXT',NULL,FALSE,19),

('CONTROLLER_MODEL','Controller Model','TEXT',NULL,FALSE,20),

('ILLUMINATION_TYPE','Illumination Type','TEXT',NULL,FALSE,21),

('LED_LIGHT_COUNT','LED Light Count','NUMBER',NULL,FALSE,22),

('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,23),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,24),

('UPS_BACKUP','UPS Backup','BOOLEAN',NULL,FALSE,25),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,26),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,27),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,28),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,29),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,30),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,31),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,32),

('NOTES','Remarks','TEXT',NULL,FALSE,33)

) AS v
(
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- PERIMETER SECURITY
-- ============================================================================

------------------------------------------------------------------------------
-- SEARCH LIGHT
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='PERIMETER'
      AND s.code='SEARCH_LIGHT'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('LIGHT_SOURCE','Light Source','TEXT',NULL,TRUE,4),
('LAMP_TYPE','Lamp Type','TEXT',NULL,FALSE,5),

('LUMINOUS_FLUX','Luminous Flux','NUMBER','Lumens',FALSE,6),

('BEAM_DISTANCE','Beam Distance','NUMBER','m',FALSE,7),

('BEAM_ANGLE','Beam Angle','NUMBER','Degree',FALSE,8),

('COLOUR_TEMPERATURE','Colour Temperature','NUMBER','K',FALSE,9),

('POWER_RATING','Power Rating','NUMBER','W',TRUE,10),

('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,11),

('OPERATING_CURRENT','Operating Current','NUMBER','A',FALSE,12),

('MOUNTING_TYPE','Mounting Type','TEXT',NULL,FALSE,13),

('POLE_HEIGHT','Pole Height','NUMBER','m',FALSE,14),

('ROTATION_SUPPORTED','Pan Rotation','BOOLEAN',NULL,FALSE,15),

('TILT_SUPPORTED','Tilt Control','BOOLEAN',NULL,FALSE,16),

('CONTROL_MODE','Control Mode','TEXT',NULL,FALSE,17),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,18),

('SURGE_PROTECTION','Surge Protection','BOOLEAN',NULL,FALSE,19),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,20),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,21),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,22),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,23),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,24),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,25),

('NOTES','Remarks','TEXT',NULL,FALSE,26)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- PERIMETER LIGHT
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='PERIMETER'
AND s.code='PERIMETER_LIGHT'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('LIGHT_SOURCE','Light Source','TEXT',NULL,TRUE,4),

('LUMINOUS_FLUX','Luminous Flux','NUMBER','Lumens',FALSE,5),

('POWER_RATING','Power Rating','NUMBER','W',TRUE,6),

('SUPPLY_VOLTAGE','Supply Voltage','NUMBER','V',TRUE,7),

('COLOUR_TEMPERATURE','Colour Temperature','NUMBER','K',FALSE,8),

('BEAM_ANGLE','Beam Angle','NUMBER','Degree',FALSE,9),

('POLE_HEIGHT','Pole Height','NUMBER','m',FALSE,10),

('MOUNTING_TYPE','Mounting Type','TEXT',NULL,FALSE,11),

('SURGE_PROTECTION','Surge Protection','BOOLEAN',NULL,FALSE,12),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,13),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,14),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,15),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,16),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,17),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,18),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,19),

('NOTES','Remarks','TEXT',NULL,FALSE,20)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- JUNCTION BOX
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='PERIMETER'
AND s.code='JUNCTION_BOX'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('BOX_TYPE','Box Type','TEXT',NULL,FALSE,4),

('ENCLOSURE_MATERIAL','Enclosure Material','TEXT',NULL,FALSE,5),

('DIMENSIONS','Dimensions','TEXT',NULL,FALSE,6),

('IP_RATING','IP Rating','TEXT',NULL,TRUE,7),

('GLAND_SIZE','Cable Gland Size','TEXT',NULL,FALSE,8),

('GLAND_COUNT','Cable Glands','NUMBER',NULL,FALSE,9),

('TERMINAL_BLOCKS','Terminal Blocks','NUMBER',NULL,FALSE,10),

('EARTHING_POINT','Earthing Point','BOOLEAN',NULL,FALSE,11),

('SURGE_PROTECTION','Surge Protection','BOOLEAN',NULL,FALSE,12),

('MOUNTING_TYPE','Mounting Type','TEXT',NULL,FALSE,13),

('INSTALLATION_LOCATION','Installation Location','TEXT',NULL,FALSE,14),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,15),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,16),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,17),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,18),

('NOTES','Remarks','TEXT',NULL,FALSE,19)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;


-- ============================================================================
-- COMMUNICATION
-- ============================================================================

------------------------------------------------------------------------------
-- IP PHONE
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='COMMUNICATION'
      AND s.code='IP_PHONE'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,4),
('IP_ADDRESS','IP Address','TEXT',NULL,FALSE,5),

('HOSTNAME','Hostname','TEXT',NULL,FALSE,6),

('SIP_VERSION','SIP Version','TEXT',NULL,FALSE,7),

('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,8),

('ETHERNET_PORTS','Ethernet Ports','NUMBER',NULL,FALSE,9),

('POE_SUPPORTED','PoE Supported','BOOLEAN',NULL,FALSE,10),

('DISPLAY_SIZE','Display Size','NUMBER','inch',FALSE,11),

('DISPLAY_TYPE','Display Type','TEXT',NULL,FALSE,12),

('LINE_KEYS','Line Keys','NUMBER',NULL,FALSE,13),

('VOICE_CODEC','Voice Codec','TEXT',NULL,FALSE,14),

('HEADSET_PORT','Headset Port','BOOLEAN',NULL,FALSE,15),

('USB_PORT','USB Port','BOOLEAN',NULL,FALSE,16),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,17),

('BLUETOOTH_SUPPORTED','Bluetooth Supported','BOOLEAN',NULL,FALSE,18),

('POWER_INPUT','Power Input','TEXT',NULL,FALSE,19),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,20),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,21),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,22),

('NOTES','Remarks','TEXT',NULL,FALSE,23)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- IP DISTRESS ALARM
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='IP_DISTRESS_ALARM'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('MAC_ADDRESS','MAC Address','TEXT',NULL,TRUE,4),

('IP_ADDRESS','IP Address','TEXT',NULL,FALSE,5),

('HOSTNAME','Hostname','TEXT',NULL,FALSE,6),

('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,7),

('ALARM_BUTTONS','Alarm Buttons','NUMBER',NULL,FALSE,8),

('MICROPHONE','Microphone','BOOLEAN',NULL,FALSE,9),

('SPEAKER','Speaker','BOOLEAN',NULL,FALSE,10),

('POE_SUPPORTED','PoE Supported','BOOLEAN',NULL,FALSE,11),

('ETHERNET_PORT','Ethernet Port','BOOLEAN',NULL,FALSE,12),

('OPERATING_PROTOCOL','Operating Protocol','TEXT',NULL,FALSE,13),

('OPERATING_VOLTAGE','Operating Voltage','NUMBER','V',FALSE,14),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,15),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,16),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,17),

('NOTES','Remarks','TEXT',NULL,FALSE,18)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- VIDEO CONFERENCE SYSTEM
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='VIDEO_CONFERENCE'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('CAMERA_RESOLUTION','Camera Resolution','TEXT',NULL,FALSE,4),

('CAMERA_ZOOM','Optical Zoom','NUMBER','x',FALSE,5),

('FIELD_OF_VIEW','Field of View','NUMBER','Degree',FALSE,6),

('MICROPHONE_COUNT','Microphone Count','NUMBER',NULL,FALSE,7),

('SPEAKER_OUTPUT','Speaker Output','NUMBER','W',FALSE,8),

('DISPLAY_OUTPUT','Display Output','TEXT',NULL,FALSE,9),

('HDMI_PORTS','HDMI Ports','NUMBER',NULL,FALSE,10),

('USB_PORTS','USB Ports','NUMBER',NULL,FALSE,11),

('LAN_PORTS','LAN Ports','NUMBER',NULL,FALSE,12),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,13),

('BLUETOOTH_SUPPORTED','Bluetooth Supported','BOOLEAN',NULL,FALSE,14),

('OPERATING_SYSTEM','Operating System','TEXT',NULL,FALSE,15),

('SOFTWARE_VERSION','Software Version','TEXT',NULL,FALSE,16),

('SIP_H323_SUPPORTED','SIP/H323 Support','BOOLEAN',NULL,FALSE,17),

('MAX_PARTICIPANTS','Maximum Participants','NUMBER',NULL,FALSE,18),

('POWER_RATING','Power Rating','NUMBER','W',FALSE,19),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,20),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,21),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,22),

('NOTES','Remarks','TEXT',NULL,FALSE,23)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- LTE BASE STATION
-- ============================================================================

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='LTE_BASE_STATION'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('BASE_STATION_TYPE','Base Station Type','TEXT',NULL,FALSE,4),

('FREQUENCY_BAND','Frequency Band','TEXT',NULL,TRUE,5),

('CHANNEL_BANDWIDTH','Channel Bandwidth','NUMBER','MHz',FALSE,6),

('DUPLEX_MODE','Duplex Mode','TEXT',NULL,FALSE,7),

('TRANSMIT_POWER','Transmit Power','NUMBER','W',FALSE,8),

('RECEIVER_SENSITIVITY','Receiver Sensitivity','TEXT',NULL,FALSE,9),

('MIMO_CONFIGURATION','MIMO Configuration','TEXT',NULL,FALSE,10),

('SECTOR_COUNT','Number of Sectors','NUMBER',NULL,FALSE,11),

('GPS_SYNCHRONIZATION','GPS Synchronization','BOOLEAN',NULL,FALSE,12),

('BACKHAUL_INTERFACE','Backhaul Interface','TEXT',NULL,FALSE,13),

('ETHERNET_PORTS','Ethernet Ports','NUMBER',NULL,FALSE,14),

('SFP_PORTS','SFP Ports','NUMBER',NULL,FALSE,15),

('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,16),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,17),

('BATTERY_BACKUP','Battery Backup','BOOLEAN',NULL,FALSE,18),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,19),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,20),

('SOFTWARE_VERSION','Software Version','TEXT',NULL,FALSE,21),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,22),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,23),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,24),

('NOTES','Remarks','TEXT',NULL,FALSE,25)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- LTE TOWER
-- ============================================================================

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='LTE_TOWER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,FALSE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('TOWER_TYPE','Tower Type','TEXT',NULL,TRUE,4),

('HEIGHT','Tower Height','NUMBER','m',TRUE,5),

('MATERIAL','Material','TEXT',NULL,FALSE,6),

('GALVANIZATION','Galvanization','BOOLEAN',NULL,FALSE,7),

('FOUNDATION_TYPE','Foundation Type','TEXT',NULL,FALSE,8),

('WIND_SPEED_RATING','Wind Speed Rating','NUMBER','km/h',FALSE,9),

('ANTENNA_COUNT','Number of Antennas','NUMBER',NULL,FALSE,10),

('LIGHTNING_PROTECTION','Lightning Protection','BOOLEAN',NULL,FALSE,11),

('AVIATION_LIGHT','Aviation Light','BOOLEAN',NULL,FALSE,12),

('EARTHING_RESISTANCE','Earthing Resistance','NUMBER','Ohm',FALSE,13),

('FEEDER_CABLE_TYPE','Feeder Cable Type','TEXT',NULL,FALSE,14),

('FEEDER_LENGTH','Feeder Length','NUMBER','m',FALSE,15),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,16),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,17),

('LAST_INSPECTION_DATE','Last Inspection Date','DATE',NULL,FALSE,18),

('NEXT_INSPECTION_DATE','Next Inspection Date','DATE',NULL,FALSE,19),

('NOTES','Remarks','TEXT',NULL,FALSE,20)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- TETRA BASE STATION
-- ============================================================================

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='TETRA_BASE_STATION'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('OPERATING_FREQUENCY','Operating Frequency','TEXT',NULL,TRUE,4),

('CHANNEL_SPACING','Channel Spacing','NUMBER','kHz',FALSE,5),

('TRANSMIT_POWER','Transmit Power','NUMBER','W',FALSE,6),

('RECEIVER_SENSITIVITY','Receiver Sensitivity','TEXT',NULL,FALSE,7),

('NUMBER_OF_CARRIERS','Number of Carriers','NUMBER',NULL,FALSE,8),

('BACKHAUL_INTERFACE','Backhaul Interface','TEXT',NULL,FALSE,9),

('GPS_SYNCHRONIZATION','GPS Synchronization','BOOLEAN',NULL,FALSE,10),

('ETHERNET_PORTS','Ethernet Ports','NUMBER',NULL,FALSE,11),

('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,12),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,13),

('BATTERY_BACKUP','Battery Backup','BOOLEAN',NULL,FALSE,14),

('SOFTWARE_VERSION','Software Version','TEXT',NULL,FALSE,15),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,16),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,17),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,18),

('NOTES','Remarks','TEXT',NULL,FALSE,19)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- TETRA TOWER
-- ============================================================================

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='TETRA_TOWER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,FALSE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('HEIGHT','Tower Height','NUMBER','m',TRUE,4),

('TOWER_TYPE','Tower Type','TEXT',NULL,FALSE,5),

('MATERIAL','Material','TEXT',NULL,FALSE,6),

('FOUNDATION_TYPE','Foundation Type','TEXT',NULL,FALSE,7),

('ANTENNA_COUNT','Number of Antennas','NUMBER',NULL,FALSE,8),

('LIGHTNING_PROTECTION','Lightning Protection','BOOLEAN',NULL,FALSE,9),

('AVIATION_LIGHT','Aviation Light','BOOLEAN',NULL,FALSE,10),

('EARTHING_RESISTANCE','Earthing Resistance','NUMBER','Ohm',FALSE,11),

('FEEDER_CABLE_TYPE','Feeder Cable Type','TEXT',NULL,FALSE,12),

('FEEDER_LENGTH','Feeder Length','NUMBER','m',FALSE,13),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,14),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,15),

('LAST_INSPECTION_DATE','Last Inspection Date','DATE',NULL,FALSE,16),

('NEXT_INSPECTION_DATE','Next Inspection Date','DATE',NULL,FALSE,17),

('NOTES','Remarks','TEXT',NULL,FALSE,18)

) AS v
(code,name,data_type,unit_of_measure,required_flag,display_order)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- RUGGED TABLET
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='RUGGED_TABLET'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('IMEI_NUMBER','IMEI Number','TEXT',NULL,FALSE,4),
('SIM_NUMBER','SIM Number','TEXT',NULL,FALSE,5),

('OPERATING_SYSTEM','Operating System','TEXT',NULL,TRUE,6),

('OS_VERSION','OS Version','TEXT',NULL,FALSE,7),

('PROCESSOR','Processor','TEXT',NULL,FALSE,8),

('RAM','RAM','NUMBER','GB',FALSE,9),

('STORAGE','Internal Storage','NUMBER','GB',FALSE,10),

('DISPLAY_SIZE','Display Size','NUMBER','inch',FALSE,11),

('DISPLAY_RESOLUTION','Display Resolution','TEXT',NULL,FALSE,12),

('TOUCH_TYPE','Touch Screen Type','TEXT',NULL,FALSE,13),

('BATTERY_CAPACITY','Battery Capacity','NUMBER','mAh',FALSE,14),

('BATTERY_TYPE','Battery Type','TEXT',NULL,FALSE,15),

('CAMERA_FRONT','Front Camera','TEXT',NULL,FALSE,16),

('CAMERA_REAR','Rear Camera','TEXT',NULL,FALSE,17),

('GPS_SUPPORTED','GPS Supported','BOOLEAN',NULL,FALSE,18),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,19),

('BLUETOOTH_SUPPORTED','Bluetooth Supported','BOOLEAN',NULL,FALSE,20),

('NFC_SUPPORTED','NFC Supported','BOOLEAN',NULL,FALSE,21),

('USB_PORT_TYPE','USB Port Type','TEXT',NULL,FALSE,22),

('EXPANSION_SLOT','Memory Card Slot','BOOLEAN',NULL,FALSE,23),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,24),

('MIL_STD_CERTIFICATION','MIL-STD Certification','TEXT',NULL,FALSE,25),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,26),

('WEIGHT','Weight','NUMBER','kg',FALSE,27),

('INSTALLATION_DATE','Issue Date','DATE',NULL,FALSE,28),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,29),

('NOTES','Remarks','TEXT',NULL,FALSE,30)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- GPS TAG
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMMUNICATION'
AND s.code='GPS_TAG'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('IMEI_NUMBER','IMEI Number','TEXT',NULL,FALSE,4),

('SIM_NUMBER','SIM Number','TEXT',NULL,FALSE,5),

('GNSS_SYSTEM','GNSS System','TEXT',NULL,FALSE,6),

('POSITION_ACCURACY','Position Accuracy','NUMBER','m',FALSE,7),

('TRACKING_MODE','Tracking Mode','TEXT',NULL,FALSE,8),

('REPORTING_INTERVAL','Reporting Interval','NUMBER','sec',FALSE,9),

('GEOFENCING_SUPPORTED','Geofencing','BOOLEAN',NULL,FALSE,10),

('SOS_BUTTON','SOS Button','BOOLEAN',NULL,FALSE,11),

('MOTION_SENSOR','Motion Sensor','BOOLEAN',NULL,FALSE,12),

('ACCELEROMETER','Accelerometer','BOOLEAN',NULL,FALSE,13),

('BATTERY_CAPACITY','Battery Capacity','NUMBER','mAh',FALSE,14),

('BATTERY_BACKUP','Battery Backup','NUMBER','Hours',FALSE,15),

('CHARGING_TYPE','Charging Type','TEXT',NULL,FALSE,16),

('LTE_SUPPORTED','LTE Supported','BOOLEAN',NULL,FALSE,17),

('GSM_SUPPORTED','GSM Supported','BOOLEAN',NULL,FALSE,18),

('BLUETOOTH_SUPPORTED','Bluetooth Supported','BOOLEAN',NULL,FALSE,19),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,20),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,21),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,22),

('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,23),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,24),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,25),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,26),

('NOTES','Remarks','TEXT',NULL,FALSE,27)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- COMPUTING
-- ============================================================================

------------------------------------------------------------------------------
-- SERVER
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id = c.id
    WHERE c.code='COMPUTING'
      AND s.code='SERVER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('FORM_FACTOR','Form Factor','TEXT',NULL,FALSE,4),

('RACK_SIZE','Rack Size','TEXT',NULL,FALSE,5),

('PROCESSOR_MODEL','Processor Model','TEXT',NULL,TRUE,6),

('PROCESSOR_COUNT','Number of CPUs','NUMBER',NULL,FALSE,7),

('TOTAL_CORES','Total CPU Cores','NUMBER',NULL,FALSE,8),

('TOTAL_THREADS','Total Threads','NUMBER',NULL,FALSE,9),

('RAM_TYPE','Memory Type','TEXT',NULL,FALSE,10),

('RAM_CAPACITY','Installed RAM','NUMBER','GB',TRUE,11),

('RAM_SLOTS','Memory Slots','NUMBER',NULL,FALSE,12),

('STORAGE_TYPE','Storage Type','TEXT',NULL,FALSE,13),

('STORAGE_CAPACITY','Storage Capacity','NUMBER','TB',FALSE,14),

('DRIVE_BAYS','Drive Bays','NUMBER',NULL,FALSE,15),

('RAID_CONTROLLER','RAID Controller','TEXT',NULL,FALSE,16),

('RAID_LEVEL','Configured RAID','TEXT',NULL,FALSE,17),

('NIC_PORTS','Network Ports','NUMBER',NULL,FALSE,18),

('NIC_SPEED','NIC Speed','TEXT',NULL,FALSE,19),

('ILO_IDRAC_VERSION','iLO / iDRAC Version','TEXT',NULL,FALSE,20),

('POWER_SUPPLY_COUNT','Power Supplies','NUMBER',NULL,FALSE,21),

('POWER_REDUNDANT','Redundant Power','BOOLEAN',NULL,FALSE,22),

('POWER_RATING','Power Rating','NUMBER','W',FALSE,23),

('OPERATING_SYSTEM','Operating System','TEXT',NULL,FALSE,24),

('OS_VERSION','OS Version','TEXT',NULL,FALSE,25),

('VIRTUALIZATION','Virtualization Enabled','BOOLEAN',NULL,FALSE,26),

('TPM_VERSION','TPM Version','TEXT',NULL,FALSE,27),

('BIOS_VERSION','BIOS Version','TEXT',NULL,FALSE,28),

('FIRMWARE_VERSION','Firmware Version','TEXT',NULL,FALSE,29),

('MAC_ADDRESS','MAC Address','TEXT',NULL,FALSE,30),

('IP_ADDRESS','IP Address','TEXT',NULL,FALSE,31),

('HOSTNAME','Hostname','TEXT',NULL,FALSE,32),

('RACK_LOCATION','Rack Location','TEXT',NULL,FALSE,33),

('UPS_CONNECTED','Connected to UPS','BOOLEAN',NULL,FALSE,34),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,35),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,36),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,37),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,38),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,39),

('NOTES','Remarks','TEXT',NULL,FALSE,40)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- WORKSTATION
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMPUTING'
AND s.code='WORKSTATION'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('PROCESSOR_MODEL','Processor Model','TEXT',NULL,TRUE,4),

('RAM_CAPACITY','Installed RAM','NUMBER','GB',FALSE,5),

('RAM_TYPE','Memory Type','TEXT',NULL,FALSE,6),

('STORAGE_TYPE','Storage Type','TEXT',NULL,FALSE,7),

('STORAGE_CAPACITY','Storage Capacity','NUMBER','GB',FALSE,8),

('GRAPHICS_CARD','Graphics Card','TEXT',NULL,FALSE,9),

('GRAPHICS_MEMORY','Graphics Memory','NUMBER','GB',FALSE,10),

('DISPLAY_OUTPUTS','Display Outputs','TEXT',NULL,FALSE,11),

('NETWORK_PORTS','Network Ports','NUMBER',NULL,FALSE,12),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,13),

('BLUETOOTH_SUPPORTED','Bluetooth Supported','BOOLEAN',NULL,FALSE,14),

('OPERATING_SYSTEM','Operating System','TEXT',NULL,FALSE,15),

('OS_VERSION','OS Version','TEXT',NULL,FALSE,16),

('TPM_VERSION','TPM Version','TEXT',NULL,FALSE,17),

('BIOS_VERSION','BIOS Version','TEXT',NULL,FALSE,18),

('MAC_ADDRESS','MAC Address','TEXT',NULL,FALSE,19),

('IP_ADDRESS','IP Address','TEXT',NULL,FALSE,20),

('HOSTNAME','Hostname','TEXT',NULL,FALSE,21),

('POWER_RATING','Power Rating','NUMBER','W',FALSE,22),

('UPS_CONNECTED','Connected to UPS','BOOLEAN',NULL,FALSE,23),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,24),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,25),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,26),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,27),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,28),

('NOTES','Remarks','TEXT',NULL,FALSE,29)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- DESKTOP
------------------------------------------------------------------------------

WITH ids AS (
    SELECT c.id AS category_id,
           s.id AS subcategory_id
    FROM master.asset_categories c
    JOIN master.asset_subcategories s
      ON s.asset_category_id=c.id
    WHERE c.code='COMPUTING'
      AND s.code='DESKTOP'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('PROCESSOR_MODEL','Processor Model','TEXT',NULL,TRUE,4),
('PROCESSOR_GENERATION','Processor Generation','TEXT',NULL,FALSE,5),

('RAM_CAPACITY','Installed RAM','NUMBER','GB',FALSE,6),
('RAM_TYPE','Memory Type','TEXT',NULL,FALSE,7),

('STORAGE_TYPE','Storage Type','TEXT',NULL,FALSE,8),
('STORAGE_CAPACITY','Storage Capacity','NUMBER','GB',FALSE,9),

('GRAPHICS_TYPE','Graphics Type','TEXT',NULL,FALSE,10),

('DISPLAY_OUTPUTS','Display Outputs','TEXT',NULL,FALSE,11),

('USB_PORTS','USB Ports','NUMBER',NULL,FALSE,12),

('ETHERNET_PORTS','Ethernet Ports','NUMBER',NULL,FALSE,13),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,14),

('BLUETOOTH_SUPPORTED','Bluetooth Supported','BOOLEAN',NULL,FALSE,15),

('OPERATING_SYSTEM','Operating System','TEXT',NULL,FALSE,16),

('OS_VERSION','OS Version','TEXT',NULL,FALSE,17),

('TPM_VERSION','TPM Version','TEXT',NULL,FALSE,18),

('BIOS_VERSION','BIOS Version','TEXT',NULL,FALSE,19),

('MAC_ADDRESS','MAC Address','TEXT',NULL,FALSE,20),

('IP_ADDRESS','IP Address','TEXT',NULL,FALSE,21),

('HOSTNAME','Hostname','TEXT',NULL,FALSE,22),

('POWER_SUPPLY','Power Supply','NUMBER','W',FALSE,23),

('UPS_CONNECTED','Connected to UPS','BOOLEAN',NULL,FALSE,24),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,25),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,26),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,27),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,28),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,29),

('NOTES','Remarks','TEXT',NULL,FALSE,30)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- MONITOR
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMPUTING'
AND s.code='MONITOR'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('DISPLAY_SIZE','Display Size','NUMBER','inch',TRUE,4),

('DISPLAY_TYPE','Display Type','TEXT',NULL,FALSE,5),

('RESOLUTION','Resolution','TEXT',NULL,FALSE,6),

('ASPECT_RATIO','Aspect Ratio','TEXT',NULL,FALSE,7),

('REFRESH_RATE','Refresh Rate','NUMBER','Hz',FALSE,8),

('BRIGHTNESS','Brightness','NUMBER','cd/m²',FALSE,9),

('CONTRAST_RATIO','Contrast Ratio','TEXT',NULL,FALSE,10),

('RESPONSE_TIME','Response Time','NUMBER','ms',FALSE,11),

('HDMI_PORTS','HDMI Ports','NUMBER',NULL,FALSE,12),

('DISPLAYPORTS','Display Ports','NUMBER',NULL,FALSE,13),

('VGA_PORTS','VGA Ports','NUMBER',NULL,FALSE,14),

('USB_HUB','USB Hub','BOOLEAN',NULL,FALSE,15),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,16),

('VESA_MOUNT','VESA Mount','BOOLEAN',NULL,FALSE,17),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,18),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,19),

('NOTES','Remarks','TEXT',NULL,FALSE,20)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- PRINTER
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,
       s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='COMPUTING'
AND s.code='PRINTER'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),

('MODEL','Model','TEXT',NULL,TRUE,2),

('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('PRINTER_TYPE','Printer Type','TEXT',NULL,TRUE,4),

('PRINT_TECHNOLOGY','Print Technology','TEXT',NULL,FALSE,5),

('PRINT_SPEED','Print Speed','NUMBER','PPM',FALSE,6),

('PRINT_RESOLUTION','Print Resolution','TEXT',NULL,FALSE,7),

('COLOUR_PRINTING','Colour Printing','BOOLEAN',NULL,FALSE,8),

('DUPLEX_PRINTING','Duplex Printing','BOOLEAN',NULL,FALSE,9),

('PAPER_SIZE','Supported Paper Size','TEXT',NULL,FALSE,10),

('PAPER_TRAY_CAPACITY','Paper Tray Capacity','NUMBER','Sheets',FALSE,11),

('MONTHLY_DUTY_CYCLE','Monthly Duty Cycle','NUMBER','Pages',FALSE,12),

('USB_SUPPORTED','USB Interface','BOOLEAN',NULL,FALSE,13),

('ETHERNET_SUPPORTED','Ethernet Interface','BOOLEAN',NULL,FALSE,14),

('WIFI_SUPPORTED','WiFi Supported','BOOLEAN',NULL,FALSE,15),

('NETWORK_PRINTING','Network Printing','BOOLEAN',NULL,FALSE,16),

('SCANNER_AVAILABLE','Scanner Available','BOOLEAN',NULL,FALSE,17),

('COPIER_AVAILABLE','Copier Available','BOOLEAN',NULL,FALSE,18),

('FAX_AVAILABLE','Fax Available','BOOLEAN',NULL,FALSE,19),

('TONER_MODEL','Toner Model','TEXT',NULL,FALSE,20),

('POWER_CONSUMPTION','Power Consumption','NUMBER','W',FALSE,21),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,22),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,23),

('LAST_PM_DATE','Last Preventive Maintenance','DATE',NULL,FALSE,24),

('NEXT_PM_DATE','Next Preventive Maintenance','DATE',NULL,FALSE,25),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,26),

('NOTES','Remarks','TEXT',NULL,FALSE,27)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

-- ============================================================================
-- HVAC
-- ============================================================================

------------------------------------------------------------------------------
-- PRECISION AC
------------------------------------------------------------------------------

WITH ids AS (
SELECT c.id category_id,s.id subcategory_id
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
WHERE c.code='HVAC'
AND s.code='PRECISION_AC'
)
INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
category_id,
subcategory_id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM ids
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('COOLING_CAPACITY','Cooling Capacity','NUMBER','TR',TRUE,4),

('AIRFLOW','Air Flow','NUMBER','CFM',FALSE,5),

('COMPRESSOR_TYPE','Compressor Type','TEXT',NULL,FALSE,6),

('REFRIGERANT_TYPE','Refrigerant','TEXT',NULL,FALSE,7),

('REFRIGERANT_CHARGE','Refrigerant Charge','NUMBER','kg',FALSE,8),

('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,9),

('POWER_CONSUMPTION','Power Consumption','NUMBER','kW',FALSE,10),

('VOLTAGE','Operating Voltage','NUMBER','V',FALSE,11),

('FREQUENCY','Frequency','NUMBER','Hz',FALSE,12),

('PHASE','Phase','TEXT',NULL,FALSE,13),

('INDOOR_UNIT_MODEL','Indoor Unit Model','TEXT',NULL,FALSE,14),

('OUTDOOR_UNIT_MODEL','Outdoor Unit Model','TEXT',NULL,FALSE,15),

('FILTER_TYPE','Filter Type','TEXT',NULL,FALSE,16),

('HUMIDIFIER','Humidifier Available','BOOLEAN',NULL,FALSE,17),

('DEHUMIDIFIER','Dehumidifier Available','BOOLEAN',NULL,FALSE,18),

('REMOTE_MONITORING','Remote Monitoring','BOOLEAN',NULL,FALSE,19),

('CONTROLLER_MODEL','Controller Model','TEXT',NULL,FALSE,20),

('IP_RATING','IP Rating','TEXT',NULL,FALSE,21),

('OPERATING_TEMPERATURE','Operating Temperature','TEXT',NULL,FALSE,22),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,23),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,24),

('LAST_SERVICE_DATE','Last Service Date','DATE',NULL,FALSE,25),

('NEXT_SERVICE_DATE','Next Service Date','DATE',NULL,FALSE,26),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,27),

('NOTES','Remarks','TEXT',NULL,FALSE,28)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

------------------------------------------------------------------------------
-- SPLIT AC (Applicable to 1T, 1.5T, 2T & 4T)
------------------------------------------------------------------------------

DO $$
DECLARE
    ac_code TEXT;
BEGIN
    FOREACH ac_code IN ARRAY ARRAY[
        'SPLIT_AC_1T',
        'SPLIT_AC_1_5T',
        'SPLIT_AC_2T',
        'SPLIT_AC_4T'
    ]
    LOOP

        INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
c.id,
s.id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('COOLING_CAPACITY','Cooling Capacity','NUMBER','TR',TRUE,4),

('STAR_RATING','Energy Rating','NUMBER','Star',FALSE,5),

('COMPRESSOR_TYPE','Compressor Type','TEXT',NULL,FALSE,6),

('REFRIGERANT_TYPE','Refrigerant','TEXT',NULL,FALSE,7),

('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,8),

('POWER_CONSUMPTION','Power Consumption','NUMBER','kW',FALSE,9),

('VOLTAGE','Operating Voltage','NUMBER','V',FALSE,10),

('FREQUENCY','Frequency','NUMBER','Hz',FALSE,11),

('PHASE','Phase','TEXT',NULL,FALSE,12),

('INDOOR_UNIT_MODEL','Indoor Unit Model','TEXT',NULL,FALSE,13),

('OUTDOOR_UNIT_MODEL','Outdoor Unit Model','TEXT',NULL,FALSE,14),

('AIRFLOW','Air Flow','NUMBER','CFM',FALSE,15),

('FILTER_TYPE','Filter Type','TEXT',NULL,FALSE,16),

('REMOTE_CONTROLLER','Remote Controller','BOOLEAN',NULL,FALSE,17),

('INVERTER_TYPE','Inverter Technology','BOOLEAN',NULL,FALSE,18),

('NOISE_LEVEL','Noise Level','NUMBER','dB',FALSE,19),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,20),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,21),

('LAST_SERVICE_DATE','Last Service Date','DATE',NULL,FALSE,22),

('NEXT_SERVICE_DATE','Next Service Date','DATE',NULL,FALSE,23),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,24),

('NOTES','Remarks','TEXT',NULL,FALSE,25)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
WHERE c.code='HVAC'
AND s.code=ac_code
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

    END LOOP;
END $$;

------------------------------------------------------------------------------
-- CASSETTE AC (Applicable to 2T & 4T)
------------------------------------------------------------------------------

DO $$
DECLARE
    ac_code TEXT;
BEGIN
    FOREACH ac_code IN ARRAY ARRAY[
        'CASSETTE_AC_2T',
        'CASSETTE_AC_4T'
    ]
    LOOP

        INSERT INTO master.specification_definitions
(
asset_category_id,
asset_subcategory_id,
code,
name,
data_type,
unit_of_measure,
required_flag,
display_order,
is_active
)
SELECT
c.id,
s.id,
v.code,
v.name,
v.data_type,
v.unit_of_measure,
v.required_flag,
v.display_order,
TRUE
FROM master.asset_categories c
JOIN master.asset_subcategories s
ON s.asset_category_id=c.id
CROSS JOIN (
VALUES

('SERIAL_NUMBER','Serial Number','TEXT',NULL,TRUE,1),
('MODEL','Model','TEXT',NULL,TRUE,2),
('MANUFACTURER','Manufacturer','TEXT',NULL,FALSE,3),

('COOLING_CAPACITY','Cooling Capacity','NUMBER','TR',TRUE,4),

('COMPRESSOR_TYPE','Compressor Type','TEXT',NULL,FALSE,5),

('REFRIGERANT_TYPE','Refrigerant','TEXT',NULL,FALSE,6),

('POWER_SUPPLY','Power Supply','TEXT',NULL,FALSE,7),

('POWER_CONSUMPTION','Power Consumption','NUMBER','kW',FALSE,8),

('AIRFLOW','Air Flow','NUMBER','CFM',FALSE,9),

('SWING_MODE','Swing Mode','BOOLEAN',NULL,FALSE,10),

('FILTER_TYPE','Filter Type','TEXT',NULL,FALSE,11),

('NOISE_LEVEL','Noise Level','NUMBER','dB',FALSE,12),

('REMOTE_CONTROLLER','Remote Controller','BOOLEAN',NULL,FALSE,13),

('INSTALLATION_DATE','Installation Date','DATE',NULL,FALSE,14),

('COMMISSION_DATE','Commission Date','DATE',NULL,FALSE,15),

('LAST_SERVICE_DATE','Last Service Date','DATE',NULL,FALSE,16),

('NEXT_SERVICE_DATE','Next Service Date','DATE',NULL,FALSE,17),

('WARRANTY_EXPIRY','Warranty Expiry','DATE',NULL,FALSE,18),

('NOTES','Remarks','TEXT',NULL,FALSE,19)

) AS v
(
code,name,data_type,unit_of_measure,required_flag,display_order
)
WHERE c.code='HVAC'
AND s.code=ac_code
ON CONFLICT (asset_subcategory_id,code) DO NOTHING;

    END LOOP;
END $$;