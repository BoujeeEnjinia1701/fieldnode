---
doc_id: FND-DDR-002
title: FieldNode recommendations accepted
project: FieldNode
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record Amish's acceptance of all recommendations and what changed in the repo
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: "O1 to O3 decided by Amish as recommended (FND-DEC-001)"
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted. Every item below marked "Decided" is decided by Amish, 2026-09-25: go with recommendation. Items without a recommendation (O1 to O3) were decided by Amish on 2026-10-02, as later recommended: "i approve your recommendations for all 555 open decisions." (FND-DEC-001).

## Context

After the TRL 3 session, FieldNode had twelve items adopted for TRL 3 work pending Amish's review (FND-DDR-001, D1 to D12) and five new items in `docs/REVIEW.md` (session 2026-09-25, TRL 3, items 4 to 8), each with a recommendation. On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Where a recommendation offered several options, the recommended option is the decision. Items that carried no recommendation are not decided by this record.

## Decision

*Table 1. Items decided by Amish, 2026-09-25: go with recommendation.*

| # | Item | Decision | What changed in the repo |
| --- | --- | --- | --- |
| D1 to D12 | FND-DDR-001 items: LoRaWAN radio; STM32WL-class module; one 6 Ah LiFePO4 cell with its own 1S protection; 6 W panel standard; two M12 5-pin ports plus a gland; 15 min default interval; TwinKit first with The Things Network as fallback; stock polycarbonate IP65 enclosure; panel as hood; antenna down; 1.75 m mounting height; no change to budget, pitch or problem | As recommended in FND-DDR-001 | FND-DDR-001 v0.2 status wording; FND-PRC-001 v0.4 "Key design choices" now decided. `budget_usd` stays $150; pitch and problem unchanged |
| N1 | Sun shield (REVIEW item 4) | Option (b): a ventilated white aluminium shield only at hot-climate sites; R14 applies to the base node | BOM line 14 added as an option at qty 0 ($8.00); `build_shield()` in `cad/src/model.py` and `cad/step/fieldnode-shield.step` and `.stl`; FND-CAL-001 v0.2 finds the threshold: the shield is fitted where the site's design maximum exceeds 30 °C; R3 restated; drawing note on FND-DWG-001 Rev P2 |
| N2 | R14 mass (REVIEW item 5) | Keep 2.5 kg for the base node | R14 restated to exclude the shield; base node 2.41 kg, hot-climate node 2.55 kg |
| N3 | Panel voltage class (REVIEW item 6) | 9 V class panel of the same power, subject to the charger chosen at TRL 4 | BOM line 4 respecified at the same price; FND-CAL-001 [C6] now 7.42 V when hot, 2.42 V above a 5 V charger minimum input (was 4.95 V, 0.05 V short); drawing note, precis, README |
| N4 | Published sensor allowance (REVIEW item 7) | 100 mW | R7 notes 100 mW as published; precis, README, blueprint key figures; autonomy 5.75 days, 15 % margin; sibling notes citing 115 mW listed as a cross-repo action |
| N5 | Firmware airtime rule (REVIEW item 8) | On The Things Network, lengthen the interval automatically at SF10 and slower: 22 min at SF10, 48 min at SF11, 87 min at SF12 | R9 restated to include the rule; FND-CAL-001 [B1b] shows 30.0 s a day or less at every spreading factor; precis airtime table. Writing the firmware is TRL 4 work and on hold |

*Table 2. Items left open on 2026-09-25, decided by Amish on 2026-10-02.*

| # | Item | Status |
| --- | --- | --- |
| O1 | First adopting projects and pilot region, which set the radio band and antenna. No recommendation was made on 2026-09-25. | Decided by Amish, 2026-10-02, as recommended: US915 (North America) is the default first variant with a 915 MHz whip; the band switches to that of the first adopting project's site if it is outside North America (FND-DEC-001) |
| O2 | Sensor port pinout, to be agreed with the first two adopting projects. FND-CAL-001 offers a candidate for discussion only, not a recommendation, on 2026-09-25. | Decided by Amish, 2026-10-02, as recommended: the candidate pinout above is the proposed standard, sent to HeatMap Node and the next adopting project for sign-off (FND-DEC-001) |
| O3 | Firmware update method in the field (sealed USB port or over the air). No recommendation was made on 2026-09-25. | Decided by Amish, 2026-10-02, as recommended: update by cable inside the box with the lid open (a USB or serial header on the board, no extra hole in the enclosure); over the air left for a later private-gateway variant (FND-DEC-001) |

The suggestion in `docs/REVIEW.md` of a panel-powered cell heater for long sub-zero spells was a suggestion, not a recommendation awaiting decision, and is not adopted.

## Consequences

- Requirement status (FND-CAL-001 v0.2): none not met, 2 at risk (R2 cold charging, R6 cold or aged cell), 10 met on paper, 5 met by design, 1 not verifiable at TRL 3 (R12 install time). Before: 1 not met, 5 at risk, 6 met on paper.
- Controlled documents revised: FND-PRB-001 v0.4, FND-PRC-001 v0.4, FND-REQ-001 v0.4, FND-CAL-001 v0.2, FND-DDR-001 v0.2; drawing FND-DWG-001 Rev P2.
- Cost: base node $126.00 (unchanged); hot-climate node $134.00. Both within the $150 `budget_usd`, which is unchanged.
- Mass: base node 2.41 kg; hot-climate node 2.55 kg.
- Cross-repo actions (other repos not edited): see `docs/REVIEW.md`, session "recommendations accepted".
- TRL 4 remains on hold by Amish's instruction. The charger part choice, the firmware rule's implementation and any test of the shield factor are TRL 4 work and have not been started.
