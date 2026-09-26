---
doc_id: FND-DDR-001
title: FieldNode TRL 2 review decisions
project: FieldNode
doc_type: Design decision record
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the TRL 2 review recommendations adopted for TRL 3 work under Amish's 2026-09-25 instruction, and the items that remain open
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** proposed. The recommendations in items D1 to D12 are adopted for TRL 3 work pending Amish's review; items O1 to O3 remain "Proposed, awaiting Amish".

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed ten items as "Proposed, awaiting Amish", and the design precis FND-PRC-001 v0.2 listed eight key design choices, all marked proposed. On 2026-09-25 Amish asked for this batch of Design Molecule repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's items one by one. Every item that carried a recommendation is therefore adopted as recommended for TRL 3 work, open for his review. Items without a recommendation stay open. Nothing here is recorded as decided or approved by Amish.

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (session 2026-09-25, /populate) and in FND-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Items adopted for TRL 3 work.*

| # | Item | Adopted recommendation | Status |
| --- | --- | --- | --- |
| D1 | Radio | LoRaWAN now; cellular LTE-M or NB-IoT kept as a later variant; LoRa point-to-point not used | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D2 | Controller module | STM32WL-class single-chip module (for example RAK3172 or Wio-E5) | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D3 | Energy storage | One 6 Ah LiFePO4 cell with a 1S protection IC, fuse and NTC on the power board; CellGuard (4 to 16 cells) not used | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D4 | Panel size | 6 W standard; 3 W and 10 W variants kept as later options | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D5 | Sensor port standard | Two M12 5-pin ports carrying I2C, UART or RS-485, one analog input and a switched rail, plus a gland for fixed-cable sensors; pinout to be agreed with the first two adopting projects (see O2) | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D6 | Default reporting interval | 15 min, adjustable from 1 min to 24 h within airtime limits | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D7 | Default network | TwinKit gateway first, The Things Network as the public fallback, any LoRaWAN server allowed | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D8 | Enclosure | Stock light grey polycarbonate IP65 box with an ePTFE vent, rather than a printed ASA enclosure | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D9 | Panel as sun and rain hood (precis choice 4) | Panel mounted above the enclosure to shade it and shed rain from the lid seam | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D10 | Antenna pointing down (precis choice 5) | Whip on a bottom bulkhead, out of the panel's shadow and away from hands at the lid | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D11 | Mounting height (precis choice 7) | Enclosure base about 1.75 m above ground, reachable from a short ladder | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D12 | Budget, pitch and problem | No change was recommended; `budget_usd` stays at $150 and the pitch and problem lines are unchanged | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |

*Table 2. Items that remain open.*

| # | Item | Status |
| --- | --- | --- |
| O1 | First adopting projects and pilot region, which set the radio band (EU868, US915, AS923 or IN865) and the antenna. No preference stated and no recommendation made. | Proposed, awaiting Amish |
| O2 | Sensor port pinout. D5 fixes the connector and the signal set; the pin assignment is to be agreed with the first two adopting projects. FND-CAL-001 offers a candidate (pin 1 switched rail, 2 data A, 3 ground, 4 data B, 5 analog) for that discussion only. | Proposed, awaiting Amish and the adopting project teams |
| O3 | Firmware update method in the field (sealed USB port or over the air). No recommendation was made. | Proposed, awaiting Amish |

## Consequences

- `project.yaml`: only the TRL fields and the evidence list change. `budget_usd`, the pitch and the problem are unchanged.
- FND-PRB-001, FND-PRC-001 and FND-REQ-001 are revised to v0.3. The design choices in the precis are no longer described as "proposed"; they are adopted for TRL 3 work pending Amish's review.
- Requirement R11 is restated to match D5: each port carries one switched rail, selectable at 3.3, 5 or 12 V, because a 5-pin connector cannot carry three rails, a bus and an analog input at once. Requirement R16 is restated to make explicit that it costs the FieldNode core (enclosure, power, radio, panel and mounting), the figure that sibling projects cite when they cost their own parts separately. No other target changes.
- The TRL 3 calculations (FND-CAL-001) found problems that need Amish's decision: interior heat in hot, sunny weather blocks charging (R3 not met, R5 at risk), a sun shield would fix it but adds cost and mass, a 6 V class panel leaves no voltage headroom when hot, and the sensor allowance of 115 mW has no autonomy margin. These are listed in `docs/REVIEW.md` as proposed and are not decided by this record.
- The internal mounting plate is specified in printed ASA rather than aluminium, which the TRL 2 BOM already allowed, to save about 0.11 kg against R14. This is a detail choice within D8, not a new decision.
- TRL 4 is on hold by Amish's instruction. Nothing in this record authorizes building or testing.
