---
doc_id: FND-CAL-001
title: FieldNode sizing calculations
project: FieldNode
doc_type: Calculation
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First issue for TRL 3 (core consumption, energy budget and autonomy, airtime, link budget, store and forward, enclosure temperature and charging window, panel voltage, wind and mounting, installation and service, mass, cost)
---

# FieldNode sizing calculations

On paper, FieldNode meets eleven of its eighteen requirements (six by calculation, five by design), has five at risk, misses one and leaves one that only a timed installation can settle. The miss is heat. In full sun at 45 °C ambient the enclosure reaches 58.7 °C clean and 66.2 °C dusty on a hot design day, and up to 63.3 °C and 73.3 °C with the sun in its worst position, against the 60 °C of R3. The cell is then above its 45 °C charge limit for most of the sunny day, so a run of hot, clear days stores only 0.8 Wh a day against 2.67 Wh drawn, and a full cell lasts about 8 days. A ventilated white sun shield would fix both (48.5 °C inside, 13.1 Wh stored), for about $8 and 0.15 kg; it is proposed, awaiting Amish, and is not in the baseline. The worst-month energy budget of the TRL 2 concept stands (7.75 Wh stored against 2.67 Wh drawn), but the 115 mW sensor allowance gives exactly 5.0 days of autonomy with no margin, the cell will not charge on clear days colder than about -13 °C, a 6 V class panel has no voltage headroom above a typical charger's 5 V minimum input when hot, and the node weighs 2.41 kg against 2.5 kg. Every number in this note is printed by `docs/04-calcs/sizing.py`; the tag in brackets, for example [A3], is the line of that script's output that carries it.

> **Safety:** These are first-principles estimates for a paper proof of concept. They do not show that the lithium iron phosphate cell, the charger or the pole mounting is safe. Cell temperature, charge lockout and clamp preload must be checked on hardware before any node is left unattended. See FND-PRC-001, Safety.

## Scope and method

The note checks every requirement in FND-REQ-001 v0.3 against the design in FND-PRC-001 v0.3 and the parametric model `cad/src/model.py`. The script imports the model's `PARAMS` and `derived()` and builds the model once for part volumes, so the enclosure, panel position, bracket, back plate and V-blocks used here are the ones in the STEP files and in drawing FND-DWG-001. It also reads `bom/bom.csv` and `budget_usd` in `project.yaml`. Run it from the repo root with `python docs/04-calcs/sizing.py`; it also writes `docs/04-calcs/results.csv`.

The design case is a node on a 48.3 mm pole with the enclosure base 1.75 m above ground, facing the equator, reporting a 20-byte LoRaWAN uplink every 15 min (DDR-001, D6) to a gateway 2 km away in suburban terrain.

## Assumptions

*Table 1. Main assumptions.*

| Area | Assumption | Basis |
| --- | --- | --- |
| Energy chain | 6 W panel; 2 peak sun hours on the tilted panel in the worst month; 20 % panel loss (heat, dust, angle); charger 85 %; cell charge 95 %; rail converters 90 % | As FND-PRC-001 v0.2; screening values |
| Cell | LiFePO4 3.2 V, 6 Ah; 80 % usable; 70 % of capacity at -20 °C; 80 % at end of life; charging allowed 0 to 45 °C | Typical cell data (see FND-PRC-001) |
| Core | SX1262 at +14 dBm 45 mA, receive 4.6 mA; two 0.1 s receive windows; controller awake 0.5 s at 8 mA per report; 33 µA whole-node sleep and quiescent current at 3.3 V | Semtech SX1261/2 datasheet figures; the rest assumed |
| Radio | 20-byte payload plus 13 bytes of LoRaWAN overhead; 125 kHz; coding rate 4/5; 8-symbol preamble; explicit header; CRC on | LoRaWAN defaults |
| Link | +14 dBm; 2 dBi antennas; 0.5 dB node and 2 dB gateway feeder loss; 6 dB receiver noise figure; Okumura-Hata suburban model at 868 MHz; 10 dB fade margin | Screening values; gateway sensitivity assumed equal to the node's |
| Storage | 32 bytes per stored reading; 16 MB SPI flash; 24 bytes per reading when several are batched into one uplink | Assumed record format |
| Heat | Combined convection and radiation 10 W/m²K (still air); absorptance 0.45 clean light grey, 0.70 dusty; clear-sky direct beam from the Meinel air-mass model, diffuse 10 % of direct, ground albedo 0.2; back face against the mounting plate; panel shading traced from the model geometry; a ventilated white shield passes a quarter of the solar gain | Handbook ranges; the shield factor matches WWT-CAL-001 and is not measured |
| Design days | Hot: latitude 28.6° N, late May, clear, 30 to 45 °C. Cold: latitude 50° N, late January, clear, -20 to -10 °C | Chosen to bracket R2 |
| Panel voltage | 6 V class panel, Vmp 6.0 V at 25 °C; -0.35 %/K; panel 30 K above ambient in full sun; charger minimum input about 5.0 V | Typical crystalline silicon and bq24650 or LT3652 class figures; to confirm per part |
| Wind | 35 m/s gust; air 1.225 kg/m³; drag coefficient 1.2 on the panel (normal to it) and 1.3 on the enclosure | Screening values, not a code check |
| Mounting | Band clamp preload 1,000 N; each clamp presses the V-block with twice its preload; friction 0.2; 6063-T5 class flat bar, E = 69 GPa | Preload assumed, to be measured |
| Mass | Made parts from model volumes (polycarbonate 1.2, aluminium 2.7, ASA 1.07 g/cm³); bought parts from typical catalogue masses (panel 0.55 kg, cell 0.15 kg) | Estimates |

## A. Core consumption and energy budget (R5, R6, R7)

- **Core.** Each report costs 16.0 mA·s at SF9, so 96 reports use 0.43 mAh a day and sleep adds 0.79 mAh: the core needs 4.0 mWh a day [A1]. The TRL 2 figure stands.
- **Worst month.** The panel sees 12.0 Wh, delivers 9.60 Wh, the charger passes 8.16 Wh and the cell stores 7.75 Wh a day [A2].
- **Allowance and autonomy.** The cell holds 15.36 Wh usable. A sensor allowance of 115.0 mW is the largest that gives exactly 5.0 days without sun [A3]; at that load the node draws 3.07 Wh a day and the margin on R6 is zero. At -20 °C the same cell lasts 3.50 days and at end of life 4.00 days [A4].
- **At 100 mW** (the R7 target) the node draws 2.67 Wh a day, stores 2.9 times that in the worst month, and lasts 5.75 days, or 4.03 days at -20 °C and 4.60 days at end of life. After five sunless days it refills in 2.6 worst-month days [A5]. This note uses 100 mW as the design allowance.
- **Energy neutrality.** The worst month supports sensor loads up to 291 mW before the cell runs down day by day [A6]; autonomy, not harvest, limits the allowance.
- **Sibling loads.** AirStreet (45 mW), NoiseMap (21 mW), FloodGauge (7 mW), WellSense, HeatMap Node and SlopeWatch (about 1 mW or less) all fit within 100 mW. CurbCount's 300 mW does not fit either allowance [A7].

## B. Airtime, link and store and forward (R8, R9, R10)

*Table 2. Time on air for a 20-byte uplink (33 bytes on air) at 125 kHz [B1].*

| Spreading factor | Per uplink | Per day at 15 min | Shortest interval within 30 s/day | EU868 1 % off-time |
| --- | --- | --- | --- | --- |
| SF7 | 71.9 ms | 6.9 s | 4 min | 7 s |
| SF8 | 133.6 ms | 12.8 s | 7 min | 13 s |
| SF9 | 246.8 ms | 23.7 s | 12 min | 25 s |
| SF10 | 452.6 ms | 43.5 s | 22 min | 45 s |
| SF11 | 987.1 ms | 94.8 s | 48 min | 99 s |
| SF12 | 1,810.4 ms | 173.8 s | 87 min | 181 s |

- **R9 is at risk.** The 15 min default fits The Things Network's 30 s a day at SF7 to SF9, which covers the R8 design case, but not at SF10 or slower. Firmware must lengthen the interval when adaptive data rate moves a node to SF10 or above (22 min at SF10, 87 min at SF12). On a private TwinKit gateway only the regional duty cycle applies, and the 15 min interval fits it at every spreading factor.
- **Power limit.** At +14 dBm with a 2 dBi antenna the node radiates 15.5 dBm EIRP, 13.35 dBm ERP, inside the 14 dBm ERP limit of EU868; the whip's middle sits 1.64 m above ground [B2].
- **R8 is met on paper.** At SF9 the link budget is 145.0 dB. The Hata suburban path loss at 2 km to a 30 m gateway is 126.4 dB, a margin of 18.6 dB; with a 10 dB fade margin the range is 3.5 km. A 15 m gateway, below Hata's range of validity, gives about 2.5 km. At SF7 the margin is 13.6 dB and the range with fade margin 2.5 km [B3]. Clutter, foliage and gateway height dominate these figures; only a field survey settles them.
- **R10 is met on paper.** A day of readings takes 3,072 bytes; 30 days take 90 kB of the 16 MB flash, which would hold 5,461 days [B4].
- **Forwarding the backlog.** After a 30-day outage the node holds 2,880 readings. At SF9, batching four per uplink, resending them takes 428 s of airtime: 68 days at the 6.3 s a day left under fair use, but half a day under the EU868 duty cycle alone. At SF7 it takes 5 days under fair use [B5]. The store is ample; on The Things Network the backlog is slow to drain, so old readings should be sent when a private gateway is in range or thinned.

## C. Enclosure temperature and the charging window (R2, R3, R4, R5)

- **Loss coefficient.** The enclosure's exposed faces (all but the back, which sits on the mounting plate) total 0.0930 m² and lose 0.930 W/K. About 852 J/K of enclosure, cell, boards and plate gives a 15 min time constant, so the inside follows the sun within the hour [C1].
- **What the panel hood does.** The panel's front edge overhangs the lid by 56.6 mm and sits 120.7 mm above the enclosure top [C1b]. With the sun 60° high in front it shades 86 % of the top but none of the front face [C2b]. The hood protects the lid seam from rain; it does little for heat when the sun is low or to the side.
- **Worst sun position.** At 45 °C ambient, the worst clear-sky sun position is 35° high and 30° off the front normal: 16.9 W absorbed and 63.3 °C inside when clean, 26.3 W and 73.3 °C when dusty [C2]. This is an upper bound, since the sun is not always in that position at the day's peak ambient.

*Table 3. Hot design day, 30 to 45 °C, latitude 28.6° N, clear [C3].*

| Case | Peak inside | Sun hours with charging allowed | Energy stored in the day |
| --- | --- | --- | --- |
| Clean, no shield | 58.7 °C | 2.1 of 13.3 h | 0.8 Wh |
| Dusty, no shield | 66.2 °C | 1.4 of 13.3 h | 0.3 Wh |
| Clean, with proposed shield | 48.5 °C | 7.4 of 13.3 h | 13.1 Wh |
| Dusty, with proposed shield | 50.4 °C | 6.5 of 13.3 h | 10.8 Wh |

- **R3 is not met.** The clean enclosure scrapes under 60 °C on the design day but not with dust or with the sun in its worst position.
- **Hot weather stops charging.** Because the 45 °C charge lockout (R4) acts on a cell that sits above 45 °C from mid-morning, a clean node stores 0.8 Wh on a hot clear day against 2.67 Wh drawn. A run of such days loses 1.84 Wh a day, so a full cell lasts 8.3 days (6.4 days dusty). With the proposed shield the day ends 10.4 Wh in credit (8.1 Wh dusty) [C3b]. The lockout is correct and must stay; the fix is to keep the cell cooler.
- **Cold weather.** On a clear day at 50° N with -20 to -10 °C ambient, sun on the box lifts the inside to 3.3 °C, which allows 4.2 h of charging and 8.7 Wh stored [C4]. The peak rise is 13.3 K, so on clear days whose maximum is below about -13 °C the cell never reaches 0 °C and cannot charge [C5]. Overcast cold spells longer than the cold autonomy of about 4 days (section A) will stop the node.
- **Panel voltage.** In full sun on the hot day the panel runs at about 75 °C, where a 6 V class panel's Vmp falls to 4.95 V, 0.05 V below a typical 5.0 V charger minimum input. A 9 V class panel of the same power would give 7.42 V [C6]. The part choice for the power board (TRL 4 work) must confirm the minimum input; a 9 V class panel is proposed, awaiting Amish.
- **R2 is at risk.** The electronics are rated to 70 °C and the dusty worst case is 73.3 °C; the cold end works only on clear days above about -13 °C.

## D. Wind and mounting (R12, R13)

- **Loads.** A 35 m/s gust gives a dynamic pressure of 750 Pa: 52.2 N normal to the panel, 29.3 N on the enclosure front-on and 17.6 N side-on [D1].
- **Overturning.** With wind from behind, the panel lifts and pushes forward; together with the node's weight this gives 14.8 N·m about the lower clamp and pulls the upper clamp off the pole with 59 N. Wind from the front presses the node onto the pole [D2]. Against the 2,000 N that a 1,000 N band preload holds, the factor is 33.9 [D3].
- **Slip.** Weight and wind push the node down the pole with 64 N against 800 N of friction (factor 13); side wind twists it with 1.58 N·m against 19.3 N·m (factor 12) [D4]. These factors depend on the assumed preload, which a torque check at installation must confirm.
- **Bracket.** The rear posts are 170 mm long at 89° and the front struts 171 mm at 50°. Each member carries at most about 41 N, and a 25 x 3 mm flat bar of that length buckles out of plane at 1,317 N, a factor of 32 [D5].
- **Pole range.** On a 40 mm pole the V contacts sit 14.1 mm either side of the center and on a 60 mm pole 21.2 mm, both inside the 50 mm V-block, which seats poles up to 71 mm. Each band needs about 197 to 248 mm of length around the pole and block [D6], [D6b].
- **R13 is met on paper**, subject to the preload assumption. The pole, its footing and any wall anchors are site supplied and outside this note; the node adds about 81 N of wind load about 2 m up the pole, which the site owner should check.

## E. Installation and service (R12, R15)

- **Installation.** Fitting the bracket and panel on the ground, lifting the node, tightening two clamps, aiming the panel, plugging in the sensor and confirming an uplink take an estimated 15 min with a helper [E1], exactly the R12 limit. Only a timed installation can verify it.
- **Cell swap.** Opening the lid, swapping the cell in its fused holder, renewing the desiccant and confirming an uplink take an estimated 7 min with a screwdriver and no soldering [E2]. R15 is met by design.

## F. Mass and cost (R14, R16)

- **Mass.** The enclosure body and lid weigh 0.43 kg, the printed ASA internal plate 0.08 kg, the bracket 0.14 kg and the back plate with V-blocks 0.63 kg; bought parts add 1.14 kg: 2.41 kg in all [F1]. The TRL 2 figure of about 1.7 kg left out most of the back plate. **R14 is at risk**, with 0.09 kg of margin.
- **Cost.** The BOM has 13 lines, all priced, totaling $126.00 against the $150 `budget_usd`, a margin of $24.00 (16 %) [F2]. R16 is met on paper. The proposed sun shield would bring the node to $134.00 and 2.56 kg, over R14 [F3].

## L. Results against every requirement

*Table 4. Requirement status from this note [L].*

| ID | Requirement | Value | Target | Status |
| --- | --- | --- | --- | --- |
| R3 | Interior temperature in sun | 58.7 °C clean, 66.2 °C dusty on the hot day; 63.3 °C worst sun position; 48.5 °C with the proposed shield | 60 °C or less at 45 °C ambient, full sun, still air | **Not met** |
| R2 | Operating temperature | 73.3 °C dusty worst case against the 70 °C electronics rating; no charging on clear days below about -13 °C | -20 to +45 °C ambient; electronics -20 to +70 °C inside | **At risk** |
| R5 | Energy neutral in the worst month | 7.75 Wh stored against 2.67 Wh drawn; but 0.8 Wh stored on a hot clear day without the shield; Vmp headroom -0.05 V when hot | Harvest exceeds demand at 2 peak sun hours | **At risk** |
| R6 | Autonomy without sun | 5.75 days at 100 mW; 5.00 days at 115 mW; 4.03 days at -20 °C; 4.60 days at end of life | 5 days or more | **At risk** |
| R9 | Airtime within fair use | 23.7 s a day at SF9; 43.5 s at SF10; 173.8 s at SF12 | 30 s a day or less at 15 min | **At risk** (not met at SF10 to SF12) |
| R14 | Mass | 2.41 kg; 2.56 kg with the proposed shield | 2.5 kg or less | **At risk** |
| R12 | Mounting and install | Seats 40 to 71 mm poles; installation estimated at 15 min | 40 to 60 mm poles and walls; 15 min or less | Not verifiable at TRL 3 (time); fit met by design |
| R7 | Sensor power allowance | 115.0 mW for exactly 5 days; 100 mW design value | 100 mW or more | Met on paper |
| R8 | Radio link | 18.6 dB margin at 2 km, SF9, 30 m gateway; 3.5 km with 10 dB fade margin | 2 km suburban at SF9 or faster | Met on paper |
| R10 | Store and forward | 30 days in 90 kB of 16 MB | 30 days or more | Met on paper |
| R11 | Standard sensor interface | Two M12 5-pin ports: switched rail, ground and three signal pins | Two sealed ports with a bus, analog input and one switched rail each | Met on paper (pinout open, DDR-001 O2) |
| R13 | Wind | Clamp pull 59 N against 2,000 N; slip factor 13; bracket factor 32 | 35 m/s without loosening | Met on paper (preload assumed) |
| R16 | Cost | $126.00 | $150 or less for the FieldNode core | Met on paper |
| R1 | Weather protection | IP65 box and ePTFE vent; IP67 class glands, capped ports and bulkhead | IP65; sealed penetrations | Met by design |
| R4 | Safe charging window | NTC gates the charger at 0 and 45 °C | Charging blocked outside 0 to 45 °C | Met by design |
| R15 | Serviceable | Cell swap in about 7 min | 10 min or less, no soldering | Met by design |
| R17 | Open and independent | CERN-OHL-S-2.0 and MIT; standard LoRaWAN | Open files, any network server | Met by design |
| R18 | Privacy pass-through | Core forwards only what the sensor firmware passes | No images or audio leave the node | Met by design |

Counts: 1 not met, 5 at risk, 6 met on paper, 5 met by design, 1 not verifiable at TRL 3. R2, R3 and R5 all turn on the same cause, the enclosure's heat gain, and on an assumed shield factor that only a test can settle.

## Checks against the TRL 2 figures

| TRL 2 claim (FND-PRC-001 v0.2) | This note | Action |
| --- | --- | --- |
| 7.8 Wh/day stored; 3.1 Wh/day drawn | 7.75 and 3.07 Wh/day at 115 mW | Stands |
| Sensor allowance about 115 mW | 115.0 mW gives exactly 5.0 days; 100 mW used as the design value | Precis updated; published value awaiting Amish |
| Autonomy about 5.0 days | 5.00 days at 115 mW, 5.75 days at 100 mW; 3.5 to 4.6 days cold or aged | Precis updated |
| Core about 4 mWh/day | 4.0 mWh/day | Stands |
| Airtime 24 s at SF9, 43 s at SF10 | 23.7 s and 43.5 s | Stands |
| Link budget about 145 dB | 145.0 dB; 18.6 dB margin at 2 km | Precis updated |
| Wind about 52 N, about 16 N·m | 52.2 N; 14.8 N·m about the lower clamp | Precis updated |
| Mass about 1.7 kg | 2.41 kg | Precis updated; back plate was under-counted |
| Cost about $126 | $126.00 | Stands |
| Panel hood "helps" with interior heat | Shades 86 % of the top but not the front; R3 not met; charging blocked in hot weather | Precis updated; shield proposed |
| One gland fitted, one blanked | The panel lead needs a gland; both glands are fitted | BOM line 3 updated |
