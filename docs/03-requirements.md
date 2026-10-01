---
doc_id: FND-REQ-001
title: FieldNode requirements
project: FieldNode
doc_type: Requirements
version: "0.5"
status: Draft
date: '2026-09-30'
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
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: TRL 3 status from FND-CAL-001; R11 and R16 restated to match FND-DDR-001 (D5 and the FieldNode core costing)
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.5"
  date: '2026-09-30'
  author: Amish Chadha
  change: "Design for construction (FND-DDR-003) applied; mass, cost, bracket, mounting and service figures updated; open for Amish's review"
---

# FieldNode requirements

Fifteen of the eighteen requirements are met on paper or by design, two are at risk, none is missed and one can only be verified by a timed installation (FND-CAL-001 v0.3, Table 4). Amish accepted the TRL 3 recommendations on 2026-09-25 (FND-DDR-002), and three targets are restated to match: R3 now requires the sun shield where the site's design maximum ambient exceeds 30 °C, R9 applies on The Things Network with a firmware rule that lengthens the interval at slow spreading factors, and R14 applies to the base node without the hot-climate shield. R7 is unchanged at 100 mW, which is now the published allowance. R11 and R16 stay as restated in v0.3 to match FND-DDR-001. The status column gives the standing from FND-CAL-001; "Met on paper" means shown by calculation, not by test.

Table 1. Requirements and status at TRL 3

| ID | Requirement | Target | Verification (TRL 3 or later) | Status (FND-CAL-001) |
| --- | --- | --- | --- | --- |
| R1 | Weather protection | Enclosure IP65 or better with membrane vent; all penetrations sealed glands or rated connectors | Enclosure rating; later spray test | Met by design: IP65 box, ePTFE vent, two IP68 glands, capped IP67 ports and bulkhead |
| R2 | Operating temperature | -20 to +45 °C ambient; electronics rated -20 to +70 °C inside the enclosure | Datasheets; thermal calculation | **At risk (cold):** warm end covered (52.2 °C dusty worst case with the shield at 45 °C; 58.3 °C unshielded at 30 °C); no charging on clear days colder than about -13 °C |
| R3 | Interior temperature in sun | 60 °C or less inside the enclosure in full sun, still air, at the site's design maximum ambient up to 45 °C; the ventilated sun shield (BOM line 14) is fitted wherever that maximum exceeds 30 °C | Thermal calculation; later test in sun | Met on paper: with the shield at 45 °C, 48.5 °C clean, 50.4 °C dusty, 52.2 °C worst sun position; unshielded at 30 °C, 58.3 °C worst sun position; shield factor assumed |
| R4 | Safe charging window | Cell charging blocked below 0 °C and above 45 °C by an NTC on the cell | Charger design review | Met by design |
| R5 | Energy neutral in the worst month | Daily harvest exceeds full-load demand at 2 peak sun hours | Energy budget | Met on paper: 7.75 Wh stored against 2.67 Wh drawn in the worst month; 10.8 to 13.1 Wh stored on a hot clear day with the shield; 9 V class panel keeps 2.42 V above the charger minimum input when hot |
| R6 | Autonomy without sun | 5 days or more at full sensor allowance, starting from 80 % charge usable | Energy budget | **At risk (cold or aged cell):** 5.75 days at the published 100 mW, a 15 % margin; 4.03 days at -20 °C and 4.60 days at end of life |
| R7 | Sensor power allowance | 100 mW average or more available to the sensor ports; 100 mW is the published allowance | Energy budget | Met on paper: 100 mW published; 115.0 mW is the ceiling for exactly 5 days |
| R8 | Radio link | LoRaWAN uplink to a gateway 2 km away in suburban terrain at SF9 or faster | Link budget; later field test | Met on paper: 18.6 dB margin at 2 km to a 30 m gateway |
| R9 | Airtime within fair use | 30 s uplink airtime per day or less on The Things Network; firmware keeps the 15 min default at SF7 to SF9 and lengthens the interval at SF10 and slower (22 min at SF10, 48 min at SF11, 87 min at SF12) | Airtime calculation; later firmware review | Met on paper: 23.7 s at SF9; 30.0 s or less at every spreading factor under the rule |
| R10 | Store and forward | 30 days or more of readings kept on the node when the link is down | Memory calculation | Met on paper: 30 days in 90 kB of 16 MB |
| R11 | Standard sensor interface | Two sealed M12 5-pin ports, each carrying I2C, UART or RS-485, one analog input and one switched rail selectable at 3.3, 5 or 12 V; a gland for fixed-cable sensors | Pinout review with adopting projects | Met on paper; pinout open (FND-DDR-001, O2) |
| R12 | Mounting and install | Fits 40 to 60 mm poles and flat walls; one person installs in 15 min or less with hand tools | Design review; later timed install | Fit met by design (seats 40 to 71 mm); time estimated at 15 min, not verifiable at TRL 3 |
| R13 | Wind | Survives 35 m/s (126 km/h) gusts on the panel without loosening | Load calculation | Met on paper: clamp pull 59 N against 2,000 N; band preload assumed |
| R14 | Mass | 2.5 kg or less for the base node, including panel and mounts; the hot-climate sun shield is excluded | Massing model, then weighing | Met on paper: 2.45 kg, a thin 0.05 kg margin on catalogue masses after the design for construction (FND-DDR-003); 2.61 kg with the shield |
| R15 | Serviceable | Cell replaced in 10 min or less with a screwdriver; no soldering in the field | Design review | Met by design: about 7 min; about 9 min where the shield is fitted, since it lifts off after four thumb screws |
| R16 | Cost | FieldNode core (enclosure, power, radio, panel and mounting) $150 or less at quantity 1; sensors and gateway excluded | Priced BOM | Met on paper: $139.00 base node; $148.00 with the shield |
| R17 | Open and independent | All design files under CERN-OHL-S-2.0 and MIT; works with any LoRaWAN network server, no closed cloud | Design review | Met by design |
| R18 | Privacy pass-through | The core sends only what the sensor firmware passes to it; no images or audio leave the node | Firmware design review | Met by design; each project states its own rule |

## Requirements at risk

- **R2 (cold charging) at risk.** In the cold the cell charges only on clear days warmer than about -13 °C, so an overcast freeze longer than the cold autonomy will stop the node. The warm end is now covered by the shield at hot sites.
- **R6 (autonomy) at risk for a cold or aged cell.** At the published 100 mW a new cell lasts 5.75 days, but 4.03 days at -20 °C and 4.60 days at end of life.

Resolved by FND-DDR-002 on paper: R3 (shield at sites above 30 °C), R5 (shield and 9 V class panel), R9 (firmware interval rule) and R14 (base node). R3 and R5 rest on an assumed shield factor that only a test can confirm; testing is TRL 4 work and on hold.

## Assumptions

- Assumptions for every status above are stated in FND-CAL-001, Table 1. The main ones: worst month 2 peak sun hours on the tilted panel; panel, dust and angle losses 20 %; MPPT charger 85 %; cell charge 95 %; rail converters 90 %; LiFePO4 cell 3.2 V, 6 Ah (about 19 Wh), 80 % usable.
- Uplink payload 20 bytes plus 13 bytes of LoRaWAN overhead, 125 kHz bandwidth, coding rate 4/5, 8-symbol preamble.
- Core consumption from SX1262 datasheet figures ([Semtech SX1261/2 datasheet](https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf)): 4.0 mWh a day.
