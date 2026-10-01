---
doc_id: FND-DEC-001
title: FieldNode design decisions register
project: FieldNode
doc_type: Design decisions register
version: "0.2"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Register opened; open decisions moved out of the build plan
- version: "0.2"
  date: '2026-10-01'
  author: Amish Chadha
  change: Budget treated as a value-engineering target
---

# FieldNode design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

| # | Decision needed | Options | Recommendation | Affects in the build | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | Pilot region and radio band | Region and LoRaWAN band of the first adopting project | None yet | Antenna and radio variant | FND-DDR-001, O1 |
| 2 | Sensor port pin assignment | Pinout of the two M12 ports, agreed with the adopting projects | None yet | Port wiring (build plan section 3.4.1, wire 6) | FND-DDR-001, O2 |
| 3 | Firmware update method in the field | Over the air, cable, card swap | None yet | Not part of the TRL 3 build; needed at TRL 4 | FND-DDR-001, O3 |

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The solar panel frame has a flat back lip at least 12 mm wide | The panel clips bolt through it; without it the clip position changes | FND-DDR-003 |
| 2 | The enclosure model, its boss spacing and its lug kit | They set the internal plate holes and the lug positions | FND-DDR-003 |
| 3 | The band clamp torque that gives 1,000 N of preload | The calculation note assumes that preload | FND-CAL-001 |

## Value engineering

Value-engineering target: USD 150 (a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 139 for the base node (USD 11 under the target); USD 148 with the sun shield (USD 2 under the target). Main cost drivers and savings worth trying:

- The largest lines are the power board (USD 22, a prototype carrier price; the board design is TRL 4 work), the enclosure with vent and lug kit (USD 20), the solar panel (USD 14), the controller and LoRa module (USD 14) and the antenna (USD 10).
- Making the design constructable repriced lines 1, 5, 13 and 14 and added line 15, the plug-in connectors and rail fuses (USD 5); the base node rose from USD 126 to USD 139.
- Savings worth trying: the sun shield (USD 9) is an option for hot-climate sites only, so the base node carries none; the power board price should fall once its design is done.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D12 (LoRaWAN, STM32WL-class module, one 6 Ah LiFePO4 cell, 6 W panel, two M12 ports, 15 min interval and others) | Amish: "i accept all your recommendations, go with them across all repos." | FND-DDR-001, FND-DDR-002 |
| 2026-09-25 | Sun shield for hot-climate sites only; base node mass limit 2.5 kg; 9 V class panel; 100 mW sensor allowance; airtime rule at slow spreading factors | Amish: go with recommendation | FND-DDR-002 |
| 2026-09-30 | Design for construction: V-blocks, bottom-face layout, bracket, shield fixing, connector strip, enclosure lugs and other changes that make the node buildable | Amish: "i accept your recommended changes on design that are currently being sent across for my approval" | FND-DDR-003 |
| 2026-09-30 | Thumb screws on the shield for the prototype; 5 mm spacers for wall mounting; accept the 0.05 kg mass margin and weigh at TRL 4; fit the shield on the first prototype | Amish, same instruction | FND-DDR-003, A1 to A4 |
