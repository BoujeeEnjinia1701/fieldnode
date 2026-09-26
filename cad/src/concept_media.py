"""FieldNode concept media (TRL 3, FND-DDR-002 applied), generated from the parametric model.

Run from the repo root:  python cad/src/concept_media.py
Takes the node's parts from cad/src/model.py (PARAMS) and renders the media set with
.kit/concept.py. Every colored part carries the BOM line number used in bom/bom.csv; grey
parts (the site pole and footing, the person) are context with no BOM number. Figures on
the sheet and in the flow diagram come from docs/04-calcs/sizing.py (FND-CAL-001).
CONCEPT, NOT FOR FABRICATION. The hot-climate sun shield (BOM line 14) is an option and is
not shown; the renders show the base node.

Coordinates in mm. Z up, ground at Z = 0 in the model. The site pole stands on the Z axis
and the node faces -Y (toward the equator).
"""
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from build123d import Cylinder, Pos  # noqa: E402
from concept import Part, render_all, human_figure  # noqa: E402
from model import PARAMS as P, BOM, build_parts, derived, pole_context  # noqa: E402

D = derived(P)
m = build_parts()

# Exploded-view offsets are set in screen terms for the default isometric camera
# (elevation 24 deg, azimuth -58 deg): sx to the right, sy up, t toward the viewer (mm).
_e, _a = math.radians(24), math.radians(-58)
CAM = (math.cos(_e) * math.cos(_a), math.cos(_e) * math.sin(_a), math.sin(_e))
RIGHT = (-CAM[1], CAM[0], 0.0)
_n = math.hypot(*RIGHT)
RIGHT = (RIGHT[0] / _n, RIGHT[1] / _n, 0.0)
UP = (-RIGHT[1] * CAM[2], RIGHT[0] * CAM[2], RIGHT[1] * CAM[0] - RIGHT[0] * CAM[1])


def scr(sx, sy, t=0.0):
    return tuple(sx * RIGHT[i] + sy * UP[i] + t * CAM[i] for i in range(3))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


BODY = scr(-150, 0, 150)
GROUP = scr(-420, 30, 240)
STYLE = {  # key: (color, exploded offset)
    "body": ("#E5E7EB", BODY),
    "lid": ("#F3F4F6", scr(-680, -20, 320)),
    "glands": ("#111827", add(BODY, scr(60, -250, 0))),
    "panel": ("#1E3A8A", scr(0, 330, 0)),
    "bracket": ("#6B7280", scr(40, 150, 0)),
    "cell": ("#C2410C", add(GROUP, scr(-15, -10, 60))),
    "power": ("#16A34A", add(GROUP, scr(15, -20, 60))),
    "ctrl": ("#0F766E", add(GROUP, scr(25, 55, 60))),
    "antenna": ("#374151", add(BODY, scr(150, -170, 0))),
    "ports": ("#D4A017", add(BODY, scr(-120, -250, 0))),
    "mplate": ("#94A3B8", GROUP),
    "mount": ("#A8A29E", (0, 0, 0)),
}
parts = [Part("Pole, 48 mm OD (site supplied)", pole_context(P), "#9CA3AF", None)]
for key, (num, name) in BOM.items():
    color, off = STYLE[key]
    parts.append(Part(name, m[key], color, num, off))

pole_low = Pos(0, 0, (P["z0"] - 60) / 2) * Cylinder(P["pole_od"] / 2, P["z0"] - 60)
footing = Pos(0, 0, -40) * Cylinder(150, 80)
context = [
    Part("Pole, 48 mm OD, and footing (site supplied)", pole_low + footing, "#9CA3AF"),
    human_figure(1750.0, x=520.0, y=0.0, z=0.0),
]

# The kit's cutaway cutter is centered on Z = 0 and at the mean Y of the parts, so shift the
# whole scene down to put the enclosure at the origin. Heights above ground stay as modeled
# (ground ends up at Z = -SHIFT).
SHIFT = D["enc_zc"]
for p in parts + context:
    p.shape = Pos(0, 0, -SHIFT) * p.shape

render_all(
    parts, project="FieldNode", title="Pole-mounted solar sensor node concept", dwg_no="FND-DWG-010",
    key_figures=["Enclosure 150 x 90 x 200 mm, IP65; 6 W, 9 V class panel as rain hood",
                 "LiFePO4 cell 3.2 V, 6 Ah, about 19 Wh; charging 0 to 45 °C only",
                 "Worst month: 7.75 Wh/day stored against 2.67 Wh/day drawn",
                 "Published sensor allowance 100 mW; 5.75 days with no sun",
                 "LoRaWAN every 15 min at SF9; $126, 2.41 kg; shield option above 30 °C"],
    scale_figure=False, context=context,
    cut_exclude=("Pole, 48 mm OD (site supplied)", "Solar panel, 6 W", "Panel tilt bracket"),
    flow={"title": "daily energy flow in the worst month, Wh per day (FND-CAL-001 estimates, 2 peak sun hours, 100 mW sensors)",
          "unit": "Wh",
          "stages": [("6 W panel x 2 sun h", 12.0), ("Panel output", 9.6), ("Charger output", 8.16),
                     ("Stored in cell", 7.75), ("Drawn from cell", 2.67), ("Sensors and core", 2.40)],
          "losses": [(0, "Heat, dust, angle (20 %)", 2.4), (1, "MPPT charger (15 %)", 1.44),
                     (2, "Cell charging (5 %)", 0.41), (3, "Unused surplus", 5.08),
                     (4, "Rail converters (10 %)", 0.27)]},
)
