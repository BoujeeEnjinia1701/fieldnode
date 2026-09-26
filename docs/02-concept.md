---
doc_id: FND-PRC-001
title: FieldNode design precis
project: FieldNode
doc_type: Design precis
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
  change: Populate to TRL 2 (architecture, components, first-order numbers, safety, open questions)
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: TRL 3 update; design choices adopted per FND-DDR-001 pending Amish's review; numbers checked against FND-CAL-001; parametric model and drawing FND-DWG-001; second gland fitted, ASA internal plate
---

# FieldNode design precis

## Summary

FieldNode is a pole- or wall-mounted outdoor node built from a stock IP65 enclosure, a 6 W solar panel that doubles as a rain hood, a single 6 Ah LiFePO4 cell, an MPPT charge and power board, and an STM32WL-class LoRaWAN module. Two sealed M12 sensor ports carry power and data to whatever the host project measures. The TRL 3 calculations (FND-CAL-001) confirm the worst-month energy budget: at 2 peak sun hours the cell stores 7.75 Wh a day against 2.67 Wh drawn with a 100 mW sensor allowance, which lasts 5.75 days without sun. They also find the design's weak point: in full sun at 45 °C ambient the enclosure runs at 59 to 73 °C, above the 60 °C target, and the cell's 45 °C charge lockout then blocks charging for most of a hot, clear day. A ventilated white sun shield would fix this and is proposed, awaiting Amish. Parts cost $126.00 and the node weighs 2.41 kg. The design choices below are adopted for TRL 3 work under Amish's 2026-09-25 instruction, open for his review (FND-DDR-001).

![FieldNode concept](../media/hero.png)

Figure 1. Node on a 48 mm pole, from the parametric model, with a 1.75 m person for scale. CONCEPT, NOT FOR FABRICATION.

## How it works

1. **Harvest.** The 6 W panel sits above the enclosure at a site-dependent tilt (40° shown), facing the equator. It sheds rain from the lid seam and shades most of the enclosure top, but not its front or sides (FND-CAL-001, section C).
2. **Charge and protect.** An MPPT-style charger on the power board holds the panel near its maximum power point and charges one LiFePO4 cell to 3.6 V. An NTC on the cell blocks charging below 0 °C and above 45 °C, since LiFePO4 cells are typically rated to charge only between 0 and 45 °C ([example cell specification](https://www.batteryspace.com/prod-specs/9055.pdf)). A protection IC and an inline fuse guard against over-discharge and short circuit.
3. **Power the sensors.** The board provides switched 3.3 V, 5 V and 12 V rails; each sensor port takes one of them, selected at build, so sensors draw nothing while the node sleeps.
4. **Measure and send.** The controller wakes on a timer, powers the sensor, reads it, stores the reading in SPI flash and sends a short LoRaWAN uplink to a TwinKit gateway, The Things Network or any LoRaWAN server. Readings are kept and resent when the link returns.
5. **Mount.** A 3 mm aluminium back plate with two V-blocks and two stainless band clamps fits 40 to 60 mm poles; the same plate screws to a wall.

![Exploded view](../media/exploded.png)

Figure 2. Exploded view; callout numbers match `bom/bom.csv`.

## Main components

Table 1. Components (numbers match the BOM and Figure 2)

| No. | Component | Choice |
| --- | --- | --- |
| 1 | Enclosure body | Light grey polycarbonate, 150 x 90 x 200 mm (W x D x H), IP65 or better, with an ePTFE membrane vent on the bottom face to stop pumping of moist air |
| 2 | Lid | Supplied with the enclosure; gasketed, captive screws |
| 3 | Cable glands | Two M16: one for the panel lead, one for a sensor with its own cable (blanked when unused) |
| 4 | Solar panel | 6 W monocrystalline, about 290 x 200 mm; 6 V class, or 9 V class if adopted (see Open questions) |
| 5 | Panel tilt bracket | Aluminium flat bar 25 x 3 mm: two rear posts and two front struts, tilt set by hole position |
| 6 | Cell | LiFePO4 32700, 3.2 V, 6 Ah, in a holder with inline fuse and NTC |
| 7 | Power board | MPPT charger for 1S LiFePO4, protection, fuel gauge, switched 3.3, 5 and 12 V rails |
| 8 | Controller and radio | STM32WL-class module (for example RAK3172 or Wio-E5) on a carrier with SPI flash and status LED |
| 9 | Antenna | Sub-GHz whip, about 190 mm, on a bottom bulkhead, pointing down |
| 10 | Sensor ports | Two M12 5-pin panel connectors with caps |
| 11 | Internal mounting plate | 3 mm printed ASA; carries cell and boards and lifts out as one unit |
| 12 | Pole mounting kit | Back plate 180 x 320 x 3 mm, two 50 mm V-blocks, two stainless band clamps 250 mm apart; wall screws |

![Cutaway](../media/cutaway.png)

Figure 3. Cutaway from the front: cell (orange), power board (green) and controller (teal) on the internal plate.

The general arrangement, with the main dimensions and interfaces, is drawing FND-DWG-001 Rev P1 (`cad/drawings/FND-DWG-001.pdf`), generated from the parametric model `cad/src/model.py`.

## Numbers from the TRL 3 calculations

All values come from FND-CAL-001 v0.1, where the assumptions are stated. They are paper estimates, not measurements.

![Energy flow](../media/flow.png)

Figure 4. Daily energy flow in the worst month at the 100 mW design allowance (FND-CAL-001).

Table 2. Energy budget, worst month (2 peak sun hours)

| Quantity | Value | Assumption |
| --- | --- | --- |
| Panel rating times sun | 12.0 Wh/day | 6 W at 2 peak sun hours on the tilted panel |
| Panel output | 9.60 Wh/day | 20 % loss to heat, dust and angle |
| Charger output | 8.16 Wh/day | 85 % MPPT efficiency at 1S voltages |
| Stored in cell | 7.75 Wh/day | 95 % charge efficiency |
| Core consumption | 4.0 mWh/day | 96 SF9 uplinks and 33 µA sleep |
| Drawn from cell at 100 mW | 2.67 Wh/day | Rails 90 % efficient |
| Drawn from cell at 115 mW | 3.07 Wh/day | As above |
| Usable cell energy | 15.36 Wh | 3.2 V x 6 Ah x 80 % |
| Autonomy with no sun | 5.75 days at 100 mW; 5.00 days at 115 mW | 4.03 days at -20 °C and 4.60 days at end of life, at 100 mW |

**Sensor allowance.** 115.0 mW is the largest allowance that gives exactly 5 days without sun, so it has no margin; this precis uses 100 mW, the R7 target, as the design value. Publishing 100 mW rather than 115 mW for sibling projects is proposed, awaiting Amish. Every sibling load quoted so far fits 100 mW except CurbCount, at about 300 mW.

**Heat and charging.** At 45 °C ambient the enclosure reaches 58.7 °C clean and 66.2 °C dusty on a hot design day, and up to 73.3 °C with the sun in its worst position. The cell is then above its 45 °C charge limit for most of the sunny day, and the node stores only 0.8 Wh on a hot clear day. A ventilated white shield would hold the inside to about 50 °C and let the node store 13.1 Wh. In the cold, sun on the box lets the cell charge on clear days warmer than about -13 °C.

**Panel voltage.** In full sun on a hot day a 6 V class panel's maximum power voltage falls to about 4.95 V, at or below the minimum input of typical charger ICs. A 9 V class panel of the same power keeps about 7.4 V.

**Airtime.** Table 3 gives airtime for a 20-byte payload (33 bytes on air) at 125 kHz. The Things Network allows 30 s of uplink airtime per node per day ([TTN fair use](https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/)).

Table 3. Airtime per day at a 15 min interval (96 uplinks)

| Spreading factor | Time on air per uplink | Per day | Within 30 s? |
| --- | --- | --- | --- |
| SF7 | 71.9 ms | 6.9 s | Yes |
| SF8 | 133.6 ms | 12.8 s | Yes |
| SF9 | 246.8 ms | 23.7 s | Yes |
| SF10 | 452.6 ms | 43.5 s | No; use 22 min or longer |
| SF12 | 1,810 ms | 173.8 s | No; use 87 min or longer |

**Link.** At +14 dBm with 2 dBi antennas and about -129.5 dBm sensitivity at SF9, the link budget is 145.0 dB. The Hata suburban model gives 126.4 dB of path loss to a 30 m gateway 2 km away, an 18.6 dB margin, and about 3.5 km of range with a 10 dB fade margin. Range depends on gateway height and clutter and needs a field survey.

**Store and forward.** Thirty days of readings take 90 kB of the 16 MB flash. Under The Things Network's fair use a 30-day backlog at SF9 would take about 68 days to resend, so backlogs are best sent through a private gateway.

**Wind.** At 35 m/s the dynamic pressure is 750 Pa: 52.2 N on the panel and 29.3 N on the enclosure. Wind from behind gives 14.8 N·m about the lower clamp and pulls the upper clamp with 59 N, against about 2,000 N of assumed clamp preload. The bracket's flat bars carry at most about 41 N.

**Mass.** 2.41 kg: enclosure 0.43 kg, back plate and V-blocks 0.63 kg, bracket 0.14 kg, internal plate 0.08 kg and bought parts 1.14 kg (panel 0.55 kg). The TRL 2 estimate of 1.7 kg under-counted the back plate.

**Cost.** $126.00 in parts at quantity 1 (see `bom/bom.csv`), within the $150 budget. The gateway is not included.

## Key design choices

These choices are adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review (FND-DDR-001).

1. **LoRaWAN rather than Wi-Fi, cellular or LoRa point-to-point.** Kilometer range at milliwatt average power, open network servers, and a match with the TwinKit gateway's LoRa concentrator. Cellular stays a later variant.
2. **STM32WL-class single-chip module.** Radio and controller in one low-sleep-current part, with LoRaWAN stacks that are open source.
3. **One LiFePO4 cell rather than Li-ion.** LiFePO4 is less prone to thermal runaway and tolerates heat better, at the cost of lower energy density. A single cell keeps the charger simple and avoids balancing. CellGuard covers 4 to 16 cell packs, so FieldNode uses a 1S protection IC on its own power board.
4. **6 W panel as standard**, with 3 W and 10 W variants kept as later options.
5. **Panel as rain hood and partial sun shade** over the enclosure. FND-CAL-001 shows it does not shade enough for hot climates on its own.
6. **Antenna pointing down** below the enclosure, out of the panel's shadow and away from hands at the lid.
7. **M12 5-pin sensor ports** rather than bare glands, so sensors can be swapped without opening the box; a gland remains for sensors with fixed cables. Pinout still open.
8. **Mounting above head height** (1.75 m to the enclosure base) to reduce tampering while staying reachable from a short ladder.
9. **Default 15 min reporting interval**, adjustable from 1 min to 24 h within airtime limits.
10. **TwinKit gateway as the default network**, with The Things Network as the public fallback.
11. **Stock polycarbonate IP65 enclosure** rather than a printed one.

## Relationship to other lab projects

- **TwinKit** is the default gateway and data platform; FieldNode sends standard LoRaWAN uplinks, so any LoRaWAN server also works. TwinKit's recommended 8-channel LoRaWAN concentrator matches choice 1.
- **CalRig** is where sensors should be checked before and after deployment; SensorScope found offsets over 2 °C in pre-deployment checks ([Barrenetxea et al., 2008](https://gsfr.github.io/pdf/sensys2008.pdf)).
- **CellGuard** is not used, because it targets 4 to 16 cell packs; see choice 3.
- Adopting projects named in their READMEs include AirStreet, BridgePulse, CurbCount, FloodGauge, HeatMap Node, LoadZone, NoiseMap, SlopeWatch and WellSense. Several of them cost the FieldNode core at about $126 and plan against a 115 mW allowance; see `docs/REVIEW.md` for the proposed change to 100 mW.

## Safety

> **Safety:** The node contains a lithium iron phosphate cell of about 19 Wh. Fuse the cell at the holder, use a protection circuit, and never charge below 0 °C or above 45 °C. Do not install or charge a cell that is swollen, damaged or wet. Store and transport spare cells at partial charge. In hot climates the enclosure can exceed 60 °C in sun; shade it, and never defeat the charge lockout to gain energy.

> **Safety:** Work at height. Mount from a stable ladder or platform with a second person present, and never on a pole carrying power lines unless the utility authorizes it. Check that the pole and wall anchors can carry the wind load, about 80 N at 2 m, before fitting the panel, and tighten both band clamps to the maker's torque.

> **Safety:** Glass-fronted panels and cut aluminium bar have sharp edges; deburr all cut parts and wear gloves. Keep the antenna and node clear of overhead conductors.

## Open questions

- [ ] Which two lab projects adopt FieldNode first, and in which region (EU868, US915, AS923 or IN865)? Awaiting Amish (FND-DDR-001, O1).
- [ ] Sensor port pinout: which pins carry which bus, and which rail each port gets. Awaiting Amish and the adopting teams (FND-DDR-001, O2).
- [ ] Sun shield as standard, or only for hot-climate sites? Proposed, awaiting Amish (R3, R5).
- [ ] 6 V or 9 V class panel? Proposed, awaiting Amish.
- [ ] Publish 100 mW or 115 mW as the sensor allowance? Proposed, awaiting Amish.
- [ ] Firmware update method in the field: USB through a sealed port, or over the air? Awaiting Amish (FND-DDR-001, O3).
