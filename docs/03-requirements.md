---
doc_id: FND-REQ-001
title: FieldNode requirements
project: FieldNode
doc_type: Requirements
version: "0.2"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: First measurable requirements for TRL 2, with concept status against each
---

# FieldNode requirements

These are first-pass requirements for the concept. Targets are proposals for review, awaiting Amish, and will be checked by calculation at TRL 3. The status column gives the concept's standing from the first-order estimates in FND-PRC-001; "Met (estimate)" means met on paper only.

Table 1. Requirements and concept status

| ID | Requirement | Target | Verification (TRL 3 or later) | Concept status |
| --- | --- | --- | --- | --- |
| R1 | Weather protection | Enclosure IP65 or better with membrane vent; all penetrations sealed glands or rated connectors | Enclosure rating; later spray test | Met by design (rated stock enclosure); gland and connector sealing unverified |
| R2 | Operating temperature | -20 to +45 °C ambient; electronics rated -20 to +70 °C inside the enclosure | Datasheets; thermal estimate | At risk: interior temperature in full sun unverified (see R3) |
| R3 | Interior temperature in sun | 60 °C or less inside the enclosure at 45 °C ambient, full sun, still air | Thermal calculation | **Not shown.** Panel shading helps, but the estimate has no margin to claim |
| R4 | Safe charging window | Cell charging blocked below 0 °C and above 45 °C by an NTC on the cell | Charger design review | Met by design |
| R5 | Energy neutral in the worst month | Daily harvest exceeds full-load demand at 2 peak sun hours | Energy budget | Met (estimate): about 7.8 Wh stored against 3.1 Wh drawn |
| R6 | Autonomy without sun | 5 days or more at full sensor allowance, starting from 80 % charge usable | Energy budget | Met (estimate): about 5.0 days, no margin |
| R7 | Sensor power allowance | 100 mW average or more available to the sensor ports | Energy budget | Met (estimate): about 115 mW |
| R8 | Radio link | LoRaWAN uplink to a gateway 2 km away in suburban terrain at SF9 or faster | Link budget; later field test | Unverified (range figures are estimates) |
| R9 | Airtime within fair use | 30 s uplink airtime per day or less at the default interval | Airtime calculation | Met at SF7 to SF9 with a 20-byte payload every 15 min (about 24 s at SF9). **Not met at SF10 or slower** unless the interval is 30 min or longer |
| R10 | Store and forward | 30 days or more of readings kept on the node when the link is down | Memory calculation | Met by design (SPI flash); sizing to confirm |
| R11 | Standard sensor interface | Two sealed ports carrying I2C, UART or RS-485, one analog input and switched 3.3 V, 5 V and 12 V rails | Pinout review with adopting projects | Proposed; pinout awaiting Amish and project teams |
| R12 | Mounting and install | Fits 40 to 60 mm poles and flat walls; one person installs in 15 min or less with hand tools | Design review; later timed install | Met by design (band clamps and back plate); time unverified |
| R13 | Wind | Survives 35 m/s (126 km/h) gusts on the panel without loosening | Load calculation | Unverified: about 50 N on the panel (estimate) |
| R14 | Mass | 2.5 kg or less including panel and mounts | Massing model, then weighing | Met (estimate): about 1.7 kg |
| R15 | Serviceable | Cell replaced in 10 min or less with a screwdriver; no soldering in the field | Design review | Met by design |
| R16 | Cost | Parts $150 or less per node at quantity 1, gateway excluded | Priced BOM | Met (indicative): about $126 |
| R17 | Open and independent | All design files under CERN-OHL-S-2.0 and MIT; works with any LoRaWAN network server, no closed cloud | Design review | Met by design |
| R18 | Privacy pass-through | The core sends only what the sensor firmware passes to it; no images or audio leave the node | Firmware design review | Met by design; each project states its own rule |

## Requirements not met or at risk

- **R3 (interior temperature) not shown.** A light-colored box shaded by the panel may still exceed 60 °C in still air at 45 °C ambient. This drives cell life and the charge window.
- **R9 (airtime) not met at SF10 or slower.** At SF10 a 20-byte uplink takes about 0.45 s, so 96 uplinks a day use about 43 s. Distant nodes must report every 30 min or less often.
- **R6 (autonomy)** is met with no margin; a heavier sensor load or an older cell misses it.
- **R8 (range)** and **R13 (wind)** are unverified estimates.

## Assumptions

- Worst month 2 peak sun hours on the tilted panel; panel, dust and angle losses 20 %; MPPT charger 85 % efficient at 1S LiFePO4 voltages; cell charge efficiency 95 %; rail converters 90 %. All estimates.
- LiFePO4 cell 3.2 V, 6 Ah (about 19 Wh), 80 % usable.
- Uplink payload 20 bytes plus 13 bytes of LoRaWAN overhead, 125 kHz bandwidth, coding rate 4/5, 8-symbol preamble.
- Core consumption (controller asleep, radio bursts, power board quiescent) under 0.01 Wh/day; estimate from SX1262 datasheet figures ([Semtech SX1261/2 datasheet](https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf)).
