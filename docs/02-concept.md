---
doc_id: FND-PRC-001
title: FieldNode design precis
project: FieldNode
doc_type: Design precis
version: "0.6"
status: Draft
date: '2026-10-01'
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
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.5"
  date: '2026-09-30'
  author: Amish Chadha
  change: "Design for construction (FND-DDR-003) applied; mass, cost, bracket, mounting and service figures updated; open for Amish's review"
- version: "0.6"
  date: '2026-10-01'
  author: Amish Chadha
  change: Budget treated as a value-engineering target
---

# FieldNode design precis

## Summary

FieldNode is a pole- or wall-mounted outdoor node built from a stock IP65 enclosure, a 6 W, 9 V class solar panel that doubles as a rain hood, a single 6 Ah LiFePO4 cell, an MPPT charge and power board, and an STM32WL-class LoRaWAN module. Two sealed M12 sensor ports carry power and data to whatever the host project measures, within a published sensor allowance of 100 mW. The TRL 3 calculations (FND-CAL-001 v0.2) confirm the worst-month energy budget: at 2 peak sun hours the cell stores 7.75 Wh a day against 2.67 Wh drawn at 100 mW, which lasts 5.75 days without sun. They also found the design's weak point: in full sun at 45 °C ambient the bare enclosure runs at 59 to 73 °C, above the 60 °C target, and the cell's 45 °C charge lockout then blocks charging for most of a hot, clear day. Amish decided on 2026-09-25 (FND-DDR-002) to fit a ventilated white sun shield, BOM line 14, at sites whose design maximum exceeds 30 °C; with it the inside stays at or below about 52 °C. The base node costs $139.00 in parts and weighs 2.45 kg; the hot-climate node costs $148.00 and weighs 2.61 kg. All design choices below are decided by Amish (FND-DDR-001 and FND-DDR-002); the changes made on 2026-09-30 so that every part can be made and fixed (FND-DDR-003, "Design for construction") are open for his review.

![FieldNode concept](../media/hero.png)

Figure 1. Node on a 48 mm pole, from the parametric model, with a 1.75 m person for scale. CONCEPT, NOT FOR FABRICATION.

## How it works

1. **Harvest.** The 6 W panel sits above the enclosure at a site-dependent tilt (40° shown), facing the equator. It sheds rain from the lid seam and shades most of the enclosure top, but not its front or sides (FND-CAL-001, section C).
2. **Charge and protect.** An MPPT-style charger on the power board holds the panel near its maximum power point and charges one LiFePO4 cell to 3.6 V. An NTC on the cell blocks charging below 0 °C and above 45 °C, since LiFePO4 cells are typically rated to charge only between 0 and 45 °C ([example cell specification](https://www.batteryspace.com/prod-specs/9055.pdf)). A protection IC and an inline fuse guard against over-discharge and short circuit.
3. **Power the sensors.** The board provides switched 3.3 V, 5 V and 12 V rails; each sensor port takes one of them, selected at build, so sensors draw nothing while the node sleeps.
4. **Measure and send.** The controller wakes on a timer, powers the sensor, reads it, stores the reading in SPI flash and sends a short LoRaWAN uplink to a TwinKit gateway, The Things Network or any LoRaWAN server. Readings are kept and resent when the link returns.
5. **Mount.** A 3 mm aluminium back plate with two V-blocks and two stainless band clamps fits 40 to 60 mm poles; the same plate screws to a wall. The enclosure hangs on the plate by four external lugs, and the panel bracket bolts to angle clips on the plate and on the panel frame.
6. **Shade, at hot sites.** Where the site's design maximum ambient exceeds 30 °C, a white aluminium shield is held to the back plate by four thumb screws and stands 15 mm off the enclosure's front, sides and top. Air enters at the open bottom and leaves through a slot at the back of the top sheet, so the box sits in moving shade.

![Exploded view](../media/exploded.png)

Figure 2. Exploded view of the base node; callout numbers match `bom/bom.csv`. Line 13 (hardware) has no callout and line 14 (the shield option) is not shown.

## Main components

Table 1. Components (numbers match the BOM and Figure 2)

| No. | Component | Choice |
| --- | --- | --- |
| 1 | Enclosure body | Light grey polycarbonate, 150 x 90 x 200 mm (W x D x H), IP65 or better, with an ePTFE membrane vent on the bottom face to stop pumping of moist air |
| 2 | Lid | Supplied with the enclosure; gasketed, captive screws |
| 3 | Cable glands | Two M16: one for the panel lead, one for a sensor with its own cable (blanked when unused) |
| 4 | Solar panel | 6 W monocrystalline, 9 V class (Vmp about 9 V at 25 °C), about 290 x 200 mm |
| 5 | Panel tilt bracket | Two rear posts and two front struts in 20 x 3 mm aluminium flat bar, bolted flat to 30 x 30 x 3 mm angle clips on the back plate and on the panel frame's back lip; tilt set by hole position |
| 6 | Cell | LiFePO4 32700, 3.2 V, 6 Ah, in a holder with inline fuse and NTC |
| 7 | Power board | MPPT charger for 1S LiFePO4, protection, fuel gauge, switched 3.3, 5 and 12 V rails |
| 8 | Controller and radio | STM32WL-class module (for example RAK3172 or Wio-E5) on a carrier with SPI flash and status LED |
| 9 | Antenna | Sub-GHz whip, about 190 mm, on a bottom bulkhead, pointing down |
| 10 | Sensor ports | Two M12 5-pin panel connectors with caps |
| 11 | Internal mounting plate | 3 mm printed ASA; carries cell and boards and lifts out as one unit |
| 12 | Pole mounting kit | Back plate 180 x 320 x 3 mm with a window behind the enclosure, two 60 x 33 x 20 mm V-blocks with a true 90° V, two stainless band clamps 250 mm apart; wall screws |
| 15 | Plug-in connectors and rail fuses | Pluggable terminal strip on the internal plate, so it lifts out as one unit; a resettable fuse on each sensor rail |
| 14 | Sun shield (hot-climate option) | White powder-coated aluminium sheet 0.5 mm, 181 x 106 x 206 mm, 15 mm off the enclosure, open bottom, 30 mm vent slot at the back of the top, lifts off after four thumb screws; fitted only where the design maximum exceeds 30 °C; not shown in the figures |

![Cutaway](../media/cutaway.png)

Figure 3. Cutaway from the front: cell (orange), power board (green) and controller (teal) on the internal plate.

The general arrangement, with the main dimensions and interfaces, is drawing FND-DWG-001 Rev P2 (`cad/drawings/FND-DWG-001.pdf`), generated from the parametric model `cad/src/model.py`. The model also exports the shield option as `cad/step/fieldnode-shield.step`.

## Numbers from the TRL 3 calculations

All values come from FND-CAL-001 v0.2, where the assumptions are stated. They are paper estimates, not measurements.

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

**Sensor allowance.** The published allowance is 100 mW (FND-DDR-002), which gives 5.75 days without sun, a 15 % margin on R6. 115.0 mW would give exactly 5 days with no margin. Every sibling load quoted so far fits 100 mW except CurbCount, at about 300 mW.

**Heat and charging.** At 45 °C ambient the enclosure reaches 58.7 °C clean and 66.2 °C dusty on a hot design day, and up to 73.3 °C with the sun in its worst position. The cell is then above its 45 °C charge limit for most of the sunny day, and the node stores only 0.8 Wh on a hot clear day. The ventilated white shield holds the inside to 48.5 to 50.4 °C on the same day (52.2 °C with the sun in its worst position) and lets the node store 10.8 to 13.1 Wh. Without the shield the box stays at 60 °C or less up to about 31.7 °C ambient, so the shield is fitted where the site's design maximum exceeds 30 °C. In the cold, sun on the box lets the cell charge on clear days warmer than about -13 °C.

**Panel voltage.** In full sun on a hot day the 9 V class panel's maximum power voltage falls to about 7.42 V, 2.42 V above the 5 V minimum input of typical charger ICs. A 6 V class panel would fall to about 4.95 V, which is why the 9 V class was chosen. The charger part, chosen at TRL 4, must confirm both its minimum and maximum input.

**Airtime.** Table 3 gives airtime for a 20-byte payload (33 bytes on air) at 125 kHz. The Things Network allows 30 s of uplink airtime per node per day ([TTN fair use](https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/)).

**Firmware airtime rule (FND-DDR-002).** On The Things Network the firmware keeps the 15 min default at SF7 to SF9 and, when adaptive data rate moves the node to SF10 or slower, lengthens the interval to 22 min at SF10, 48 min at SF11 and 87 min at SF12. Airtime then stays at 30 s a day or less at every spreading factor. On a private gateway only the regional duty cycle applies. This is a rule for the firmware; writing the firmware is TRL 4 work.

Table 3. Airtime per day at a 15 min interval (96 uplinks)

| Spreading factor | Time on air per uplink | Per day | Within 30 s? |
| --- | --- | --- | --- |
| SF7 | 71.9 ms | 6.9 s | Yes |
| SF8 | 133.6 ms | 12.8 s | Yes |
| SF9 | 246.8 ms | 23.7 s | Yes |
| SF10 | 452.6 ms | 43.5 s | No; firmware rule sets 22 min |
| SF11 | 987.1 ms | 94.8 s | No; firmware rule sets 48 min |
| SF12 | 1,810 ms | 173.8 s | No; firmware rule sets 87 min |

**Link.** At +14 dBm with 2 dBi antennas and about -129.5 dBm sensitivity at SF9, the link budget is 145.0 dB. The Hata suburban model gives 126.4 dB of path loss to a 30 m gateway 2 km away, an 18.6 dB margin, and about 3.5 km of range with a 10 dB fade margin. Range depends on gateway height and clutter and needs a field survey.

**Store and forward.** Thirty days of readings take 90 kB of the 16 MB flash. Under The Things Network's fair use a 30-day backlog at SF9 would take about 68 days to resend, so backlogs are best sent through a private gateway.

**Wind.** At 35 m/s the dynamic pressure is 750 Pa: 52.2 N on the panel and 29.3 N on the enclosure (36.3 N on the shield where fitted). Wind from behind gives 14.8 N·m about the lower clamp and pulls the upper clamp with 59 N (63 N with the shield), against about 2,000 N of assumed clamp preload. The bracket's flat bars carry at most about 39 N.

**Mass.** 2.45 kg for the base node: enclosure with lugs 0.43 kg, back plate and V-blocks 0.48 kg, bracket 0.22 kg, internal plate 0.07 kg and bought parts 1.24 kg (panel 0.55 kg). The TRL 2 estimate of 1.7 kg under-counted the back plate. The shield adds 0.16 kg (2.61 kg); R14 applies to the base node.

**Cost.** $139.00 in parts at quantity 1 for the base node (see `bom/bom.csv`), within the $150 value-engineering target ($11.00 under); $148.00 with the shield ($2.00 under). The gateway is not included.

## Key design choices

These choices are decided by Amish, 2026-09-25: go with recommendation (FND-DDR-001, D1 to D12, and FND-DDR-002).

1. **LoRaWAN rather than Wi-Fi, cellular or LoRa point-to-point.** Kilometer range at milliwatt average power, open network servers, and a match with the TwinKit gateway's LoRa concentrator. Cellular stays a later variant.
2. **STM32WL-class single-chip module.** Radio and controller in one low-sleep-current part, with LoRaWAN stacks that are open source.
3. **One LiFePO4 cell rather than Li-ion.** LiFePO4 is less prone to thermal runaway and tolerates heat better, at the cost of lower energy density. A single cell keeps the charger simple and avoids balancing. CellGuard covers 4 to 16 cell packs, so FieldNode uses a 1S protection IC on its own power board.
4. **6 W panel as standard, 9 V class**, with 3 W and 10 W variants kept as later options. The 9 V class keeps voltage headroom for the charger when hot.
5. **Panel as rain hood and partial sun shade** over the enclosure. FND-CAL-001 shows it does not shade enough for hot climates on its own, so a ventilated white shield is added at sites whose design maximum exceeds 30 °C (choice 12).
6. **Antenna pointing down** below the enclosure, out of the panel's shadow and away from hands at the lid.
7. **M12 5-pin sensor ports** rather than bare glands, so sensors can be swapped without opening the box; a gland remains for sensors with fixed cables. Pinout still open.
8. **Mounting above head height** (1.75 m to the enclosure base) to reduce tampering while staying reachable from a short ladder.
9. **Default 15 min reporting interval**, adjustable from 1 min to 24 h within airtime limits, with the firmware airtime rule above on The Things Network.
10. **TwinKit gateway as the default network**, with The Things Network as the public fallback.
11. **Stock polycarbonate IP65 enclosure** rather than a printed one.
12. **Sun shield only at hot-climate sites** (design maximum above 30 °C), so the base node stays light and cheap; R14 applies to the base node.
13. **Published sensor allowance 100 mW** rather than 115 mW, for a 15 % autonomy margin.

## Relationship to other lab projects

- **TwinKit** is the default gateway and data platform; FieldNode sends standard LoRaWAN uplinks, so any LoRaWAN server also works. TwinKit's recommended 8-channel LoRaWAN concentrator matches choice 1.
- **CalRig** is where sensors should be checked before and after deployment; SensorScope found offsets over 2 °C in pre-deployment checks ([Barrenetxea et al., 2008](https://gsfr.github.io/pdf/sensys2008.pdf)).
- **CellGuard** is not used, because it targets 4 to 16 cell packs; see choice 3.
- Adopting projects named in their READMEs include AirStreet, BridgePulse, CurbCount, FloodGauge, HeatMap Node, LoadZone, NoiseMap, SlopeWatch and WellSense. Several of them cost the FieldNode core at about $126 and plan against a 115 mW allowance; the published allowance is now 100 mW, and updating those notes is listed as a cross-repo action in `docs/REVIEW.md`.

## Safety

> **Safety:** The node contains a lithium iron phosphate cell of about 19 Wh. Fuse the cell at the holder, use a protection circuit, and never charge below 0 °C or above 45 °C. Do not install or charge a cell that is swollen, damaged or wet. Store and transport spare cells at partial charge. In hot climates the bare enclosure can exceed 60 °C in sun; fit the sun shield wherever the design maximum exceeds 30 °C, and never defeat the charge lockout to gain energy.

> **Safety:** Work at height. Mount from a stable ladder or platform with a second person present, and never on a pole carrying power lines unless the utility authorizes it. Check that the pole and wall anchors can carry the wind load, about 80 N at 2 m, before fitting the panel, and tighten both band clamps to the maker's torque.

> **Safety:** Glass-fronted panels and cut aluminium bar have sharp edges; deburr all cut parts and wear gloves. Keep the antenna and node clear of overhead conductors.

## Open questions

- [ ] Which two lab projects adopt FieldNode first, and in which region (EU868, US915, AS923 or IN865)? Awaiting Amish (FND-DDR-001, O1).
- [ ] Sensor port pinout: which pins carry which bus, and which rail each port gets. Awaiting Amish and the adopting teams (FND-DDR-001, O2).
- [ ] Firmware update method in the field: USB through a sealed port, or over the air? Awaiting Amish (FND-DDR-001, O3).
