# Review note: FieldNode

## Session 2026-09-25: /populate to a strong TRL 2

### What was done

- `docs/01-problem.md` (FND-PRB-001 v0.2): problem with cited evidence, users, operating environment, constraints, out of scope, co-design checklist, open questions.
- `docs/03-requirements.md` (FND-REQ-001 v0.2): 18 measurable requirements (R1 to R18) with targets and a concept status column, plus assumptions.
- `docs/02-concept.md` (FND-PRC-001 v0.2): how it works, 12 numbered components, energy budget, core consumption, airtime table, link budget, wind load, mass, cost, proposed design choices, links to sibling projects, safety, open questions.
- `cad/src/concept_media.py`: massing model of the node on a 48 mm pole (enclosure body and lid, internal plate with cell, power board and controller, gland, M12 ports, antenna, panel, bracket, mounting kit). Pole and a 1.75 m person are context parts in the hero, since the kit's automatic scale figure stands on the lowest part and would float at node height. The scene is shifted so the enclosure is near Z = 0, because the kit's cutaway cutter is centered on Z = 0.
- `media/`: hero, blueprint sheet (PNG, PDF, SVG), exploded view with callouts 1 to 12, cutaway, worst-month energy flow, `model.glb` and `viewer.html`. Temporary `_views` folders removed.
- `bom/bom.csv` (13 lines, indicative prices) and `bom/bom-notes.md`.
- `README.md`: hero and links line; concept rationale, burning platform, industry and region tables and trigger expanded with cited sources; key components and safety updated.
- `docs/pdf/`: branded PDFs of the three controlled documents.

### Key results (estimates, to be checked at TRL 3)

| Quantity | Estimate | Requirement |
| --- | --- | --- |
| Stored energy, worst month (6 W, 2 sun h) | about 7.8 Wh/day | R5 met |
| Full-load draw from cell | about 3.1 Wh/day | |
| Sensor allowance | about 115 mW average (2.75 Wh/day) | R7 met |
| Autonomy with no sun | about 5.0 days | R6 met, no margin |
| Core consumption | about 4 mWh/day | |
| Airtime, 20-byte uplink every 15 min | about 24 s/day at SF9, 43 s/day at SF10 | **R9 not met at SF10 or slower** |
| Link budget at SF9 | about 145 dB | R8 unverified |
| Wind load on panel at 35 m/s | about 52 N, about 16 N·m | R13 unverified |
| Mass | about 1.7 kg | R14 met |
| Parts cost | about $126 | R16 met (budget $150) |

Requirements not met or at risk:

- **R3 (interior 60 °C or less at 45 °C ambient, full sun) not shown.** The panel hood helps, but there is no estimate with margin.
- **R9 (30 s/day airtime) not met at SF10 or slower** at the 15 min default; distant nodes need 30 min or longer intervals.
- **R6 (5 days autonomy)** has no margin.
- **R2, R8 and R13** depend on unverified estimates.

### Proposed, awaiting Amish (status updated 2026-09-25, FND-DDR-002)

1. **Radio.** Options: LoRaWAN (recommended), LoRa point-to-point, or cellular LTE-M/NB-IoT. Recommendation: LoRaWAN now; cellular as a later variant. **Decided by Amish, 2026-09-25: go with recommendation.**
2. **Controller module.** Options: STM32WL-class module such as RAK3172 or Wio-E5 (recommended), ESP32 plus SX1262, or nRF52840 plus SX1262. **Decided by Amish, 2026-09-25: go with recommendation.**
3. **Energy storage.** Options: one 6 Ah LiFePO4 cell with a 1S protection IC on the power board (recommended), 2 to 3 Li-ion 18650 cells, or a small CellGuard pack. CellGuard covers 4 to 16 cells, so it does not fit a 1S node; a note to the CellGuard project may be worth adding. **Decided by Amish, 2026-09-25: go with recommendation.**
4. **Panel size.** 6 W standard (recommended), with 3 W and 10 W variants for low- and high-power payloads as a later option. **Decided by Amish, 2026-09-25: go with recommendation.**
5. **Sensor port standard.** Two M12 5-pin ports carrying I2C, UART or RS-485, one analog input and switched rails (recommended), versus glands only. Pinout to be agreed with the first two adopting projects. **Decided by Amish, 2026-09-25: go with recommendation.**
6. **Default reporting interval** of 15 min. **Decided by Amish, 2026-09-25: go with recommendation.**
7. **Default network.** TwinKit gateway first, with The Things Network as the public fallback (recommended). **Decided by Amish, 2026-09-25: go with recommendation.**
8. **First adopting projects and region** (which set the radio band). No recommendation; still Proposed, awaiting Amish.
9. **Enclosure.** Stock polycarbonate IP65 box (recommended) versus a printed ASA enclosure. **Decided by Amish, 2026-09-25: go with recommendation.**
10. No change is proposed to `budget_usd`, the pitch or the problem in `project.yaml`. **Decided by Amish, 2026-09-25: go with recommendation.**

### Safety concerns

- About 19 Wh LiFePO4 cell left unattended outdoors: fuse, protection IC and NTC-gated charging between 0 and 45 °C; interior heat (R3) directly affects cell life and safety.
- Work at height during installation, and proximity to overhead power lines on street poles.
- Wind load on the panel; a loosened clamp could drop the node.
- Sharp edges on cut aluminium and glass-fronted panels.

### Problems and notes

- The cutaway is a front section. The sensor ports and gland fall in the removed half, so they appear only in the exploded view.
- The kit's `render_all` places the automatic scale figure at the lowest part's Z, and its cutaway cutter is centered at Z = 0. Both were worked around in `concept_media.py`; a kit fix may help other pole-mounted repos.
- The legacy `cad/src/model.py` placeholder is untouched (TRL 3 work).
- Sibling READMEs (AirStreet, BridgePulse, CurbCount, FloodGauge, HeatMap Node, LoadZone, NoiseMap, SlopeWatch, TwinKit, WellSense) all describe FieldNode as a power and radio core with LoRa; this concept matches them.

### Recommended next step

Review this note and the media, then decide items 1 to 5 and 8. If approved, run `/advance-trl3` to check the energy budget, interior temperature, link budget and wind load by calculation and to produce the parametric model and drawing sheet.

## Session 2026-09-25: TRL 3

On 2026-09-25 Amish asked for this batch of repos to go through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's TRL 2 items one by one, so every item that carried a recommendation is adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review. This session ran `/advance-trl3` on that basis and stopped at TRL 3.

### What was done

- `docs/decisions/0001-trl2-review-decisions.md` (FND-DDR-001 v0.1, status proposed): twelve items adopted as recommended for TRL 3, open for Amish's review (D1 to D12), and three left open (O1 to O3).
- `docs/04-calcs/01-sizing.md` (FND-CAL-001 v0.1) and `docs/04-calcs/sizing.py`: core consumption, energy budget and autonomy, airtime, link budget, store and forward, enclosure temperature and charging window on hot and cold design days, panel voltage, wind and mounting, installation and service times, mass and cost, with a status for every requirement. The script imports the model, reads the BOM and `project.yaml`, prints every number the note quotes and writes `docs/04-calcs/results.csv`.
- `cad/src/model.py`: parametric build123d model (enclosure, lid, two glands, two M12 ports, antenna, internal plate, cell, power board, controller, panel, flat-bar bracket, back plate, V-blocks and band clamps on a 48.3 mm pole). Exports `cad/step/` and `cad/stl/` for `fieldnode-assembly`, `fieldnode-core` and `fieldnode-mount`.
- `cad/src/sheets.py` and `cad/drawings/FND-DWG-001.svg`, `.pdf`, `.png`: general arrangement at Rev P1, 1:10, marked "CONCEPT, NOT FOR FABRICATION" and "PRELIMINARY, NOT FOR FABRICATION". FND-DWG-001 was free because the concept blueprint is FND-DWG-010.
- `bom/bom.csv` (13 lines, all priced with a supplier or supplier type, $126.00 against the $150 budget) and `bom/bom-notes.md`. Two changes, total unchanged: both glands are now fitted, because the panel lead needs one; the internal plate is printed ASA.
- `cad/src/concept_media.py` now builds from the model; all of `media/` was re-rendered and every image checked; temporary `_views` folders deleted.
- FND-PRB-001, FND-PRC-001 and FND-REQ-001 revised to v0.3; `README.md` (TRL line, links, key figures) and `project.yaml` (`trl: 3`, `trl_target: 3`, evidence list) updated. PDFs rebuilt in `docs/pdf/`.

### Requirement status (FND-CAL-001, Table 4)

1 not met, 5 at risk, 6 met on paper, 5 met by design, 1 not verifiable at TRL 3.

| ID | Status | Key number |
| --- | --- | --- |
| R3 Interior temperature | **Not met** | 58.7 °C clean, 66.2 °C dusty on a 45 °C design day; 63.3 to 73.3 °C with the sun in its worst position (target 60 °C); 48.5 °C with a shield |
| R2 Operating temperature | At risk | Dusty worst case 73.3 °C against the 70 °C electronics rating; no charging on clear days below about -13 °C |
| R5 Energy neutral | At risk | Worst month 7.75 Wh stored against 2.67 Wh drawn, but a hot clear day stores 0.8 Wh because the cell is above 45 °C; 6 V class panel Vmp 4.95 V when hot |
| R6 Autonomy | At risk | 5.75 days at 100 mW; exactly 5.00 days at 115 mW; 4.03 days at -20 °C; 4.60 days at end of life |
| R9 Airtime | At risk | 23.7 s/day at SF9; not met at SF10 (43.5 s) to SF12 at 15 min |
| R14 Mass | At risk | 2.41 kg against 2.5 kg (TRL 2 said 1.7 kg); 2.56 kg with a shield |
| R12 Install | Not verifiable at TRL 3 | Fit met by design (40 to 71 mm poles); 15 min estimate, at the limit |
| R7, R8, R10, R11, R13, R16 | Met on paper | 115.0 mW ceiling; 18.6 dB link margin at 2 km; 30 days in 90 kB; pin count; clamp pull 59 N against 2,000 N; $126.00 |
| R1, R4, R15, R17, R18 | Met by design | |

Key numbers: core 4.0 mWh/day; 145.0 dB link budget at SF9; 52.2 N on the panel at 35 m/s; bracket buckling factor 32.

### Decisions recorded (FND-DDR-001)

Decided by Amish, 2026-09-25: go with recommendation (FND-DDR-002; recorded at the time of this session as adopted for TRL 3, open for his review): D1 LoRaWAN, cellular later; D2 STM32WL-class module; D3 one 6 Ah LiFePO4 cell with its own 1S protection, CellGuard not used; D4 6 W panel standard; D5 two M12 5-pin ports plus a gland; D6 15 min default interval; D7 TwinKit first, The Things Network as fallback; D8 stock polycarbonate IP65 enclosure; D9 to D11 panel as hood, antenna down, 1.75 m mounting height (precis choices); D12 no change to budget, pitch or problem. As consequences, R11 is restated to one switched rail per port (a 5-pin connector cannot carry three rails, a bus and an analog input) and R16 is restated as the FieldNode core cost, the figure sibling repos cite.

### Still awaiting Amish (status updated 2026-09-25, FND-DDR-002)

1. **O1, first adopting projects and pilot region** (sets the band and antenna). No preference stated.
2. **O2, sensor port pinout**, with the adopting teams. FND-CAL-001 offers a candidate only.
3. **O3, firmware update method in the field.** No recommendation was made.
4. **New, sun shield (R3, R5, R2).** Options: (a) a ventilated white aluminium shield as standard (+$8, +0.15 kg; $134.00 and 2.56 kg, which breaks R14); (b) shield only for hot-climate sites, with R14 applying to the base node; (c) no shield and accept that R3 is not met and hot sites lose charge. Recommendation: (b). **Decided by Amish, 2026-09-25: go with recommendation.** Applied (see below).
5. **New, R14 mass.** If (a) is chosen, relax R14 to 2.75 kg or thin the back plate. Recommendation: keep 2.5 kg for the base node. **Decided by Amish, 2026-09-25: go with recommendation.** Applied.
6. **New, panel voltage class.** Options: 6 V class (current) or 9 V class of the same power, which keeps about 7.4 V when hot. Recommendation: 9 V class, subject to the charger chosen at TRL 4. **Decided by Amish, 2026-09-25: go with recommendation.** Applied.
7. **New, published sensor allowance.** Options: 115 mW (exactly 5 days, no margin) or 100 mW (5.75 days). Recommendation: 100 mW. Sibling notes cite 115 mW; all their quoted loads except CurbCount (about 300 mW) fit 100 mW. Not applied to any other repo. **Decided by Amish, 2026-09-25: go with recommendation.** Applied here; siblings listed as a cross-repo action.
8. **New, firmware airtime rule (R9).** Recommendation: lengthen the interval automatically at SF10 and slower (22 min at SF10, 87 min at SF12) when on The Things Network. **Decided by Amish, 2026-09-25: go with recommendation.** Applied as a requirement; firmware is TRL 4.

Suggestion only, not in the repo: a panel-powered cell heater for sites with long sub-zero spells.

### Cross-repo consistency

- TwinKit recommends an 8-channel LoRaWAN concentrator and FieldNode as its first example twin; consistent with D1 and D7. Its twin example refers to the cell as FieldNode BOM part 4; in this repo the cell is line 6 (the panel is 4). Noted here, TwinKit not edited.
- CellGuard's note that FieldNode needs its own one-cell protector agrees with D3.
- The FieldNode core cost stays $126.00, the figure AirStreet, BridgePulse, FloodGauge, LoadZone, SlopeWatch and WellSense use; NoiseMap ($119) and CurbCount (about $95) quote other figures. The allowance change (item 7) would affect sibling notes that cite 115 mW. No other repo was edited.

### Safety concerns

- Heat: without a shield the enclosure reaches 66 to 73 °C when dusty in 45 °C sun, near or above the electronics rating and well above LiFePO4 comfort. The 45 °C charge lockout must never be defeated to recover energy.
- Cold: the cell must not charge below 0 °C; a node on a long overcast freeze will stop rather than charge unsafely.
- Mounting: clamp preload (assumed 1,000 N) carries every wind margin; installers need a torque figure. The node adds about 80 N of wind load about 2 m up a site pole that this design does not check. Work at height and overhead lines as at TRL 2.
- About 19 Wh LiFePO4 cell left unattended: fuse, protection IC and NTC as specified.

### Gaps and notes

- No citations were flagged as unchecked in the TRL 2 note, so no WebFetch checks were run. The panel voltage coefficient, charger minimum input, cell cold capacity and clamp preload are typical values, not checked against a chosen part.
- Assumptions only tests can settle: the shield factor (0.25, borrowed from WWT-CAL-001), band preload, gateway sensitivity and real path loss.
- The kit's cutaway still cuts at the mean Y of the parts; with the scene shifted down by the enclosure's center height (as at TRL 2) the section shows the cell, boards and controller. The ports and glands fall in the removed half and show only in the exploded view, where callouts 3 and 10 partly cover their small parts.
- Existing material beyond TRL 3: `build-log/README.md` (scaffold) is present, untouched and not extended. No test, build or firmware material exists.

### Recommended next step

TRL 4 is on hold by Amish's instruction; this repo stops at TRL 3. Amish's review is needed on items 4 to 8 above and on O1 to O3. For the record only, TRL 4 would need: a bench build of the power board and core; a lab test report (TST, `environment: lab`) covering enclosure temperature in sun with and without the shield, charge lockout at 0 and 45 °C, sleep current and energy per report, and clamp preload and slip; and build log entries. None of this has been started.

## Session 2026-09-25: recommendations accepted

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Every item in this note and in FND-DDR-001 that carried a recommendation is now decided by Amish, 2026-09-25: go with recommendation. The decisions and their effects are recorded in `docs/decisions/0002-recommendations-accepted.md` (FND-DDR-002 v0.1).

### Decisions applied and what changed

| Decision | Before | After |
| --- | --- | --- |
| D1 to D12 (FND-DDR-001) | Adopted for TRL 3, open for review | Decided; no design change; `budget_usd` stays $150, pitch and problem unchanged |
| Sun shield, option (b): hot-climate sites only | Not in the design; R3 not met (58.7 to 73.3 °C inside at 45 °C) | BOM line 14 option at qty 0, $8.00, 0.15 kg; modeled (`build_shield()`, `cad/step/fieldnode-shield.step`); fitted where the design maximum exceeds 30 °C (FND-CAL-001 [C2c]); 48.5 to 52.2 °C inside at 45 °C with it; R3 restated, met on paper |
| R14 for the base node | 2.41 kg, at risk; 2.56 kg with a shield | R14 restated to the base node: 2.41 kg, met on paper (0.09 kg margin); hot-climate node 2.55 kg (shield mass now from the model) |
| 9 V class panel | 6 V class, Vmp 4.95 V when hot (0.05 V short of a 5 V charger minimum) | 9 V class, Vmp 7.42 V when hot (2.42 V headroom); same price; R5 met on paper |
| Published sensor allowance 100 mW | 115 mW cited by siblings; exactly 5.00 days | 100 mW published; 5.75 days, 15 % margin; R6 stays at risk for a cold (4.03 days) or aged (4.60 days) cell |
| Firmware airtime rule | R9 at risk: 43.5 s a day at SF10, 173.8 s at SF12 | Rule: 22 min at SF10, 48 min at SF11, 87 min at SF12 on The Things Network; 30.0 s a day or less; R9 restated, met on paper |

Files changed: `bom/bom.csv` (line 4 respecified, line 14 added) and `bom/bom-notes.md`; `cad/src/model.py` (shield parameters, `build_shield()`, `shield_geometry()`, new export) and re-exported STEP and STL; `cad/src/sheets.py` and FND-DWG-001 at Rev P2 (panel class and shield option notes, revision row); `cad/src/concept_media.py` key figures and all of `media/` re-rendered (hero, blueprint and exploded checked; `_views` folders deleted); `docs/04-calcs/sizing.py` and `results.csv`; FND-CAL-001 v0.2, FND-REQ-001 v0.4, FND-PRC-001 v0.4, FND-PRB-001 v0.4, FND-DDR-001 v0.2; `README.md` (key figures, components, and a rewritten "What sparked the idea" citing the 2003 Great Duck Island deployment); `project.yaml` evidence list. All PDFs rebuilt.

### Requirement status (FND-CAL-001 v0.2, Table 4)

None not met, 2 at risk, 1 not verifiable at TRL 3, 10 met on paper, 5 met by design.

| ID | Status | Key number |
| --- | --- | --- |
| R2 Operating temperature | At risk (cold) | No charging on clear days below about -13 °C; warm end covered (52.2 °C dusty worst case with the shield) |
| R6 Autonomy | At risk | 5.75 days at 100 mW; 4.03 days at -20 °C; 4.60 days at end of life |
| R12 Install | Not verifiable at TRL 3 | 15 min estimate, at the limit |
| R3, R5, R7, R8, R9, R10, R11, R13, R14, R16 | Met on paper | R3 and R5 rest on the assumed shield factor of 0.25 |
| R1, R4, R15, R17, R18 | Met by design | |

### Still awaiting Amish

1. **O1, first adopting projects and pilot region** (band and antenna). No recommendation.
2. **O2, sensor port pinout**, with the adopting teams. Candidate only, no recommendation.
3. **O3, firmware update method in the field.** No recommendation.

The cell heater for long sub-zero spells remains a suggestion only, not in the repo.

### Cross-repo actions (other repos not edited)

- **Sibling notes that cite a 115 mW allowance** (the adopting projects listed in FND-PRC-001): update to the published 100 mW allowance.
- **CurbCount** (about 300 mW) exceeds the allowance; it needs its own storage and panel sizing or the 10 W panel variant.
- **Hot-climate sibling pilots** (for example HeatMap Node or any site with a design maximum above 30 °C): add the $8.00, 0.15 kg shield to their FieldNode cost and mass ($134.00, 2.55 kg).
- **Sibling notes describing the panel** as 6 V class: now 9 V class.
- **TwinKit**: its twin example calls the cell FieldNode BOM part 4; the cell is line 6 (the panel is line 4).
- **NoiseMap ($119) and CurbCount (about $95)**: align their quoted FieldNode core cost with $126.00.
- **Kit**: the cutaway cutter and scale figure placement for pole-mounted repos (noted at TRL 2).

### TRL 4

TRL 4 remains on hold by Amish's instruction. `trl` and `trl_target` stay at 3. The charger part choice, firmware (including the airtime rule), a sun test of the shield factor, the power board and any purchasing have not been started.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26. This session added an appearance model for photoreal product renders; the massing model, BOM, calculations and drawing are unchanged.

### What was done

- `cad/src/product_model.py`: `product_parts()` (54 parts: 33 shell, 15 internal, 6 context), `TITLE` and `RENDER_VIEWS` (hero, exploded and a detail view without the pole). It imports `PARAMS`, `derived()`, `build_parts()` and `on_panel()` from `cad/src/model.py` and keeps every main dimension and interface: enclosure envelope and parting line, port, gland and antenna positions, internal plate and the envelopes on it, panel size, tilt and position, bracket members, back plate, V-blocks and clamp heights.
- Appearance detail added:
  - Enclosure base with filleted corners, side ribs, lid screw bosses and holes for the penetrations; lid with a parting line, the dark EPDM gasket showing, four captive stainless screws, a label with an accent band, port markings A and B and a lit green status light pipe.
  - M12 sockets with pin inserts (port A open, port B with a knurled, tethered sealing cap); M16 glands with domed nuts; the ePTFE vent; the whip antenna on a hex bulkhead.
  - Panel with an aluminium frame, cell grid, junction box and badge; bracket angle clips and M6 bolts; back plate with keyhole and band slots; true 90 deg V-blocks; band clamps with worm housings.
  - Inside: ASA plate with a lift-out slot, the LiFePO4 cell in its strapped, fused holder, power board and controller carrier with components, LoRa module shield can, antenna pigtail and a desiccant pack.
  - Context: a short section of the 48.3 mm pole with a cap, the panel lead from gland 1 to the junction box, and a sensor cable plugged into port A and tied to the pole.
- `README.md`: hero image now points to `media/render-hero.png`, with a link to `media/render-exploded.png`. The render files are produced separately.

### Differences from model.py, proposed, awaiting Amish

1. **Clear window in the lid** (96 x 58 mm, over the upper lid). BOM line 2 describes a plain gasketed lid. The window shows the cell and wiring in the renders and lets a field visit read the status without opening the box. Options: (a) plain grey lid, as the BOM; (b) grey lid with a clear UV-stabilized polycarbonate window, which several enclosure makers offer as a standard variant. **Recommendation: (b)** for the renders only until the enclosure is chosen at TRL 4; check the cost and UV rating then. Proposed, awaiting Amish.
2. **ePTFE vent position.** In `model.py` the vent sits at (58, -63) mm, which overlaps the antenna bulkhead at (58, -76) mm (13 mm apart for two 18 mm parts). The appearance model moves the vent to (30, -63) mm, about 5 mm clear of the nearer gland flange and 13 mm clear of the bulkhead. **Recommendation:** adopt the new position in `PARAMS` (a `vent_xy` entry) and on FND-DWG-001 at the next revision. Proposed, awaiting Amish.
3. **Status light pipe on the lid.** The BOM puts the status LED on the controller carrier (line 8); the appearance model adds a small light pipe through the lid so the LED shows from outside. **Recommendation:** keep it if option 1(a) is chosen; with the window it is optional. Proposed, awaiting Amish.
4. **V-blocks drawn with a true 90 deg V** instead of the cylindrical seat used for massing in `model.py`; the depth and clamp heights are unchanged. No decision needed; noted for the drawing.

### Scope

This is an appearance model only: no tolerances, no PCB layouts and no fabrication detail. `trl` and `trl_target` stay at 3, and TRL 4 remains on hold.

## Session 2026-09-27: kit 1.5.0 and image quality

- Kit 1.5.0 synced: STANDARDS v1.5 (sections 12 to 15: product renders, storefront images and image quality, public release, authorship and signing), `.kit/cards.py`, `.kit/image_qc.py`, `.kit/release_gate.py`, issue templates, and the `/render-product` and `/release` commands. `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- Every `media/render-*.png` recaptioned from its original render with the new layout: the title, concept label and repository sit in a band above the render and the view note in a band below it, each line wrapped to the image width, so no text overlaps other text or the render or runs off the image. `media/card.png` and `media/social-preview.png` regenerated with the same rules.
- `python .kit/image_qc.py` and `python .kit/release_gate.py` pass. trl stays 3.

## Session 2026-09-30: design for construction and illustrated build plan (BLD-001)

Run under `/build-plan` steps 1 to 4 with Amish's instruction of 2026-09-30 to replace the text-only plan: "Design concept and constructability are different states", speak plainly, draw every component and how it fits, and "fix the design assumptions to match and be physically feasible". This section replaces the earlier 2026-09-30 build plan section. Commit and push were skipped by instruction. TRL cap respected: no PCB layout, firmware, purchasing list, test plan or build log; the power board is bought modules wired at block level.

### What was done

- `cad/src/model.py`: rebuilt as components with every fixing, plus 97 build123d constructability checks (`python cad/src/model.py --check`: overlap volume and gap for every pair that must touch or must clear). All 97 pass. STEP and STL regenerated in `cad/step/` and `cad/stl/` (the shield file now includes its thumb screws).
- `docs/decisions/0003-design-for-construction.md` (FND-DDR-003): every change and its reason, "made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review".
- `docs/05-build-plan.md` (FND-BLD-001 v0.2): rewritten from `.kit/templates/build-plan.md` in plain English, components in build order, each with a making sketch, numbered making steps, a joint close-up and a check; twelve assembly steps each with a picture; first checks; safety stops; tools; open questions. The old text-only v0.1 is withdrawn (its research on modules, wiring and safety holds is reused).
- `cad/src/build_plan_media.py` (new) with `.kit/build_views.py`: overview, nine making sketches FND-DWG-101 to 109, two drilling layouts, eight joint close-ups, twelve step pictures and the block wiring diagram. Every picture was looked at and reworked where it was cluttered or unclear.
- `docs/04-calcs/sizing.py` re-run: mass from the new components, V-block geometry [D6b], cell swap with the shield [E2b]. FND-CAL-001 v0.3, FND-PRC-001 v0.5 and FND-REQ-001 v0.5 carry the new mass, cost, bracket and service figures. `bom/bom.csv`: lines 1, 5, 12, 13 and 14 respecified, line 15 added.
- Drawing FND-DWG-001 Rev P3 (`cad/src/sheets.py`): new penetration leaders and notes; its annotation offsets fixed (they no longer matched the kit 1.7 view layout, so dimensions sat about 11 mm off the views).
- Concept media regenerated (`cad/src/concept_media.py`): hero, blueprint, cutaway, exploded (now with callout 15), flow, model.glb and viewer.
- `project.yaml`: `design_state: constructable`; FND-DDR-003, the overview picture and `build_plan_media.py` added to `trl_evidence`. README: new "Building the prototype" section with the overview picture.
- Kit fixes, reported for the kit source: `.kit/build_views.py` (picture band kept clear of the title and subtitle; leader lines end on the part itself; joints drop parts a window leaves empty; `component_sheet` takes a laid-flat shape for the views and an inset camera); `.kit/drawing.py` (front and right view sublabels no longer overlap when the right view is narrow).

### Design changes made for construction (FND-DDR-003)

1. **V-blocks (P1):** 60 x 33 x 20 mm with a true 90° V, 50.3 mm wide, point 7.8 mm from the plate; the 48.3 mm pole touches both faces 24.9 mm from the plate; poles 40 to 71 mm seat. Two M4 countersunk screws each. The pole stays where the concept put it.
2. **Penetrations (P2, P3):** two rows 27 and 55 mm from the back face. Back row: glands at 40 and 8 mm left, vent 24 mm right. Front row: ports at 54 and 22 mm left, antenna 30 mm right. Flanges at least 8.0 mm apart (was 2 mm); vent and antenna 10.6 mm apart (were overlapping).
3. **Bracket (P4):** per side, a 30 x 30 x 3 angle plate clip (two M5 to the plate), a 20 x 3 flat-bar post on two M6 bolts (rigid), a 20 x 3 strut on one M6 bolt each end, and two 30 x 30 x 3 angle panel clips bolted through the panel frame's back lip (two M4 each). Every joint is face to face. The concept's pinned post and strut formed a linkage that could swing; the two-bolt post foot makes a rigid triangle.
4. **Shield (P5):** 12 mm flanges folded in at the back of each side, four M4 knurled thumb screws into tapped holes in the plate; slides off forward. Cell swap on a hot-climate node about 9 min (was 7 min); R15 (10 min) still met.
5. **Fuses and connectors (P6):** BOM line 15, a plug-in terminal strip on the internal plate (modelled) and a 0.5 A resettable fuse on each sensor supply.
6. **Enclosure fixing (P7):** four bought external lugs, one M5 button-head screw each through the plate.
7. **Internal plate fixing (P8):** on the enclosure's four moulded bosses, 6 mm off the back wall, four M4 screws.
8. **Band path (P9):** each band round the pole, through two slots in the plate 51 mm each side of centre and across the plate front (below the box and above it).
9. **Mass:** a 100 x 150 mm window in the back plate behind the box and 20 mm bar (was 25 mm) offset the added parts.
10. **Found while drawing:** the upper plate clip hole sat 5 mm below the plate edge; moved so it is 15 mm clear.

### Key results

- Constructability checks: 97 of 97 pass.
- Mass: base node **2.45 kg** (was 2.41 kg), **0.05 kg** under R14; hot-climate node 2.61 kg. R14 is met on paper, but the margin is thin.
- Cost: base node $139.00, hot-climate node $148.00, both within the unchanged $150 value-engineering target (`budget_usd`).
- Thermal, energy, radio and wind results unchanged (enclosure, panel and shield keep their size and place); clamp pull 59 N (63 N with the shield) against 2,000 N; bracket buckling factor 30.
- Requirement status unchanged: none not met; R2 and R6 at risk; R12 install time not verifiable at TRL 3.

### Proposed, awaiting Amish

1. **A1, shield fixing:** thumb screws (tool free) lower tamper resistance at a node mounted at 1.75 m partly against tampering. Options: (a) thumb screws; (b) M4 pan-head screws. Recommendation: (a) for the prototype. **Decided by Amish, 2026-09-30: go with recommendation.**
2. **A2, wall mounting:** the plate's back now carries screw heads and the V-blocks. Options: (a) remove the V-blocks and use 5 mm spacers on the wall screws; (b) a separate wall plate. Recommendation: (a). **Decided by Amish, 2026-09-30: go with recommendation.**
3. **A3, mass margin 0.05 kg:** (a) accept and weigh at TRL 4; (b) remove more mass now. Recommendation: (a). **Decided by Amish, 2026-09-30: go with recommendation.**
4. **A4, shield on the first prototype** (carried over): (a) yes, $148.00 within the value-engineering target; (b) base node first. Recommendation: (a). **Decided by Amish, 2026-09-30: go with recommendation.**
5. Still open: O1 pilot region and band, O2 port pin assignment, O3 firmware update method; the enclosure part (boss spacing, lug kit); a panel with a back lip at least 12 mm wide; the band torque that gives 1,000 N preload.

### Stale, to regenerate on Amish's Mac

- `media/render-hero.png`, `media/render-exploded.png`, `media/render-detail.png` (Blender photoreal renders) still show the concept bracket, V-blocks and penetration layout. `media/card.png` and `media/social-preview.png` are built from them.
- `cad/src/product_model.py` (the appearance model for those renders) still reads PARAMS keys the model no longer has (`port_x`, `gland_x`, `ant_x`, `bracket_x`, `post_ly` and others) and will not run until it is updated to the constructable geometry.
- `docs/pdf/` PDFs of FND-CAL-001, FND-PRC-001 and FND-REQ-001 are the older versions until `python .kit/render.py` is run.
- Cross-repo: sibling READMEs that cost the FieldNode core at about $126 should read $139.

### Safety concerns

- First charge of the LiFePO4 cell: the plan holds charging until the 3.6 V charge voltage and both temperature stops are shown with substitute resistors, then requires an attended first charge on a non-combustible surface.
- The charger's temperature window must be 0 to 45 °C and the protection board must use LiFePO4 limits; both are checked on the datasheet before buying.
- The new rail fuses limit a shorted sensor cable; the 5 A cell fuse stays.
- Sharp edges on cut bar, angle and 0.5 mm sheet; ASA print fumes; work at height stays outside the plan.

### Recommended next step

Amish reviews FND-DDR-003 and the illustrated plan, decides A1 to A4, and says whether this plan format should be used across the portfolio. The photoreal renders and `product_model.py` can then be brought up to the constructable design on his Mac. Building to the plan is TRL 4 work and stays on hold.

### Decisions, 2026-09-30

Amish, 2026-09-30: "i accept your recommended changes on design that are currently being sent across for my approval". FND-DDR-003 (design for construction) is accepted as v0.2, and A1 to A4 are decided as recommended: thumb screws on the shield for the prototype, 5 mm spacers for wall mounting with the V-blocks removed, accept the 0.05 kg mass margin and weigh at TRL 4, and fit the shield on the first prototype.

## 2026-10-02: open decisions decided

Amish, 2026-10-02: "i approve your recommendations for all 555 open decisions." The recommendations written for this repo's open decisions are recorded as decided.

### Decisions recorded

3 decisions, moved from "Open decisions" to "Decisions made" in the register (FND-DEC-001 v0.3):

1. Pilot region and radio band (FND-DDR-001, O1): US915 (North America) is the default first variant with a 915 MHz whip; the band switches to that of the first adopting project's site if it is outside North America (EU868, AS923 or IN865).
2. Sensor port pin assignment (FND-DDR-001, O2): pin 1 switched rail, pin 2 data A, pin 3 ground, pin 4 data B, pin 5 analog, as the proposed standard, sent to HeatMap Node and the next adopting project for sign-off.
3. Firmware update method in the field (FND-DDR-001, O3): by cable inside the box with the lid open, through a USB or serial header on the board, with no extra hole in the enclosure; over-the-air updates are left for a later private-gateway variant.

### Documents changed

- `docs/06-design-decisions.md`: FND-DEC-001 v0.3
- `docs/decisions/0001-trl2-review-decisions.md`: FND-DDR-001 v0.3 (O1 to O3 marked decided)
- `docs/decisions/0002-recommendations-accepted.md`: FND-DDR-002 v0.2 (O1 to O3 marked decided)
- `docs/01-problem.md`: FND-PRB-001 v0.5 (co-design partner and open questions)
- `docs/02-concept.md`: FND-PRC-001 v0.7 (pinout, band and firmware update)
- `docs/03-requirements.md`: FND-REQ-001 v0.7 (R11 status)
- `docs/04-calcs/01-sizing.md`: FND-CAL-001 v0.5 (R11 status in the requirement table; no figure changed)
- `docs/05-build-plan.md`: FND-BLD-001 v0.4 (port wiring and antenna text)
- `README.md` and `bom/bom-notes.md` (not controlled): pinout, antenna band and update method

### Follow-up actions to carry approved decisions into the design

1. Decision 1: BOM line 9, respecify the antenna as a 915 MHz whip for the US915 first variant (description only; price unchanged) (BOM).
2. Decision 1: set the LoRaWAN region to US915 in the firmware configuration when the firmware is written at TRL 4 (docs).
3. Decision 2: label the pin numbers and signals of ports A and B on the wiring picture of the build plan and on FND-DWG-001 (build plan pictures, drawings).
4. Decision 2: send the proposed pinout to HeatMap Node and the next adopting project and record their sign-off; this also closes HeatMap Node's open item 6 (docs).
5. Decision 3: add a USB or serial programming header to the power board and controller layout in the model, reachable with the lid open, and to the BOM notes of line 7 (model, BOM).

### Points found in the review

- Pole range is stated two ways: FND-DDR-003 P1 says poles of 40 to 71 mm seat on both V faces, while the concept, requirement R12 and the build plan say 40 to 60 mm. The band clamp length probably sets the 60 mm limit; worth one line saying so.
- HeatMap Node's open item 6 depends on item 2 here; deciding it closes both.
