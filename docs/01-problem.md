---
doc_id: FND-PRB-001
title: FieldNode problem statement
project: FieldNode
doc_type: Problem statement
version: "0.5"
status: Draft
date: '2026-10-02'
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
  change: Populate to TRL 2 (problem, users, context, constraints, prior work, open questions)
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: TRL 3 update; open questions aligned with FND-DDR-001 and the thermal findings of FND-CAL-001
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.5"
  date: '2026-10-02'
  author: Amish Chadha
  change: "Pilot band and pinout decisions of 2026-10-02 (FND-DEC-001)"
---

# FieldNode problem statement

Outdoor sensing projects rarely fail because of the sensor. They fail because the box leaks, the battery goes flat in a cloudy week, the charger cooks in the sun or refuses to charge in the cold, or the radio link drops. Every project in the Design Molecule lab that measures something outdoors has been about to solve these same problems again, on its own, with a new enclosure and a new charger.

## The problem

Monitoring networks for weather, water, air and ground movement are thin exactly where hazards are highest. The World Meteorological Organization notes that Germany has more stations meeting the Global Basic Observing Network standard than the whole of Africa ([WMO](https://wmo.int/media/news/closing-gaps-observing-network)). UNEP found that 37 % of countries do not legally require air quality monitoring ([UNEP, 2021](https://www.unep.org/news-and-stories/press-release/one-three-countries-world-lack-any-legally-mandated-standards)). Low-cost sensor nodes are one way to fill such gaps, but only if they keep working for months without a visit.

The field record shows where they stop working. The SensorScope team at EPFL reported water ingress and corrosion, battery charging failures below freezing, crystal drift in the cold, radio interference and miscalibrated sensors across their deployments ([Barrenetxea et al., SenSys 2008](https://gsfr.github.io/pdf/sensys2008.pdf)). None of these are sensor problems; all of them are platform problems. A lab that solves them once, in the open, can reuse the answer across many projects.

Open loggers exist. The EnviroDIY Mayfly is an Arduino-compatible logger released under the CERN Open Hardware License with solar charging support ([EnviroDIY](https://www.envirodiy.org/mayfly/); [GitHub](https://github.com/EnviroDIY/EnviroDIY_Mayfly_Logger)). The Things Network provides an open community LoRaWAN network ([TTN](https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/)). What is missing for this lab is a complete, documented node: enclosure, solar and battery sizing, mounting, a standard sensor port and a LoRa radio, specified together as one reference design that each sensing project plugs into.

## Users and context

| User | Need | Context |
| --- | --- | --- |
| Lab project teams (WaterWatch, FloodGauge, SlopeWatch, WellSense, AirStreet, NoiseMap, HeatMap Node, CurbCount, BridgePulse, LoadZone and others) | A tested base so they design only the sensor and its firmware | Prototypes and pilots at outdoor sites |
| Community groups, schools and NGOs | A node they can build, mount and repair with hand tools | Villages, farms, catchments, school grounds |
| Municipal and utility technicians | A node that mounts on a pole or wall in minutes and reports for a season without a visit | Streets, drains, pump houses, bridges |
| Researchers | An inspectable, calibratable platform whose power and data paths are documented | Field studies; calibration against CalRig before and after deployment |
| Network operators | Nodes that stay inside regional radio rules and fair-use limits | TwinKit gateways, The Things Network or a private LoRaWAN server |

## Operating environment

- Outdoors, pole or wall mounted at about 1.8 to 2.5 m above ground, in full sun or partial shade.
- Ambient -20 to +45 °C (-4 to +113 °F), rain, dust, insects and UV; coastal salt air at some sites.
- Worst-month solar resource as low as about 2 peak sun hours per day (monsoon or high-latitude winter). This is the design assumption in FND-CAL-001; site data are still to be checked for each pilot.
- Hot, sunny seasons matter as much as dark ones: FND-CAL-001 shows that at 45 °C ambient the cell sits above its 45 °C charge limit for most of a clear day unless the enclosure is shaded, which is why hot-climate sites get a sun shield.
- No mains power and no on-site Wi-Fi; a LoRaWAN gateway within a few kilometers, or none (store and forward).

## Constraints

- Garage-buildable prototype, $150 USD or less in parts for the FieldNode core (enclosure, power, radio, panel and mounting; sensors and gateway excluded), using off-the-shelf modules, a stock enclosure and hand tools.
- Open design: hardware under CERN-OHL-S-2.0, firmware under MIT; no dependency on a closed cloud service.
- Must comply with regional radio rules (for example the 1 % duty cycle sub-bands of EU868) and should fit The Things Network fair-use policy of 30 s uplink airtime per node per day ([TTN](https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/)).
- Lithium chemistry must be safe when unattended outdoors for months.
- Where a project states a privacy rule (counts or levels only, no images or audio leaving the device), the node must not weaken it.

## Out of scope

- The sensors themselves; each project owns its sensor and calibration.
- The gateway and data platform (see TwinKit).
- Cellular or satellite backhaul in the first version (kept as an open question).
- Mains-powered or high-power payloads such as cameras or pumps.

## Co-design and deployment partner

- [ ] Identify the first two lab projects to adopt FieldNode and their pilot sites.
- [ ] Get sign-off from HeatMap Node and the next adopting project on the proposed standard pinout (FND-DEC-001, decided 2026-10-02).
- [ ] Find a site host (school, utility or municipality) for a first season outdoors.

## Open questions

- Which lab projects adopt the node first, and in which region? The radio band is decided (Amish, 2026-10-02, FND-DEC-001): US915 is the default first variant, switching to the band of the first adopting project's site if it is outside North America.
- Is a single common node realistic for both low-power sensors (water level, tilt) and higher-power ones (particulate fans, microphones)? FND-CAL-001 finds that every sibling load quoted so far fits a 100 mW allowance except CurbCount (about 300 mW), which would need more storage and the 10 W panel variant kept as a later option (FND-DDR-001, D4).
- A cellular (LTE-M or NB-IoT) variant for sites with no gateway is kept as a later variant (FND-DDR-001, D1), decided by Amish on 2026-09-25.
- Hot-climate sun shield: decided by Amish on 2026-09-25 (FND-DDR-002). The shield is fitted only where the site's design maximum exceeds 30 °C; the threshold rests on an assumed shield factor that a test must confirm.
