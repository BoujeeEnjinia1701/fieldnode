---
doc_id: FND-DDR-001
title: FieldNode TRL 2 review decisions
project: FieldNode
doc_type: Design decision record
version: "0.3"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the TRL 2 review recommendations adopted for TRL 3 work under Amish's 2026-09-25 instruction, and the items that remain open
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.3"
  date: '2026-10-02'
  author: Amish Chadha
  change: "O1 to O3 decided by Amish as recommended (FND-DEC-001)"
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** accepted for D1 to D12. Decided by Amish, 2026-09-25: go with recommendation (see FND-DDR-002). Items O1 to O3 had no recommendation at TRL 2; recommendations were written for them later, and Amish approved them on 2026-10-02: "i approve your recommendations for all 555 open decisions." (FND-DEC-001).

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed ten items as "Proposed, awaiting Amish", and the design precis FND-PRC-001 v0.2 listed eight key design choices, all marked proposed. On 2026-09-25 Amish asked for this batch of Design Molecule repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's items one by one. Every item that carried a recommendation is therefore adopted as recommended for TRL 3 work, open for his review. Items without a recommendation stay open. Later on 2026-09-25 Amish wrote "i accept all your recommendations, go with them across all repos", so D1 to D12 are now decided (FND-DDR-002).

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (session 2026-09-25, /populate) and in FND-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Items decided.*

| # | Item | Adopted recommendation | Status |
| --- | --- | --- | --- |
| D1 | Radio | LoRaWAN now; cellular LTE-M or NB-IoT kept as a later variant; LoRa point-to-point not used | Decided by Amish, 2026-09-25: go with recommendation |
| D2 | Controller module | STM32WL-class single-chip module (for example RAK3172 or Wio-E5) | Decided by Amish, 2026-09-25: go with recommendation |
| D3 | Energy storage | One 6 Ah LiFePO4 cell with a 1S protection IC, fuse and NTC on the power board; CellGuard (4 to 16 cells) not used | Decided by Amish, 2026-09-25: go with recommendation |
| D4 | Panel size | 6 W standard; 3 W and 10 W variants kept as later options | Decided by Amish, 2026-09-25: go with recommendation |
| D5 | Sensor port standard | Two M12 5-pin ports carrying I2C, UART or RS-485, one analog input and a switched rail, plus a gland for fixed-cable sensors; pinout to be agreed with the first two adopting projects (see O2) | Decided by Amish, 2026-09-25: go with recommendation |
| D6 | Default reporting interval | 15 min, adjustable from 1 min to 24 h within airtime limits | Decided by Amish, 2026-09-25: go with recommendation |
| D7 | Default network | TwinKit gateway first, The Things Network as the public fallback, any LoRaWAN server allowed | Decided by Amish, 2026-09-25: go with recommendation |
| D8 | Enclosure | Stock light grey polycarbonate IP65 box with an ePTFE vent, rather than a printed ASA enclosure | Decided by Amish, 2026-09-25: go with recommendation |
| D9 | Panel as sun and rain hood (precis choice 4) | Panel mounted above the enclosure to shade it and shed rain from the lid seam | Decided by Amish, 2026-09-25: go with recommendation |
| D10 | Antenna pointing down (precis choice 5) | Whip on a bottom bulkhead, out of the panel's shadow and away from hands at the lid | Decided by Amish, 2026-09-25: go with recommendation |
| D11 | Mounting height (precis choice 7) | Enclosure base about 1.75 m above ground, reachable from a short ladder | Decided by Amish, 2026-09-25: go with recommendation |
| D12 | Budget, pitch and problem | No change was recommended; `budget_usd` stays at $150 and the pitch and problem lines are unchanged | Decided by Amish, 2026-09-25: go with recommendation |

*Table 2. Items left open at TRL 2, decided by Amish on 2026-10-02.*

| # | Item | Status |
| --- | --- | --- |
| O1 | First adopting projects and pilot region, which set the radio band (EU868, US915, AS923 or IN865) and the antenna. No preference stated and no recommendation made at TRL 2. | Decided by Amish, 2026-10-02, as recommended: US915 (North America) is the default first variant with a 915 MHz whip; the band switches to that of the first adopting project's site if it is outside North America (FND-DEC-001) |
| O2 | Sensor port pinout. D5 fixes the connector and the signal set; the pin assignment is to be agreed with the first two adopting projects. FND-CAL-001 offers a candidate (pin 1 switched rail, 2 data A, 3 ground, 4 data B, 5 analog) for that discussion only. | Decided by Amish, 2026-10-02, as recommended: the candidate pinout above is the proposed standard, sent to HeatMap Node and the next adopting project for sign-off (FND-DEC-001) |
| O3 | Firmware update method in the field (sealed USB port or over the air). No recommendation was made at TRL 2. | Decided by Amish, 2026-10-02, as recommended: update by cable inside the box with the lid open (a USB or serial header on the board, no extra hole in the enclosure); over the air left for a later private-gateway variant (FND-DEC-001) |

## Consequences

- `project.yaml`: only the TRL fields and the evidence list change. `budget_usd`, the pitch and the problem are unchanged.
- FND-PRB-001, FND-PRC-001 and FND-REQ-001 are revised to v0.3. The design choices in the precis are no longer described as "proposed"; since FND-DDR-002 they are decided.
- Requirement R11 is restated to match D5: each port carries one switched rail, selectable at 3.3, 5 or 12 V, because a 5-pin connector cannot carry three rails, a bus and an analog input at once. Requirement R16 is restated to make explicit that it costs the FieldNode core (enclosure, power, radio, panel and mounting), the figure that sibling projects cite when they cost their own parts separately. No other target changes.
- The TRL 3 calculations (FND-CAL-001) found problems that need Amish's decision: interior heat in hot, sunny weather blocks charging (R3 not met, R5 at risk), a sun shield would fix it but adds cost and mass, a 6 V class panel leaves no voltage headroom when hot, and the sensor allowance of 115 mW has no autonomy margin. They are decided in FND-DDR-002, not in this record.
- The internal mounting plate is specified in printed ASA rather than aluminium, which the TRL 2 BOM already allowed, to save about 0.11 kg against R14. This is a detail choice within D8, not a new decision.
- TRL 4 is on hold by Amish's instruction. Nothing in this record authorizes building or testing.
