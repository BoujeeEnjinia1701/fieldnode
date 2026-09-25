# FieldNode

![TRL 2](https://img.shields.io/badge/TRL-2%20of%209-0F766E) ![Hardware: CERN-OHL-S-2.0](https://img.shields.io/badge/hardware-CERN--OHL--S--2.0-111827) ![Software: MIT](https://img.shields.io/badge/software-MIT-111827)

**Area:** Shared Components · **TRL:** 2 of 9 (concept formulated) · **Prototype budget:** about $150 USD · **Difficulty:** 3 of 5

A solar-powered, weatherproof sensor node with a common mounting, power and radio core, so any lab project that needs to measure something outdoors starts from the same tested base instead of a new enclosure and charger each time.

![FieldNode concept](media/hero.png)

[Interactive 3D model](media/viewer.html) · [Concept blueprint (PDF)](media/concept-blueprint.pdf) · [Review note](docs/REVIEW.md)

## Concept rationale

Outdoor sensing projects in the lab fail for the same few reasons: water gets in, the battery runs flat in a cloudy week, the charger overheats or will not charge in the cold, or the radio link drops. FieldNode solves these once. It pairs a stock IP65 enclosure with a 6 W panel that also shades the box, a single LiFePO4 cell, an MPPT charger with a cold-charge lockout, and an STM32WL-class LoRaWAN module, with two sealed sensor ports. Each project then designs only its sensor and firmware, and a fix found in one deployment reaches all of them.

Keeping it open and garage-buildable matters because the users who most need monitoring are the least able to buy closed commercial nodes or pay for their clouds. Every part is off the shelf or cut from flat bar with hand tools, the design files are under CERN-OHL-S-2.0, and the node talks to any LoRaWAN server, including the lab's TwinKit gateway and The Things Network.

## Burning platform

Monitoring is thinnest where hazards are greatest. Germany has more stations meeting the WMO Global Basic Observing Network standard than the whole of Africa ([WMO](https://wmo.int/media/news/closing-gaps-observing-network)). Only 108 countries, 55 % of the total, reported multi-hazard early warning systems in 2024, and fewer than half of the least developed countries did ([UNDRR and WMO, 2024](https://www.undrr.org/reports/global-status-MHEWS-2024)). The same report found that countries with limited early warning coverage have disaster mortality nearly six times higher than those with substantial coverage.

For air quality, 37 % of countries do not legally require monitoring at all ([UNEP, 2021](https://www.unep.org/news-and-stories/press-release/one-three-countries-world-lack-any-legally-mandated-standards)). Low-cost nodes can help close these gaps only if they survive in the field; long-running deployments report water ingress, cold-weather charging failures and radio problems as the main causes of lost data ([Barrenetxea et al., SenSys 2008](https://gsfr.github.io/pdf/sensys2008.pdf)).

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| Water utilities and water resources | River, drain and well level logging (FloodGauge, WellSense, WaterWatch) |
| Disaster risk and civil protection | Slope movement, flood and heat sensing that feeds local early warning (SlopeWatch, HeatMap Node) |
| Municipal services and smart cities | Air, noise, parking and curb sensing on street poles, counts or levels only (AirStreet, NoiseMap, CurbCount, LoadZone) |
| Civil infrastructure and mining | Bridge vibration, tailings dam and pit wall tilt monitoring (BridgePulse, SlopeWatch) |
| Agriculture | Soil moisture, microclimate and grain store conditions at farms without power |
| Research and education | A documented, repeatable field platform for university and school projects |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| Sub-Saharan Africa | Weather observation is sparse: Germany alone has more GBON-standard stations than the whole continent ([WMO](https://wmo.int/media/news/closing-gaps-observing-network)). |
| India | Only about 12 % of 4,041 census cities and towns have air quality monitoring stations ([CSE, 2023](https://www.cseindia.org/only-12-per-cent-of-india-s-census-cities-and-towns-have-air-quality-monitoring-stations-11779)). |
| Least developed countries and small island states | Fewer than half of least developed countries report multi-hazard early warning systems; about two thirds of small island developing states do ([UNDRR and WMO, 2024](https://www.undrr.org/reports/global-status-MHEWS-2024)). |
| United States | The USGS runs about 12,165 streamgages ([USGS](https://www.usgs.gov/mission-areas/water-resources/science/usgs-national-streamgaging-network)), yet small streams, farm drains and urban culverts are mostly ungauged; low-cost nodes can fill local gaps. |
| European Union and United Kingdom | Dense official networks exist, but LoRa nodes must respect 1 % duty-cycle sub-bands in EU868 ([TTN, citing ETSI EN 300 220](https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/)), so an open reference that stays within the rules is useful to community sensing groups. |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. Six existing and several proposed projects (WaterWatch, GrainGuard, FloodGauge, SlopeWatch and more) each needed the same outdoor node. The trigger in the wider world is the push to extend early warning to everyone by 2027 under the UN Early Warnings for All initiative ([WMO](https://wmo.int/activities/early-warnings-all/wmo-and-early-warnings-all-initiative)), which depends on many more observations in places that have few today.

## Problem

Every outdoor sensing project rebuilds the same things: an enclosure that survives sun and rain, a small solar charger, a battery that lasts the night, and a low-power radio. Commercial nodes are closed or costly, and one-off builds fail in the field for the same few reasons.

## Concept

A solar-powered, weatherproof sensor node with a common mounting, power and radio core, so any lab project that needs to measure something outdoors starts from the same tested base instead of a new enclosure and charger each time.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- IP65 polycarbonate enclosure with membrane vent and cable gland
- 6 W solar panel on a tilt bracket, doubling as a sun and rain hood
- LiFePO4 cell, 3.2 V 6 Ah, fused, with a cold-charge lockout
- MPPT charge and power board with switched 3.3, 5 and 12 V sensor rails
- STM32WL-class microcontroller with LoRaWAN radio and SPI flash for store and forward
- Two sealed M12 sensor ports with a standard pinout (proposed)
- Pole and wall mounting kit

First-order estimates (to be checked at TRL 3): about 5 days without sun at full sensor load, about 115 mW average for sensors, energy neutral at 2 peak sun hours, about 1.7 kg and about $126 in parts. See the [design precis](docs/02-concept.md) and [requirements](docs/03-requirements.md), including the requirements not yet met.

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Lithium cells can overheat, vent and burn. Use protected cells or LiFePO4, fuse every pack, charge only within the cell maker's limits (for LiFePO4, typically 0 to 45 °C) and never leave a first build charging unattended.
>
> Mounting is work at height: use a stable ladder with a second person present, keep clear of overhead power lines, and check the pole or wall can carry the wind load on the panel.

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Documentation

Controlled documents follow the portfolio [documentation standard](.kit/STANDARDS.md). Each carries a document ID (FND-PRC-001 for the precis), a version and a revision history. Branded PDFs are built with `python .kit/render.py` and attached to GitHub Releases when a document is tagged, for example `FND-PRC-001/v1.0`.

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Shared components set.
