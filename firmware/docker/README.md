# Vibrocore Docker — HMI & MQTT on WAGO PFC200 XTR

This directory contains the Docker Compose stack.
The stack runs the operator HMI.
The stack also runs the local MQTT broker.
The stack runs next to the CODESYS Runtime on the WAGO PFC200 XTR.

## Architecture

```
WAGO PFC200 XTR (192.168.1.10)
├── CODESYS Runtime  (real-time, port 502 Modbus TCP Slave)
└── Docker (Firmware ≥ 23)
    ├── vibrocore-hmi    (Node-RED + Dashboard, port 1880)
    └── vibrocore-mqtt   (Mosquitto, port 1883 / 9001 WS)
```

The CODESYS Runtime shows the machine state.
The path is the Modbus TCP Slave on port 502.

- Node-RED polls this every 500 ms.
- Node-RED then draws the operator dashboard.
- Mosquitto sends the cycle records to the RDDL cloud.
- Mosquitto does this when LTE is up.

## Hardware

| Component | Spec |
|-----------|------|
| Controller | WAGO PFC200 XTR 750-8212 |
| CPU | 1 GHz ARM Cortex-A8 |
| RAM | 512 MB DDR3 |
| Flash | 4 GB eMMC |
| OS | Linux 3.18 (WAGO Firmware) |
| Docker | Built-in from Firmware 23 |

Idle use of this stack is about 45 MB of RAM.
This stack uses less than 5 % of the CPU.

## First-Time Setup

### 1. Enable Docker on PFC200

Open the WAGO WBM.
WBM is short for Web-Based Management.

```
http://192.168.1.10  → WAGO Web-Based Management (WBM)
→ Configuration → Docker → Enable
→ Reboot
```

- At the first login, change the default WBM password of WAGO.
- Do not leave the factory defaults on the field unit.

### 2. Transfer files to PFC200

```bash
# From developer workstation (via VPN/LAN):
scp -r firmware/docker admin@192.168.1.10:/home/admin/vibrocore/
```

### 3. Secrets and Mosquitto auth (required)

```bash
ssh admin@192.168.1.10
cd /home/admin/vibrocore
cp .env.example .env
# Edit .env: set NODE_RED_CREDENTIAL_SECRET and NODE_RED_PASSWORD_HASH
# (no default password is shipped in the repository)

cp mosquitto/passwd.example mosquitto/passwd   # then replace with mosquitto_passwd output
cp mosquitto/acl.example mosquitto/acl
# Create a real password file, e.g.:
#   docker run --rm -v "$PWD/mosquitto:/mosquitto/config" eclipse-mosquitto:2 \
#     mosquitto_passwd -c -b /mosquitto/config/passwd vibrocore 'CHANGE_ME'
```

### 4. Start containers

```bash
ssh admin@192.168.1.10
cd /home/admin/vibrocore
docker compose up -d
```

### 5. Verify

```bash
docker compose ps
# Expected output:
#   vibrocore-mqtt    Up   (no host ports — internal Docker network only)
#   vibrocore-hmi     Up   127.0.0.1:1880->1880/tcp
```

The default bind for Node-RED is loopback on the controller.
Use the PFC200 shell or the WireGuard tunnel or the SSH tunnel.

```
http://127.0.0.1:1880/ui      # Dashboard (login required)
http://127.0.0.1:1880         # Editor (login required)
```

You can serve the HMI on the machine LAN.
Change the compose port bind from `127.0.0.1:1880:1880` to the HMI address, for example `192.168.1.10:1880:1880`.
Do not bind `0.0.0.0:1880` on the field unit.

## CODESYS Side: Modbus TCP Slave Setup

The Node-RED flows talk with CODESYS on Modbus TCP.

- You must add the Modbus TCP Slave to the CODESYS project.

1. Open the project in CODESYS V3.5
2. Right-click the PFC200 in the Device Tree. Add the device.
3. Search for `Modbus TCP Slave` from the `WagoAppModbusSlaveTcp` library.
4. Set the port to 502. Set the unit ID to 1.
5. Map the `%MW0..%MW21` addresses to the variables in `GVL_MODBUS.st`
6. Build the project. Download it to the PFC200.

See `firmware/codesys/GVL_MODBUS.st` for the full register map.

## Register Map (summary)

| Register | Variable | Dir | Description |
|----------|----------|-----|-------------|
| 0 | `eHMI_OperatingMode` | HMI→PLC | 0=MANUAL, 1=DT325_AUTO |
| 1 | `xHMI_CycleStart` | HMI→PLC | Rising edge starts cycle |
| 2 | `xHMI_JogDown` | HMI→PLC | Manual jog down |
| 3 | `xHMI_JogUp` | HMI→PLC | Manual jog up |
| 4 | `xHMI_SonicToggle` | HMI→PLC | Sonic on/off (MANUAL) |
| 5 | `xHMI_FaultReset` | HMI→PLC | Clear all faults |
| 6–7 | `rHMI_TargetDepth_mm` | HMI→PLC | Target depth (REAL) |
| 8–9 | `rHMI_TargetFreq_Hz` | HMI→PLC | Sonic frequency (REAL) |
| 10 | `eStatus_SystemState` | PLC→HMI | System state enum |
| 11 | `eStatus_HubState` | PLC→HMI | Hub state machine |
| 12 | `eStatus_SonicState` | PLC→HMI | Sonic state machine |
| 13–14 | `rStatus_Position_mm` | PLC→HMI | Carriage position (REAL) |
| 15–16 | `rStatus_Freq_Hz` | PLC→HMI | VFD actual frequency (REAL) |
| 17–18 | `rStatus_Current_pct` | PLC→HMI | VFD current % rated (REAL) |
| 19 | `eStatus_SafetyReason` | PLC→HMI | Safety fault code |
| 20 | `xStatus_SystemOK` | PLC→HMI | 1=OK, 0=fault/estop |
| 21 | `iStatus_CycleCount` | PLC→HMI | Completed cycles today |

## MQTT Topics

| Topic | Publisher | Description |
|-------|-----------|-------------|
| `vibrocore/cycle/{id}` | ESP32-C3 / Node-RED | JSON cycle record (signed) |
| `vibrocore/alarm` | Node-RED | Safety fault event |
| `vibrocore/hmi/status` | Node-RED | HMI online/offline (retained) |

The structure of the cycle record is JSON.

```json
{
  "ts": "2026-03-26T10:15:00Z",
  "depth_mm": 1200.0,
  "freq_hz": 100.0,
  "lat": 47.8100,
  "lon": 16.2300,
  "fix": "RTK",
  "signed": true,
  "signature": "3045...",
  "pubkey": "02ab..."
}
```

## Remote Access (via Teltonika RUT241 + WireGuard)

```bash
# Connect to WireGuard VPN first (wg-quick up vibrocore-field)
# Node-RED is bound to loopback by default — use an SSH tunnel:
ssh -L 1880:127.0.0.1:1880 admin@10.0.0.10
# Then on the workstation:
#   http://127.0.0.1:1880/ui   Dashboard (login required)
#   http://127.0.0.1:1880      Editor (login required)
ssh admin@10.0.0.10            # PFC200 shell
```

See `docs/design/CONTROL_SYSTEM.md` for the WireGuard VPN.
The section name is Mobile Connectivity.

## Updating Node-RED Flows

```bash
# Option A: edit via browser (http://192.168.1.10:1880), then Deploy
# Option B: edit flows.json locally, then:
scp firmware/docker/nodered/flows.json admin@192.168.1.10:/home/admin/vibrocore/nodered/
ssh admin@192.168.1.10 "cd /home/admin/vibrocore && docker compose restart nodered"
```

## Logs

```bash
docker compose logs -f nodered      # Node-RED logs
docker compose logs -f mosquitto    # MQTT broker logs
docker compose logs --tail 50       # last 50 lines from all containers
```

## Resource Monitoring

```bash
# On PFC200:
docker stats
free -m
top
```
