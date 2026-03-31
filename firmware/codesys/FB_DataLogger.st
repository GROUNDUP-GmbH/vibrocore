(*
 * FB_DataLogger — Cycle Data Logging and MQTT Payload Builder
 *
 * On each completed sampling cycle, assembles a JSON payload containing:
 *   - Machine ID, cycle number, timestamp
 *   - GPS coordinates (received from SE050/ESP32-C3 via UART → Modbus)
 *   - Achieved depth, VFD frequency, motor current
 *   - sign_pending flag → ESP32-C3 picks this up and signs via SE050 (secp256k1)
 *     then publishes to RDDL/Planetmint for VM0042 data provenance
 *
 * UART connection ESP32-C3 (RDDL Trust Wallet):
 *   WAGO COM1 (750-650 or PFC onboard UART) ↔ ESP32-C3 TX/RX
 *   Protocol: simple JSON lines at 115200 baud
 *   ESP32-C3 pushes GPS fixes every 1s: {"lat":47.123,"lon":16.456,"fix":"RTK"}
 *   WAGO sends completed cycle JSON: {"machine_id":...,"sign_pending":true}
 *   ESP32-C3 signs with SE050 and forwards to RDDL
 *
 * MQTT (WAGO onboard MQTT client via e!COCKPIT or Node-RED on PFC Linux):
 *   Topic: vibrocore/{machine_id}/cycles
 *   Broker: configured in WAGO web interface (wago-mqtt-config)
 *)
FUNCTION_BLOCK FB_DataLogger
VAR_INPUT
    xCycleTrigger       : BOOL;   (* rising edge = new cycle to log *)
    rDepth_mm           : REAL;
    rFreq_Hz            : REAL;
    rCurrent_A          : REAL;
    iSafetyReason       : INT;    (* 0=normal, >0 = what caused stop *)
END_VAR

VAR_OUTPUT
    sJSON_Payload       : STRING[500];
    xNewPayload         : BOOL;   (* TRUE for one PLC cycle when payload ready *)
    iCycleCount         : INT;
END_VAR

VAR
    (* GPS data received from ESP32-C3 — updated via UART parse task *)
    rGPS_Lat            : REAL := 0.0;
    rGPS_Lon            : REAL := 0.0;
    sGPS_Fix            : STRING[10] := 'NONE';

    tTimestamp          : TON;   (* simple uptime counter in seconds *)
    iUptimeSec          : DINT  := 0;

    xTriggerEdge        : R_TRIG;
    xPayloadSent        : BOOL;
END_VAR

(* ---- Uptime counter ---- *)
tTimestamp(IN := TRUE, PT := T#1S);
IF tTimestamp.Q THEN
    tTimestamp(IN := FALSE);
    iUptimeSec := iUptimeSec + 1;
END_IF;

(* ---- Rising edge on cycle trigger ---- *)
xTriggerEdge(CLK := xCycleTrigger);
xNewPayload := FALSE;

IF xTriggerEdge.Q THEN
    iCycleCount := iCycleCount + 1;

    (*
     * Build JSON payload manually (no dynamic allocator in IEC 61131-3).
     * Payload is read by the ESP32-C3 on COM1. The ESP32-C3 appends the
     * SE050 secp256k1 signature and publishes to RDDL/Planetmint.
     *
     * Example output:
     * {"machine_id":"VIBROCORE-001","fw":"1.0.0","cycle":1,
     *  "uptime_s":3600,"depth_mm":1198.4,"freq_hz":100.0,
     *  "current_a":1.38,"stop_reason":0,
     *  "lat":47.1234567,"lon":16.4567890,"fix":"RTK",
     *  "sign_pending":true}
     *)
    sJSON_Payload := CONCAT('{"machine_id":"',
                     CONCAT(GVL_PARAMS.sMACHINE_ID,         '","'));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('fw":"',
                     CONCAT(GVL_PARAMS.sFIRMWARE_VERSION,   '",')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"cycle":',
                     CONCAT(INT_TO_STRING(iCycleCount),     ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"uptime_s":',
                     CONCAT(DINT_TO_STRING(iUptimeSec),     ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"depth_mm":',
                     CONCAT(REAL_TO_STRING(rDepth_mm),      ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"freq_hz":',
                     CONCAT(REAL_TO_STRING(rFreq_Hz),       ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"current_a":',
                     CONCAT(REAL_TO_STRING(rCurrent_A),     ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"stop_reason":',
                     CONCAT(INT_TO_STRING(iSafetyReason),   ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"lat":',
                     CONCAT(REAL_TO_STRING(rGPS_Lat),       ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"lon":',
                     CONCAT(REAL_TO_STRING(rGPS_Lon),       ',')));
    sJSON_Payload := CONCAT(sJSON_Payload,
                     CONCAT('"fix":"',
                     CONCAT(sGPS_Fix,                       '",')));
    sJSON_Payload := CONCAT(sJSON_Payload, '"sign_pending":true}');

    xNewPayload := TRUE;
END_IF;
