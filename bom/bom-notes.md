# BOM notes

- Costs are indicative USD prices at quantity 1 for a concept estimate, not quotes. Every line is priced. Base node total $126.00 against the $150 `budget_usd`, a margin of $24.00 (FND-CAL-001, section F). Line 14 is an option at quantity 0; a hot-climate node with it costs $134.00.
- This is the cost of the FieldNode core (enclosure, power, radio, panel and mounting). Sibling projects that use FieldNode cite this figure when they cost their own parts separately. Sensors and the gateway are not included (see TwinKit).
- Line numbers 1 to 12 match the callouts in `media/exploded.png` and the part keys in `cad/src/model.py`. Line 13 has no callout. Line 14 is modeled by `build_shield()` in `cad/src/model.py` and exported as `cad/step/fieldnode-shield.step`; it is not shown in the media.
- TRL 3 changes: line 3 now has both glands fitted (one carries the panel lead), with the blanking plug moved to line 13; line 11 is printed ASA rather than aluminium, which saves about 0.11 kg. The total is unchanged.
- The power board (line 7) is priced as a prototype carrier; its design is TRL 4 work and has not been started.
- The antenna (line 9) must match the regional band chosen for the first deployment (DDR-001, O1).
- Changes from Amish's 2026-09-25 decisions (FND-DDR-002): line 4 is now a 9 V class panel of the same power, at the same indicative price; line 14, a ventilated white aluminium sun shield ($8.00, 0.15 kg), is added as an option for sites whose design maximum exceeds 30 °C.
