# FieldNode

**Area:** Shared Components · **Status:** Concept · **Prototype budget:** about $150 USD · **Difficulty:** 3 of 5

A solar-powered, weatherproof sensor node with a common mounting, power and radio core, so any lab project that needs to measure something outdoors starts from the same tested base instead of a new enclosure and charger each time.

## Concept rationale

One field-proven power, enclosure and radio core lets many sensing ideas reach a prototype faster, and makes failures in one project fixes for all of them.

## Burning platform

Low-cost environmental and infrastructure monitoring is limited less by sensors than by power, weatherproofing and connectivity, which is where most field deployments fail.

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| _To be developed_ | |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| _To be developed_ | |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. Six existing and several proposed projects (WaterWatch, GrainGuard, FloodGauge, SlopeWatch and more) each needed the same outdoor node.

## Problem

Every outdoor sensing project rebuilds the same things: an enclosure that survives sun and rain, a small solar charger, a battery that lasts the night, and a low-power radio. Commercial nodes are closed or costly, and one-off builds fail in the field for the same few reasons.

## Concept

A solar-powered, weatherproof sensor node with a common mounting, power and radio core, so any lab project that needs to measure something outdoors starts from the same tested base instead of a new enclosure and charger each time.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- IP65 enclosure with vent and cable glands
- 6 W solar panel and bracket
- LiFePO4 cell, about 6 Ah
- MPPT charge and power board
- Low-power microcontroller with LoRa radio
- Sensor header with standard connector pinout
- Pole and wall mounting kit

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Lithium cells can overheat, vent and burn. Use protected cells or LiFePO4, fuse every pack, charge only within the cell maker's limits and never leave a first build charging unattended.

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

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Shared components set.
