---
doc_id: FND-REQ-001
title: FieldNode requirements
project: FieldNode
doc_type: Requirements
version: "0.3"
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
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: TRL 3 status from FND-CAL-001; R11 and R16 restated to match FND-DDR-001 (D5 and the FieldNode core costing)
---

# FieldNode requirements

Eleven of the eighteen requirements are met on paper or by design, five are at risk, one is not met and one can only be verified by a timed installation (FND-CAL-001 v0.1, Table 4). The miss is R3: the enclosure runs hotter than 60 °C in full sun at 45 °C ambient, which also blocks cell charging in hot weather. Targets are unchanged from v0.2 except R11 and R16, which are restated to match FND-DDR-001; the design choices behind them are adopted for TRL 3 work pending Amish's review. The status column gives the standing from FND-CAL-001; "Met on paper" means shown by calculation, not by test.

Table 1. Requirements and status at TRL 3

| ID | Requirement | Target | Verification (TRL 3 or later) | Status (FND-CAL-001) |
| --- | --- | --- | --- | --- |
| R1 | Weather protection | Enclosure IP65 or better with membrane vent; all penetrations sealed glands or rated connectors | Enclosure rating; later spray test | Met by design: IP65 box, ePTFE vent, two IP68 glands, capped IP67 ports and bulkhead |
| R2 | Operating temperature | -20 to +45 °C ambient; electronics rated -20 to +70 °C inside the enclosure | Datasheets; thermal calculation | **At risk:** 73.3 °C inside in the dusty worst case; no charging on clear days colder than about -13 °C |
| R3 | Interior temperature in sun | 60 °C or less inside the enclosure at 45 °C ambient, full sun, still air | Thermal calculation | **Not met:** 58.7 °C clean and 66.2 °C dusty on the hot design day, 63.3 °C with the sun in its worst position; 48.5 °C with the proposed sun shield |
| R4 | Safe charging window | Cell charging blocked below 0 °C and above 45 °C by an NTC on the cell | Charger design review | Met by design |
| R5 | Energy neutral in the worst month | Daily harvest exceeds full-load demand at 2 peak sun hours | Energy budget | **At risk:** 7.75 Wh stored against 2.67 Wh drawn in the worst month, but only 0.8 Wh stored on a hot clear day because the cell is above 45 °C; 6 V class panel voltage marginal when hot |
| R6 | Autonomy without sun | 5 days or more at full sensor allowance, starting from 80 % charge usable | Energy budget | **At risk:** 5.75 days at 100 mW, exactly 5.00 days at 115 mW; 4.03 days at -20 °C and 4.60 days at end of life |
| R7 | Sensor power allowance | 100 mW average or more available to the sensor ports | Energy budget | Met on paper: 115.0 mW is the ceiling for 5 days; 100 mW design value |
| R8 | Radio link | LoRaWAN uplink to a gateway 2 km away in suburban terrain at SF9 or faster | Link budget; later field test | Met on paper: 18.6 dB margin at 2 km to a 30 m gateway |
| R9 | Airtime within fair use | 30 s uplink airtime per day or less at the default interval | Airtime calculation | **At risk:** 23.7 s at SF9; not met at SF10 (43.5 s) to SF12 unless firmware lengthens the interval |
| R10 | Store and forward | 30 days or more of readings kept on the node when the link is down | Memory calculation | Met on paper: 30 days in 90 kB of 16 MB |
| R11 | Standard sensor interface | Two sealed M12 5-pin ports, each carrying I2C, UART or RS-485, one analog input and one switched rail selectable at 3.3, 5 or 12 V; a gland for fixed-cable sensors | Pinout review with adopting projects | Met on paper; pinout open (FND-DDR-001, O2) |
| R12 | Mounting and install | Fits 40 to 60 mm poles and flat walls; one person installs in 15 min or less with hand tools | Design review; later timed install | Fit met by design (seats 40 to 71 mm); time estimated at 15 min, not verifiable at TRL 3 |
| R13 | Wind | Survives 35 m/s (126 km/h) gusts on the panel without loosening | Load calculation | Met on paper: clamp pull 59 N against 2,000 N; band preload assumed |
| R14 | Mass | 2.5 kg or less including panel and mounts | Massing model, then weighing | **At risk:** 2.41 kg; 2.56 kg with the proposed shield |
| R15 | Serviceable | Cell replaced in 10 min or less with a screwdriver; no soldering in the field | Design review | Met by design: about 7 min |
| R16 | Cost | FieldNode core (enclosure, power, radio, panel and mounting) $150 or less at quantity 1; sensors and gateway excluded | Priced BOM | Met on paper: $126.00 |
| R17 | Open and independent | All design files under CERN-OHL-S-2.0 and MIT; works with any LoRaWAN network server, no closed cloud | Design review | Met by design |
| R18 | Privacy pass-through | The core sends only what the sensor firmware passes to it; no images or audio leave the node | Firmware design review | Met by design; each project states its own rule |

## Requirements not met or at risk

- **R3 (interior temperature) not met.** The panel hood shades most of the top but none of the front, so low and side sun heat the box. Proposed, awaiting Amish: a ventilated white sun shield (about $8, 0.15 kg), which keeps the inside to about 50 °C.
- **R5 and R2 (hot and cold charging) at risk.** Without the shield a run of hot, clear days drains a full cell in about 8 days, because the charge lockout holds above 45 °C. In the cold the cell charges only on clear days warmer than about -13 °C. A 6 V class panel may fall below the charger's minimum input when hot; a 9 V class panel is proposed.
- **R6 (autonomy) at risk.** 115 mW is exactly the 5-day ceiling; publishing 100 mW as the allowance gives 15 % margin, but cold or an aged cell still falls short.
- **R9 (airtime) at risk.** Nodes at SF10 or slower must report every 22 min or less often.
- **R14 (mass) at risk.** 2.41 kg, 0.09 kg under the limit; the shield would exceed it.

## Assumptions

- Assumptions for every status above are stated in FND-CAL-001, Table 1. The main ones: worst month 2 peak sun hours on the tilted panel; panel, dust and angle losses 20 %; MPPT charger 85 %; cell charge 95 %; rail converters 90 %; LiFePO4 cell 3.2 V, 6 Ah (about 19 Wh), 80 % usable.
- Uplink payload 20 bytes plus 13 bytes of LoRaWAN overhead, 125 kHz bandwidth, coding rate 4/5, 8-symbol preamble.
- Core consumption from SX1262 datasheet figures ([Semtech SX1261/2 datasheet](https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf)): 4.0 mWh a day.
