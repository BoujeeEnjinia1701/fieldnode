"""FieldNode concept massing model and media (TRL 2).

Run from the repo root:  python cad/src/concept_media.py
Proportions and main parts only; CONCEPT, NOT FOR FABRICATION.

Coordinates in mm. Z up, ground at Z = 0. The site pole (48.3 mm OD, 1.5 in
nominal pipe) stands on the Z axis. The node faces -Y (toward the equator in
the proposed install), so the solar panel tilts toward -Y and shades the
enclosure below it. Grey parts are site supplied or for scale and carry no BOM
number; every colored part carries the BOM line number used in bom/bom.csv.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Cylinder, Pos, Rot, Solid, Plane, Vector
from concept import Part, render_all, human_figure

# ---------------- key dimensions (mm) ----------------
POLE_R = 24.15            # 48.3 mm OD pole
ENC_W, ENC_D, ENC_H = 150.0, 90.0, 200.0    # enclosure outside, X x Y x Z
WALL = 3.0
LID_D = 12.0
Z0 = 1750.0               # enclosure bottom, above head height to deter tampering
PLATE_Y0 = -42.0          # back plate rear face (a V-block fills the gap to the pole)
PLATE_T = 6.0
ENC_BACK = PLATE_Y0 - PLATE_T              # enclosure back face
ENC_FRONT = ENC_BACK - ENC_D               # front face of lid
PANEL_W, PANEL_L, PANEL_T = 290.0, 200.0, 17.0   # 6 W panel, X x slope x thickness
TILT = 40.0               # panel tilt from horizontal (site latitude dependent)
PANEL_C = (0.0, -115.0, 2135.0)


def rod(a, b, r):
    """Round bar between two 3D points."""
    a = Vector(*a); b = Vector(*b); d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


zc = Z0 + ENC_H / 2
yc_body = ENC_BACK - (ENC_D - LID_D) / 2

# 1 Enclosure body with membrane vent (polycarbonate, IP65 or better)
body_d = ENC_D - LID_D
body = (Pos(0, yc_body, zc) * Box(ENC_W, body_d, ENC_H)
        - Pos(0, yc_body - WALL, zc) * Box(ENC_W - 2 * WALL, body_d, ENC_H - 2 * WALL))
vent = Pos(58, ENC_BACK - 20, Z0 - 4) * Cylinder(9, 8)
body = body + vent
# 2 Enclosure lid (front cover) with gasket
lid_y = ENC_FRONT + LID_D / 2
lid = (Pos(0, lid_y, zc) * Box(ENC_W, LID_D, ENC_H)
       - Pos(0, lid_y + WALL, zc) * Box(ENC_W - 2 * WALL, LID_D, ENC_H - 2 * WALL))

# 11 Internal mounting plate, just inside the back wall
in_back = ENC_BACK - WALL
mplate = Pos(0, in_back - 1.5, zc) * Box(130, 3, 180)
MP_FRONT = in_back - 3.0

# 6 LiFePO4 cell, 32700 format (32 mm x 70 mm, about 6 Ah), in a holder with inline fuse
cell = (Pos(-38, MP_FRONT - 20, Z0 + 75) * Cylinder(16, 70)
        + Pos(-38, MP_FRONT - 5, Z0 + 75) * Box(38, 10, 80))

# 7 Power board: MPPT charger, cell protection, NTC charge lockout, switched sensor rails
power = (Pos(22, MP_FRONT - 5, Z0 + 70) * Box(80, 10, 60)
         + Pos(30, MP_FRONT - 16, Z0 + 62) * Box(22, 12, 18)          # inductor and terminal block
         + Pos(5, MP_FRONT - 14, Z0 + 82) * Box(14, 8, 10))

# 8 Controller and LoRa module (STM32WL class) on a carrier with SPI flash
ctrl = (Pos(10, MP_FRONT - 4, Z0 + 150) * Box(70, 8, 45)
        + Pos(0, MP_FRONT - 11, Z0 + 150) * Box(24, 6, 20))

# 3 Cable gland (M16) for a wired sensor
gland = Pos(25, yc_body - 5, Z0 - 9) * (Cylinder(11, 18) + Pos(0, 0, 6) * Cylinder(13, 6))

# 10 Sensor ports: two M12 5-pin panel connectors with sealing caps
ports = None
for x in (-45, -12):
    p = Pos(x, yc_body - 5, Z0 - 11) * (Cylinder(8, 22) + Pos(0, 0, 8) * Cylinder(11, 6))
    ports = p if ports is None else ports + p

# 9 Antenna: bulkhead and whip pointing down, out of the panel's shadow and away from the lid
ant = (Pos(58, yc_body + 8, Z0 - 10) * Cylinder(9, 20)
       + rod((58, yc_body + 8, Z0 - 20), (58, yc_body + 8, Z0 - 210), 5))

# 12 Pole and wall mounting kit: back plate, V-blocks and two stainless band clamps
plate = Pos(0, PLATE_Y0 - PLATE_T / 2, zc) * Box(180, PLATE_T, 320)
mount = plate
for zz in (Z0 - 20, Z0 + 230):
    vblock = Pos(0, (PLATE_Y0 - POLE_R + 4) / 2, zz) * Box(50, -PLATE_Y0 - POLE_R + 4, 30)
    band = Pos(0, 0, zz) * (Cylinder(POLE_R + 3, 20) - Cylinder(POLE_R + 0.5, 22))
    mount = mount + vblock + band

# 4 Solar panel, 6 W monocrystalline, tilted toward -Y
panel = Pos(*PANEL_C) * Rot(TILT, 0, 0) * Box(PANEL_W, PANEL_L, PANEL_T)


def on_panel(ly, lz=-PANEL_T / 2):
    """Point on the panel underside at local slope coordinate ly (mm)."""
    import math
    t = math.radians(TILT)
    return (PANEL_C[1] + ly * math.cos(t) - lz * math.sin(t), PANEL_C[2] + ly * math.sin(t) + lz * math.cos(t))


# 5 Panel tilt bracket: two rear posts and two front struts from the back plate
bracket = None
for x in (-80, 80):
    yb, zb = on_panel(80)
    yf, zf = on_panel(-60)
    post = rod((x, PLATE_Y0 - PLATE_T / 2, zc + 150), (x, yb, zb), 6)
    strut = rod((x, PLATE_Y0 - PLATE_T, zc + 140), (x, yf, zf), 5)
    bracket = post + strut if bracket is None else bracket + post + strut

# Site pole: a stub in the model, the full pole only in the hero for scale
pole_stub = Pos(0, 0, Z0 + 240) * Cylinder(POLE_R, 600)
pole_low = Pos(0, 0, (Z0 - 60) / 2) * Cylinder(POLE_R, Z0 - 60)
footing = Pos(0, 0, -40) * Cylinder(150, 80)

# Exploded-view offsets are set in screen terms for the default isometric camera
# (elevation 24 deg, azimuth -58 deg): sx to the right, sy up, t toward the viewer (mm).
import math
_e, _a = math.radians(24), math.radians(-58)
CAM = (math.cos(_e) * math.cos(_a), math.cos(_e) * math.sin(_a), math.sin(_e))
RIGHT = (-CAM[1], CAM[0], 0.0)
_n = math.hypot(*RIGHT); RIGHT = (RIGHT[0] / _n, RIGHT[1] / _n, 0.0)
UP = (-RIGHT[1] * CAM[2], RIGHT[0] * CAM[2], RIGHT[1] * CAM[0] - RIGHT[0] * CAM[1])


def scr(sx, sy, t=0.0):
    return tuple(sx * RIGHT[i] + sy * UP[i] + t * CAM[i] for i in range(3))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


BODY = scr(-150, 0, 150)
GROUP = scr(-420, 30, 240)
parts = [
    Part("Pole, 48 mm OD (site supplied)", pole_stub, "#9CA3AF", None),
    Part("Enclosure body with membrane vent", body, "#E5E7EB", 1, BODY),
    Part("Enclosure lid with gasket", lid, "#F3F4F6", 2, scr(-680, -20, 320)),
    Part("Cable gland, M16", gland, "#111827", 3, add(BODY, scr(20, -230, 0))),
    Part("Solar panel, 6 W", panel, "#1E3A8A", 4, scr(0, 330, 0)),
    Part("Panel tilt bracket", bracket, "#6B7280", 5, scr(40, 150, 0)),
    Part("LiFePO4 cell, 6 Ah, fused holder", cell, "#C2410C", 6, add(GROUP, scr(-15, -10, 60))),
    Part("Power board (MPPT, protection)", power, "#16A34A", 7, add(GROUP, scr(15, -20, 60))),
    Part("Controller and LoRa module", ctrl, "#0F766E", 8, add(GROUP, scr(25, 55, 60))),
    Part("Antenna, sub-GHz whip", ant, "#374151", 9, add(BODY, scr(110, -170, 0))),
    Part("Sensor ports, 2 x M12 5-pin", ports, "#D4A017", 10, add(BODY, scr(-110, -230, 0))),
    Part("Internal mounting plate", mplate, "#94A3B8", 11, GROUP),
    Part("Pole mounting kit", mount, "#A8A29E", 12, (0, 0, 0)),
]

context = [
    Part("Pole, 48 mm OD, and footing (site supplied)", pole_low + footing, "#9CA3AF"),
    human_figure(1750.0, x=520.0, y=0.0, z=0.0),
]

# The kit's cutaway cutter is centered on Z = 0, so shift the whole scene down to put the
# enclosure near the origin. Heights above ground stay as modeled (ground is at Z = -SHIFT).
SHIFT = zc
for p in parts + context:
    p.shape = Pos(0, 0, -SHIFT) * p.shape

render_all(
    parts, project="FieldNode", title="Pole-mounted solar sensor node concept", dwg_no="FND-DWG-010",
    key_figures=["Enclosure 150 x 90 x 200 mm, IP65 class; 6 W panel above as sun and rain hood",
                 "LiFePO4 cell 3.2 V, 6 Ah, about 19 Wh; charging blocked below 0 °C",
                 "About 5 days autonomy at full sensor load, no sun (estimate)",
                 "Sensor allowance about 115 mW average, 2.75 Wh/day (estimate)",
                 "LoRaWAN uplink every 15 min; parts about $126 (indicative)"],
    scale_figure=False, context=context,
    cut_exclude=("Pole, 48 mm OD (site supplied)", "Solar panel, 6 W", "Panel tilt bracket"),
    flow={"title": "daily energy flow in the worst month, Wh per day (estimates, 2 peak sun hours)", "unit": "Wh",
          "stages": [("6 W panel x 2 sun h", 12.0), ("Panel output", 9.6), ("Charger output", 8.2),
                     ("Stored in cell", 7.8), ("Drawn from cell", 3.1), ("Sensors and core", 2.8)],
          "losses": [(0, "Heat, dust, angle (20 %)", 2.4), (1, "MPPT charger (15 %)", 1.4),
                     (2, "Cell charging (5 %)", 0.4), (3, "Unused surplus", 4.7),
                     (4, "Rail converters (10 %)", 0.3)]},
)
