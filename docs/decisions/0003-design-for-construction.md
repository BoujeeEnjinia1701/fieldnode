---
doc_id: FND-DDR-003
title: FieldNode design for construction
project: FieldNode
doc_type: Design decision record
version: "0.3"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction and open for his review
- version: "0.2"
  date: '2026-09-30'
  author: Amish Chadha
  change: Accepted by Amish, including the recommendations for A1 to A4
- version: "0.3"
  date: '2026-10-01'
  author: Amish Chadha
  change: Budget treated as a value-engineering target
---

# 0003: Design for construction

- **Date:** 2026-09-30
- **Status:** accepted. Amish, 2026-09-30: "i accept your recommended changes on design that are currently being sent across for my approval". This covers every change below and the recommendations in Table 3 (A1 to A4), which are now decided as recommended.

## Context

On 2026-09-30 Amish asked for the build plan to show how each component is made and how it fits the next, with pictures, and wrote: "If you are realising that the design cannot be built as per concept, fix the design assumptions to match and be physically feasible as you draw the illustrations." The concept model of FND-DDR-002 showed what FieldNode does but had parts that could not be made or fixed as drawn. An earlier planning pass listed six of them (P1 to P6 below); checking the model with build123d found three more (P7 to P9).

The changes keep what the node does: the same enclosure, panel size, tilt, position and hood, the same cell, electronics, radio, ports, mounting height, pole range and sun shield. Nothing here changes the pitch or the safety case. Every change is in `cad/src/model.py`, which now also runs 97 constructability checks (`python cad/src/model.py --check`): parts that must touch do touch, and parts that must not touch are apart by at least the stated clearance. All 97 pass.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| P1 | V-blocks 50 x 21.85 x 30 mm with a round seat. A true 90° V at the 42 mm pole stand-off touches the 48.3 mm pole 24.9 mm from the plate, deeper than the block, so the pole would bear on the V's edges, not its faces. | V-blocks 60 wide x 33 deep x 20 tall, with a true 90° V 50.3 mm wide at the front face and its point 7.8 mm from the plate. The design pole touches both faces 24.9 mm from the plate, 8 mm inside the front face. Each block is held by two M4 countersunk screws from the front of the plate into tapped holes. | Keeps the pole where the concept put it (so the enclosure, panel and all loads are unchanged). 60 mm width leaves 4.9 mm lands beside the V; 20 mm height clears the 12 mm band and saves mass. Poles of 40 to 71 mm still seat on both faces. |
| P2 | The two M16 glands 26 mm apart with 24 mm flanges: 2 mm between them, no room for a spanner or the inside locknuts. | Penetrations in two rows on the bottom face, 27 and 55 mm from the back face. Back row: gland 1 (panel lead) at 40 mm left, gland 2 at 8 mm left, vent at 24 mm right. Front row: port A at 54 mm left, port B at 22 mm left, antenna at 30 mm right. | Every outside flange is at least 8 mm from the next and every inside nut about 6 mm, enough for a spanner or deep socket. The back row sits under the internal plate's connector strip with 4 mm to spare. |
| P3 | Vent overlapped the antenna bulkhead by about 5 mm. | Vent moved to the back row (24 mm right); antenna in the front row (30 mm right), 10.6 mm apart at the flanges. | Solved by the same two-row layout. |
| P4 | Bracket flat bars stood edge-on to the plate and the panel; their feet cut 11 mm into the plate; the panel fixing points at 80 mm each side of centre had no frame behind them. Also (found in checking) a post and a strut pinned one bolt at each end form a four-bar linkage, so the panel could swing. | Each side now has: a plate clip (30 x 30 x 3 mm angle, 77 mm long) with one leg bolted flat to the plate by two M5 screws and one leg standing forward; a post (20 x 3 mm flat bar) bolted flat to the outside of that leg by two M6 bolts, so it is rigid; a strut (20 x 3 mm flat bar) bolted flat to the inside of the leg by one M6 bolt; and two panel clips (30 x 30 x 3 mm angle, 30 mm long) bolted through the panel frame's back lip by two M4 bolts each, one at the high edge for the post (the hinge) and one at the low edge for the strut. | Every joint is face to face and bolted. The panel frame's back lip is the only part of a framed panel that can carry a bolt, so the clips go there. Two bolts at the post foot make the side frame a rigid triangle. One angle size and one bar size keep buying simple. The strut's hole spacing (129.2 mm) sets the 40° tilt, as BOM line 5 said. |
| P5 | Sun shield had no fixing, and its front covers the lid, so it had to come off to open the box. | A 12 mm flange folded inward at the back edge of each side sheet lies flat on the back plate, 3 mm beside the box; four M4 knurled thumb screws go through the flanges into tapped holes in the plate. The shield slides off forward after four screws. | No tools, nothing left loose on the node. The 15 mm air gap, open bottom and 30 mm top slot are unchanged, so the thermal result stands. The cell swap on a hot-climate node rises from about 7 to about 9 min [E2b]; R15 (10 min) is still met. |
| P6 | No fuses on the switched sensor rails, and no plug-in connectors, although the internal plate is meant to lift out as one unit. | New BOM line 15: a pluggable terminal strip (plug and socket) along the bottom edge of the internal plate for the panel lead, both ports and gland 2, and a 0.5 A resettable fuse on each port rail. The strip is in the model. | A shorted sensor cable can no longer draw from the cell through a boost converter up to the 5 A cell fuse, and the plate unplugs in one move. |
| P7 | The enclosure had no fixing to the back plate. | The enclosure maker's kit of four external mounting lugs, one at each back corner, above and below the box, each held by one M5 button-head screw from behind the plate with a nyloc nut in front. | The box back stays sealed (no screw through it) and sits flat on the plate; all four screws can be reached with the lid shut. |
| P8 | The internal plate floated against the back wall with no fixing. | It sits on the four moulded bosses found inside most stock enclosures, 6 mm off the back wall, held by four M4 screws. | Uses what the bought box already has; the 6 mm gap leaves room for wires behind the modules. |
| P9 | The band clamps were drawn as rings round the pole, with no path through the plate. | Each band passes round the back of the pole, through two 3 x 15 mm slots in the plate (51 mm each side of centre, clear of the V-blocks by 2 mm) and across the plate's front face, where the lower band runs below the box and the upper band above it. | This is how a band clamp holds a plate to a pole; the worm-drive housing sits behind the pole where a screwdriver reaches it. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Mass | Back plate gets a 100 x 150 mm window behind the enclosure (6 mm corner radius); post and strut bar is 20 x 3 mm instead of 25 x 3 mm. Base node 2.45 kg (was 2.41 kg), 0.05 kg under R14's 2.5 kg [F1]; hot-climate node 2.61 kg [F1b]. | The clips, bolts, connector strip and fuses added about 0.2 kg. The window is hidden behind the box and away from every fixing; the narrower bar still has a buckling factor of 30 [D5]. |
| Cost | BOM lines 1, 5, 13 and 14 repriced and line 15 added: base node $139.00, hot-climate node $148.00, both within the unchanged $150 value-engineering target (`budget_usd`), $11.00 and $2.00 under [F2], [F3]. | Parts added for construction. |
| Drawing | FND-DWG-001 Rev P3; making sketches FND-DWG-101 to 109 added. | Follows the model. |
| Documents | FND-CAL-001 v0.3, FND-PRC-001 v0.5, FND-REQ-001 v0.5: mass, cost, bracket, pole range and cell swap figures updated. No requirement changed status. | Follows the model. |
| Thermal and wind | Unchanged: the enclosure, panel and shield keep their size and position, and the lugs are not counted as heat capacity. Clamp pull 59 N (63 N with the shield) against 2,000 N [D3]. | |

*Table 3. Proposed, awaiting Amish.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| A1 | The shield now comes off by hand, which lowers tamper resistance at a node mounted at 1.75 m partly to deter tampering (FND-PRC-001, choice 8). | (a) knurled thumb screws, as modelled; (b) M4 pan-head screws needing a screwdriver, which R15 allows. | (a) for the prototype; decide for deployments after the first site visit. |
| A2 | Wall mounting. The plate's back now carries screw heads (2.8 mm) and the V-blocks (33 mm), so it cannot lie flat on a wall as the concept says. | (a) for a wall, unscrew the V-blocks and fit 5 mm spacers on the four wall screws; (b) a separate wall plate. | (a): no new part, and the spacers also let water drain. |
| A3 | The R14 mass margin is now 0.05 kg on catalogue masses. | (a) accept, weigh the prototype at TRL 4; (b) look for more mass now (for example a 2.5 mm back plate). | (a). |
| A4 | Whether the first prototype includes the sun shield (carried over from the earlier planning pass; the hot-climate node is now $148.00, within the value-engineering target). | (a) build it with the shield; (b) base node first. | (a), since the shield factor is the assumption most in need of a test. |

## Consequences

- `design_state: constructable` in `project.yaml`. The build plan FND-BLD-001 shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`).
- Requirement status is unchanged: none not met, 2 at risk (R2, R6), 10 met on paper, 5 met by design, 1 not verifiable at TRL 3 (FND-CAL-001 v0.3).
- The photoreal renders (`media/render-*.png`) and the appearance model `cad/src/product_model.py` still show the concept bracket, V-blocks and penetrations; they need updating on Amish's Mac, where Blender is.
- The enclosure part is chosen at TRL 4; its boss spacing and lug kit must be checked then, and the internal plate's four holes moved to suit.
