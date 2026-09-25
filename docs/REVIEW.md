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

### Proposed, awaiting Amish

1. **Radio.** Options: LoRaWAN (recommended), LoRa point-to-point, or cellular LTE-M/NB-IoT. Recommendation: LoRaWAN now; cellular as a later variant.
2. **Controller module.** Options: STM32WL-class module such as RAK3172 or Wio-E5 (recommended), ESP32 plus SX1262, or nRF52840 plus SX1262.
3. **Energy storage.** Options: one 6 Ah LiFePO4 cell with a 1S protection IC on the power board (recommended), 2 to 3 Li-ion 18650 cells, or a small CellGuard pack. CellGuard covers 4 to 16 cells, so it does not fit a 1S node; a note to the CellGuard project may be worth adding.
4. **Panel size.** 6 W standard (recommended), with 3 W and 10 W variants for low- and high-power payloads as a later option.
5. **Sensor port standard.** Two M12 5-pin ports carrying I2C, UART or RS-485, one analog input and switched rails (recommended), versus glands only. Pinout to be agreed with the first two adopting projects.
6. **Default reporting interval** of 15 min.
7. **Default network.** TwinKit gateway first, with The Things Network as the public fallback (recommended).
8. **First adopting projects and region** (which set the radio band).
9. **Enclosure.** Stock polycarbonate IP65 box (recommended) versus a printed ASA enclosure.
10. No change is proposed to `budget_usd`, the pitch or the problem in `project.yaml`.

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
