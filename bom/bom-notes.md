# BOM notes

- Costs are indicative USD prices at quantity 1 for a concept estimate, not quotes. Every line is priced. Total $126.00 against the $150 `budget_usd`, a margin of $24.00 (FND-CAL-001, section F).
- This is the cost of the FieldNode core (enclosure, power, radio, panel and mounting). Sibling projects that use FieldNode cite this figure when they cost their own parts separately. Sensors and the gateway are not included (see TwinKit).
- Line numbers 1 to 12 match the callouts in `media/exploded.png` and the part keys in `cad/src/model.py`. Line 13 has no callout.
- TRL 3 changes: line 3 now has both glands fitted (one carries the panel lead), with the blanking plug moved to line 13; line 11 is printed ASA rather than aluminium, which saves about 0.11 kg. The total is unchanged.
- The power board (line 7) is priced as a prototype carrier; its design is TRL 4 work and has not been started.
- The antenna (line 9) must match the regional band chosen for the first deployment (DDR-001, O1).
- Proposed, awaiting Amish, and not in this BOM: a ventilated white aluminium sun shield, about $8 and 0.15 kg (FND-CAL-001, section C), which would bring the total to $134.00; and a 9 V class panel in place of the 6 V class, at about the same price.
