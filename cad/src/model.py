"""FieldNode parametric model (build123d), TRL 3, constructable design (FND-DDR-003).

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl:
    fieldnode-assembly.step / .stl   the whole node on a stub of its 48.3 mm design pole
    fieldnode-core.step / .stl       enclosure, lid, penetrations and the parts inside
    fieldnode-mount.step / .stl      back plate, V-blocks, band clamps and panel bracket
    fieldnode-shield.step / .stl     hot-climate sun shield option (BOM line 14) with its thumb
                                     screws; not in the base node or the assembly (FND-DDR-002)
and prints the constructability checks (python cad/src/model.py --check prints them only).

Axes: the site pole is the Z axis (x = y = 0), Z is up with the ground at z = 0, and the
node faces -Y (toward the equator), so the panel tilts toward -Y and shades the enclosure
below it. X is to the right seen from the front.

Revised 2026-09-30 under Amish's instruction to make the design physically buildable
(FND-DDR-003, "Design for construction"). Every component is now a shape that can be cut,
drilled, bent, printed or bought, and every joint has a fixing:
    V-blocks 60 x 33 x 20 mm with a true 90 deg V that seats the pole on its faces;
    penetrations in two rows on the bottom face, at least 8 mm apart;
    enclosure held to the back plate by four external lugs and M5 screws;
    internal plate on four moulded bosses with M4 screws and a plug-in connector strip;
    panel bracket of angle clips on the plate, angle clips on the panel frame's back lip,
    and flat-bar posts and struts bolted flat to them (post two bolts, strut one each end);
    sun shield with folded fixing flanges and four M4 thumb screws, so it lifts off;
    a window in the back plate behind the enclosure to hold the mass requirement.
Main dimensions and interfaces only; tolerances are TRL 4 work. The same PARAMS feed
docs/04-calcs/sizing.py (FND-CAL-001), the drawing FND-DWG-001 (cad/src/sheets.py), the
concept media (cad/src/concept_media.py) and the build plan pictures (cad/src/build_plan_media.py).
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # site interface: pole on the Z axis (design case 48.3 mm OD, 1.5 in nominal pipe)
    "pole_od": 48.3, "pole_range": (40.0, 60.0),
    # 1, 2 enclosure: outside W (X) x D (Y) x H (Z), wall, lid depth; bottom height above ground
    "enc": (150.0, 90.0, 200.0), "enc_wall": 3.0, "lid_d": 12.0, "z0": 1750.0,
    # 1 enclosure lugs (bought with the enclosure): x of centre, width, thickness, reach beyond the box
    "lug": (62.0, 16.0, 4.0, 16.0),
    # 12 back plate (W x H x t), rear face distance in front of the pole axis, bottom below z0
    "plate": (180.0, 320.0, 3.0), "plate_y0": -42.0, "plate_drop": 40.0,
    # 12 lightening window behind the enclosure (W x H, corner radius), centred on the enclosure
    "window": (100.0, 150.0, 6.0),
    # 12 V-blocks: width (X) x depth (Y, from the plate) x height (Z), 90 deg V
    "vblock": (60.0, 33.0, 20.0),
    # 12 stainless band clamps: width, thickness; slot centre x in the plate; clamp heights above z0
    "band": (12.0, 0.8), "band_slot_x": 51.0, "clamp_dz": (-20.0, 230.0),
    # 4 solar panel 6 W (X x slope x thickness), tilt from horizontal, center (y, height above z0),
    #   frame wall and back lip width
    "panel": (290.0, 200.0, 17.0), "tilt": 40.0, "panel_c": (-115.0, 385.0), "frame": (1.5, 12.0),
    # 5 bracket: aluminium flat bar (width x thickness) for posts and struts; aluminium angle
    #   (leg x thickness) for all clips; x of the inner face of the plate clip's upright leg;
    #   plate clip bottom and top above z0; post lower bolt (y, height above z0) and bolt pitch;
    #   strut foot bolt (y, height above z0); head bolts on the panel clips (slope position, depth
    #   below the panel mid-plane); panel clip length along the slope
    "bar": (20.0, 3.0), "angle": (30.0, 3.0), "clip_x": 80.0, "clip_z": (218.0, 295.0),
    "post_foot": (-63.0, 262.0), "post_pitch": 24.0, "strut_foot": (-62.0, 232.0),
    "head_ly": (85.0, -85.0), "head_lz": -25.0, "pclip_len": 30.0,
    # 11 internal plate (W x H x t) on moulded bosses (x, z offset from the enclosure centre, height)
    "mplate": (130.0, 180.0, 3.0), "boss": (55.0, 80.0, 6.0),
    # 6 cell 32700 (dia x length); 7 power modules; 8 controller carrier; 15 connector strip
    "cell": (32.0, 70.0), "power": (80.0, 60.0, 10.0), "ctrl": (70.0, 45.0, 8.0), "strip": (70.0, 12.0, 14.0),
    # bottom-face penetrations: two rows, distance forward of the enclosure's back face
    "pen_rows": (27.0, 55.0),
    #   name: (x, row, thread dia = hole, outside flange dia)
    "pens": {"gland_1": (-40.0, 0, 16.0, 24.0), "gland_2": (-8.0, 0, 16.0, 24.0), "vent": (24.0, 0, 12.0, 18.0),
             "port_a": (-54.0, 1, 16.0, 22.0), "port_b": (-22.0, 1, 16.0, 22.0), "antenna": (30.0, 1, 6.4, 18.0)},
    "whip": (10.0, 190.0),            # whip diameter and length below the bulkhead
    # 14 hot-climate sun shield option (FND-DDR-002): sheet thickness, air gap to the enclosure
    #   front, sides and top, open bottom, vent slot at the back of the top sheet; drop of the lower
    #   edge above the enclosure base; fixing flange width and thumb screw heights above z0
    "shield_t": 0.5, "shield_gap": 15.0, "shield_slot": 30.0, "shield_low": 10.0,
    "shield_flange": 12.0, "shield_screw_dz": (40.0, 180.0),
}

BOM = {  # model key: (BOM line, name)
    "body": (1, "Enclosure body with vent and lugs"),
    "lid": (2, "Enclosure lid with gasket"),
    "glands": (3, "Cable glands, 2 x M16"),
    "panel": (4, "Solar panel, 6 W"),
    "bracket": (5, "Panel tilt bracket"),
    "cell": (6, "LiFePO4 cell, 6 Ah, fused holder"),
    "power": (7, "Power board (MPPT, protection)"),
    "ctrl": (8, "Controller and LoRa module"),
    "antenna": (9, "Antenna, sub-GHz whip"),
    "ports": (10, "Sensor ports, 2 x M12 5-pin"),
    "mplate": (11, "Internal mounting plate"),
    "mount": (12, "Pole mounting kit"),
    "connectors": (15, "Plug-in connectors, rail fuses"),
}
OPTIONS = {  # option parts, not in the base node (FND-DDR-002)
    "shield": (14, "Sun shield, hot-climate option"),
}


@dataclass
class Comp:
    """One component: a single made or bought piece (or a matched set of fixings)."""
    name: str
    shape: object
    bom: int | None
    kind: str          # "made", "bought" or "fixing"
    group: str | None  # key in BOM (build_parts groups components by it)


def derived(p=PARAMS):
    """Dimensions the calc note and the drawing quote, computed from PARAMS."""
    ew, ed, eh = p["enc"]
    pw, pl, pt = p["plate"]
    z0 = p["z0"]
    enc_back = p["plate_y0"] - pt
    enc_front = enc_back - ed
    t = math.radians(p["tilt"])
    pcy, pcz = p["panel_c"][0], z0 + p["panel_c"][1]
    half = p["panel"][1] / 2
    low = (pcy - half * math.cos(t), pcz - half * math.sin(t))    # front (-Y) edge, underside ignored
    high = (pcy + half * math.cos(t), pcz + half * math.sin(t))
    clamps = [z0 + dz for dz in p["clamp_dz"]]
    r = p["pole_od"] / 2
    apex = -p["plate_y0"] - r * math.sqrt(2)          # V apex behind the plate's rear face, design pole
    return {
        "enc_back": enc_back, "enc_front": enc_front, "enc_yc": (enc_back + enc_front) / 2,
        "enc_bot": z0, "enc_top": z0 + eh, "enc_zc": z0 + eh / 2,
        "plate_bot": z0 - p["plate_drop"], "plate_top": z0 - p["plate_drop"] + pl, "plate_front": enc_back,
        "panel_cy": pcy, "panel_cz": pcz, "panel_low": low, "panel_high": high,
        "panel_area_m2": p["panel"][0] * p["panel"][1] / 1e6,
        "overhang_front": enc_front - low[0],                      # plan overhang of the panel beyond the lid
        "clear_top": low[1] - (z0 + eh),                           # panel front edge above the enclosure top
        "clamps": clamps, "clamp_span": clamps[1] - clamps[0],
        "overall_top": high[1] + p["panel"][2] / 2 * math.cos(t),
        "whip_tip": z0 - 20 - p["whip"][1],
        "vblock_depth": p["vblock"][1],
        "v_apex": apex,                                            # mm from the plate's rear face
        "v_mouth": 2 * (p["vblock"][1] - apex),                    # width of the V at the block's face
        "v_contact": apex + r / math.sqrt(2),                      # design pole touches the V faces here
        "enc_area": {"front": ew * eh / 1e6, "side": ed * eh / 1e6, "top": ew * ed / 1e6, "bottom": ew * ed / 1e6},
    }


def _b3d():
    import build123d as b
    return b


def box(cx, cy, cz, sx, sy, sz):
    b = _b3d()
    return b.Pos(cx, cy, cz) * b.Box(sx, sy, sz)


def bx(x0, x1, y0, y1, z0, z1):
    return box((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def zcyl(x, y, z, r, h):
    b = _b3d()
    return b.Pos(x, y, z) * b.Cylinder(r, h)


def ycyl(x, y, z, r, h):
    b = _b3d()
    return b.Pos(x, y, z) * b.Rot(90, 0, 0) * b.Cylinder(r, h)


def xcyl(x, y, z, r, h):
    b = _b3d()
    return b.Pos(x, y, z) * b.Rot(0, 90, 0) * b.Cylinder(r, h)


def hexprism(axis, x, y, z, af, h):
    """Hexagon (across flats af) of length h along axis 'x', 'y' or 'z', centred on (x, y, z)."""
    b = _b3d()
    s = b.extrude(b.RegularPolygon(af / math.sqrt(3), 6), h / 2, both=True)
    rot = {"z": b.Rot(0, 0, 0), "y": b.Rot(90, 0, 0), "x": b.Rot(0, 90, 0)}[axis]
    return b.Pos(x, y, z) * rot * s


def fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def mirror_x(shape):
    b = _b3d()
    return shape.mirror(b.Plane.YZ)


def on_panel(ly, p=PARAMS, lz=None):
    """(y, z) of a point on the panel at slope coordinate ly and depth lz from its mid-plane
    (default: the underside, which is the plane of the frame's back lip)."""
    t = math.radians(p["tilt"])
    lz = -p["panel"][2] / 2 if lz is None else lz
    pcy, pcz = p["panel_c"][0], p["z0"] + p["panel_c"][1]
    return pcy + ly * math.cos(t) - lz * math.sin(t), pcz + ly * math.sin(t) + lz * math.cos(t)


def _panel_frame(p=PARAMS):
    """Placement that takes panel-local coordinates (lx across, ly up the slope, lz out of the
    glass) to the model."""
    b = _b3d()
    D = derived(p)
    return b.Pos(0, D["panel_cy"], D["panel_cz"]) * b.Rot(p["tilt"], 0, 0)


def flat_bar(a, c, w, t, x0, holes=()):
    """Flat bar lying in the YZ plane between x0 and x0 + t, round-ended on the hole centres a and c
    ((y, z) pairs), width w, with extra holes (y, z) and 6.6 mm holes at a and c."""
    b = _b3d()
    (ya, za), (yc, zc) = a, c
    L = math.hypot(yc - ya, zc - za)
    u = ((yc - ya) / L, (zc - za) / L)
    pl = b.Plane(origin=(x0, ya, za), x_dir=(0, u[0], u[1]), z_dir=(1, 0, 0))
    sk = b.Pos(L / 2, 0) * b.SlotCenterToCenter(L, w)
    for (yh, zh) in ((ya, za), (yc, zc), *holes):
        s_ = (yh - ya) * u[0] + (zh - za) * u[1]
        n_ = -(yh - ya) * u[1] + (zh - za) * u[0]
        sk -= b.Pos(s_, n_) * b.Circle(3.3)
    return b.extrude(pl * sk, t)


def bracket_points(p=PARAMS):
    """Bolt centres (y, z) of one side frame: post lower and upper foot bolts, post head, strut
    foot, strut head."""
    z0 = p["z0"]
    yh, zh = on_panel(p["head_ly"][0], p, p["head_lz"])
    ys, zs = on_panel(p["head_ly"][1], p, p["head_lz"])
    yf, dzf = p["post_foot"]
    L = math.hypot(yh - yf, zh - (z0 + dzf))
    u = ((yh - yf) / L, (zh - z0 - dzf) / L)
    k = p["post_pitch"]
    return {"post_low": (yf, z0 + dzf), "post_up": (yf + k * u[0], z0 + dzf + k * u[1]), "post_head": (yh, zh),
            "strut_foot": (p["strut_foot"][0], z0 + p["strut_foot"][1]), "strut_head": (ys, zs)}


def _side_bracket(p=PARAMS):
    """Right-hand side frame of the bracket (x > 0): plate clip, post, strut, two panel clips.
    Returns {name: shape}. The left side is its mirror image."""
    b = _b3d()
    z0 = p["z0"]
    aw, at = p["angle"]
    bw, bt = p["bar"]
    xc = p["clip_x"]                                    # inner face of the plate clip's upright leg
    yfr = p["plate_y0"] - p["plate"][2]                 # plate front face
    za, zb = z0 + p["clip_z"][0], z0 + p["clip_z"][1]
    B = bracket_points(p)
    out = {}
    # plate clip: 30 x 30 x 3 angle, one leg flat on the plate, the other standing forward
    clip = bx(xc + at - aw, xc + at, yfr - at, yfr, za, zb) + bx(xc, xc + at, yfr - aw, yfr, za, zb)
    for zz in (za + 17, zb - 30):                       # two M5 holes into the plate
        clip -= ycyl(xc + at - aw + 12, yfr - at / 2, zz, 2.75, at + 2)
    for key in ("post_low", "post_up", "strut_foot"):
        y_, z_ = B[key]
        clip -= xcyl(xc + at / 2, y_, z_, 3.3, at + 2)
    out["plate clip"] = clip
    # post: flat bar outboard of the clip, two bolts at the foot, one at the head
    out["post"] = flat_bar(B["post_low"], B["post_head"], bw, bt, xc + at, holes=(B["post_up"],))
    # strut: flat bar inboard of the clip, one bolt each end
    out["strut"] = flat_bar(B["strut_foot"], B["strut_head"], bw, bt, xc - bt)
    # panel clips: 30 x 30 x 3 angle, flat leg on the frame's back lip (2 x M4), upright leg down
    F = _panel_frame(p)
    lzb = -p["panel"][2] / 2
    L = p["pclip_len"]
    for name, x_in, ly in (("high panel clip", xc + at + bt, p["head_ly"][0]), ("low panel clip", xc, p["head_ly"][1])):
        s = 1 if ly > 0 else -1
        ly0, ly1 = sorted((ly - s * (L / 2), ly + s * (L / 2)))
        c = bx(x_in, x_in + aw, ly0, ly1, lzb - at, lzb) + bx(x_in, x_in + at, ly0, ly1, lzb - aw, lzb)
        edge = s * (p["panel"][1] / 2 - 6)
        for xx in (x_in + 11, x_in + 23):
            c -= zcyl(xx, edge, lzb - at / 2, 2.25, at + 2)
        c -= xcyl(x_in + at / 2, ly, p["head_lz"], 3.3, at + 2)
        out[name] = F * c
    return out


def _bolt_x(x_face_a, x_face_b, y, z, d=6.0, head=10.0):
    """Hex bolt and nyloc nut along X clamping the stack between x_face_a and x_face_b (a < b)."""
    hl, nl = 0.6 * d, 0.9 * d
    return (hexprism("x", x_face_a - hl / 2, y, z, head, hl) + xcyl((x_face_a + x_face_b) / 2, y, z, d / 2 - 0.3, x_face_b - x_face_a)
            + hexprism("x", x_face_b + nl / 2, y, z, head, nl) + xcyl(x_face_b + nl + 1, y, z, d / 2 - 0.3, 2))


def _bolt_y(y_back, y_front, x, z, d=5.0, head=8.0):
    """Button-head screw from behind (+Y side) and nyloc nut in front along Y (y_front < y_back)."""
    hl, nl = 0.55 * d, 0.9 * d
    return (ycyl(x, y_back + hl / 2, z, head / 2 + 0.75, hl) + ycyl(x, (y_back + y_front) / 2, z, d / 2 - 0.3, y_back - y_front)
            + hexprism("y", x, y_front - nl / 2, z, head, nl) + ycyl(x, y_front - nl - 1, z, d / 2 - 0.3, 2))


def build_components(p=PARAMS, shield=False):
    """Every component as a Comp, keyed by a short name. shield=True adds the sun shield option
    and its thumb screws."""
    b = _b3d()
    D = derived(p)
    ew, ed, eh = p["enc"]
    w, ld = p["enc_wall"], p["lid_d"]
    z0, zc = p["z0"], D["enc_zc"]
    yb = D["enc_back"]
    C = {}

    def add(key, name, shape, bom, kind, group):
        C[key] = Comp(name, shape, bom, kind, group)

    # penetration positions
    pen_xy = {k: (x, yb - p["pen_rows"][row]) for k, (x, row, _, _) in p["pens"].items()}

    # 1 enclosure body, open to -Y, with four moulded bosses for the internal plate and the
    #   bottom face drilled for the penetrations
    bd = ed - ld
    ybody = yb - bd / 2
    body = box(0, ybody, zc, ew, bd, eh) - box(0, ybody - w, zc, ew - 2 * w, bd, eh - 2 * w)
    bxo, bzo, bh = p["boss"]
    for sx in (-1, 1):
        for sz in (-1, 1):
            body += ycyl(sx * bxo, yb - w - bh / 2, zc + sz * bzo, 4.0, bh)
            body -= ycyl(sx * bxo, yb - w - bh + 4, zc + sz * bzo, 1.6, 8.1)   # pilot for the M4 screw
    for k, (x, row, dt, df) in p["pens"].items():
        hole = dt / 2 + (0.1 if dt >= 10 else 0.05)
        body -= zcyl(x, pen_xy[k][1], z0 + w / 2, hole, w + 2)
    add("body", "Enclosure body", body, 1, "bought", "body")
    ylid = D["enc_front"] + ld / 2
    add("lid", "Enclosure lid", box(0, ylid, zc, ew, ld, eh) - box(0, ylid + w, zc, ew - 2 * w, ld, eh - 2 * w), 2, "bought", "lid")

    # 1 lugs: four external mounting lugs, flat on the plate, above and below the box
    lx, lw, lt, lr = p["lug"]
    lugs, lug_fix = [], []
    for sx in (-1, 1):
        for zlo, zhi in ((D["enc_top"], D["enc_top"] + lr), (z0 - lr, z0)):
            lug = bx(sx * lx - lw / 2, sx * lx + lw / 2, yb - lt, yb, zlo, zhi)
            zh = (zlo + zhi) / 2 + (1 if zlo > z0 else -1)
            lug -= ycyl(sx * lx, yb - lt / 2, zh, 2.75, lt + 2)
            lugs.append(lug)
            lug_fix.append(_bolt_y(p["plate_y0"], yb - lt, sx * lx, zh))
    add("lugs", "Enclosure lugs (4)", fuse(lugs), 1, "bought", "body")
    add("lug_screws", "M5 screws and nuts, lugs (4)", fuse(lug_fix), 13, "fixing", None)

    # 1 vent, 3 glands, 10 ports, 9 antenna: outside part, thread through the wall, nut inside
    def pen(k):
        x, y = pen_xy[k]
        _, _, dt, df = p["pens"][k]
        fl = zcyl(x, y, z0 - 1.5, df / 2, 3.0)
        thr = zcyl(x, y, z0 + w / 2, dt / 2, w)
        return x, y, dt, df, fl, thr
    glands = []
    for k in ("gland_1", "gland_2"):
        x, y, dt, df, fl, thr = pen(k)
        glands.append(fl + zcyl(x, y, z0 - 10, 10.0, 14.0) + thr + hexprism("z", x, y, z0 + w + 2.5, 22.0, 5.0)
                      + zcyl(x, y, z0 + w + 6, dt / 2, 2))
    add("glands", "Cable glands, 2 x M16", fuse(glands), 3, "bought", "glands")
    ports = []
    for k in ("port_a", "port_b"):
        x, y, dt, df, fl, thr = pen(k)
        ports.append(fl + zcyl(x, y, z0 - 12.5, 8.0, 19.0) + thr + hexprism("z", x, y, z0 + w + 2.5, 22.0, 5.0)
                     + zcyl(x, y, z0 + w + 9, 7.0, 8))
    add("ports", "Sensor ports, 2 x M12", fuse(ports), 10, "bought", "ports")
    x, y, dt, df, fl, thr = pen("vent")
    add("vent", "Membrane vent, M12", zcyl(x, y, z0 - 4, df / 2, 8.0) + thr + hexprism("z", x, y, z0 + w + 1.5, 17.0, 3.0),
        1, "bought", "body")
    x, y, dt, df, fl, thr = pen("antenna")
    wd, wl = p["whip"]
    ant = (hexprism("z", x, y, z0 - 2, 16.0, 4.0) + thr + hexprism("z", x, y, z0 + w + 1.5, 8.0, 3.0)
           + zcyl(x, y, z0 - 12, 7.0, 16.0) + zcyl(x, y, z0 - 20 - wl / 2, wd / 2, wl))
    add("antenna", "Antenna, bulkhead and whip", ant, 9, "bought", "antenna")

    # 11 internal plate on the bosses, and the parts it carries
    mw, mh, mt = p["mplate"]
    yp1 = yb - w - bh                                   # rear face of the internal plate
    mf = yp1 - mt                                       # its front face
    mp = bx(-mw / 2, mw / 2, mf, yp1, zc - mh / 2, zc + mh / 2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            mp -= ycyl(sx * bxo, yp1 - mt / 2, zc + sz * bzo, 2.25, mt + 2)
    finger = b.Pos(0, yp1 - mt / 2, zc + mh / 2 - 12) * b.Box(40, mt + 2, 10)
    mp -= b.fillet(finger.edges().filter_by(b.Axis.Y), 4.9)
    add("mplate", "Internal mounting plate", mp, 11, "made", "mplate")
    add("mplate_screws", "M4 screws, internal plate (4)",
        fuse(ycyl(sx * bxo, mf - 1.4, zc + sz * bzo, 3.5, 2.8) for sx in (-1, 1) for sz in (-1, 1)), 13, "fixing", None)
    cd, cl = p["cell"]
    add("cell", "LiFePO4 cell in fused holder",
        zcyl(-38, mf - cd / 2 - 4, z0 + 75, cd / 2, cl) + box(-38, mf - 5, z0 + 75, cd + 6, 10, cl + 10), 6, "bought", "cell")
    pw_, ph_, pt_ = p["power"]
    add("power", "Power modules", box(22, mf - pt_ / 2, z0 + 70, pw_, pt_, ph_)
        + box(30, mf - pt_ - 6, z0 + 62, 22, 12, 18) + box(5, mf - pt_ - 4, z0 + 82, 14, 8, 10), 7, "bought", "power")
    cw, ch, ct = p["ctrl"]
    add("ctrl", "Controller and LoRa module", box(10, mf - ct / 2, z0 + 150, cw, ct, ch) + box(0, mf - ct - 3, z0 + 150, 24, 6, 20),
        8, "bought", "ctrl")
    sw, sd, sh = p["strip"]
    zs = zc - mh / 2 + 4 + sh / 2
    add("connectors", "Plug-in connector strip", box(0, mf - sd / 2, zs, sw, sd, sh)
        + box(0, mf - sd - 4, zs, sw - 6, 8, sh - 4), 15, "bought", "connectors")

    # 12 back plate: band slots, V-block screws, lug, clip, shield and wall holes, window
    plw, plh, plt = p["plate"]
    y0p = p["plate_y0"]
    ymid = y0p - plt / 2
    plate = bx(-plw / 2, plw / 2, y0p - plt, y0p, D["plate_bot"], D["plate_top"])
    ww, wh, wr = p["window"]
    win = box(0, ymid, zc, ww, plt + 2, wh)
    plate -= b.fillet(win.edges().filter_by(b.Axis.Y), wr)
    bw_, bt_ = p["band"]
    xs = p["band_slot_x"]
    for zz in D["clamps"]:
        for sx in (-1, 1):
            plate -= box(sx * xs, ymid, zz, 3.0, plt + 2, bw_ + 3)
            plate -= ycyl(sx * 18, ymid, zz, 2.25, plt + 2)                 # M4 countersunk, V-block
            plate -= b.Pos(sx * 18, y0p - plt, zz) * b.Rot(-90, 0, 0) * b.Cone(4.1, 2.1, 2.0, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))
    for sx in (-1, 1):
        for zlo, zhi in ((D["enc_top"], D["enc_top"] + lr), (z0 - lr, z0)):
            plate -= ycyl(sx * lx, ymid, (zlo + zhi) / 2 + (1 if zlo > z0 else -1), 2.75, plt + 2)
        for zz in (z0 + p["clip_z"][0] + 17, z0 + p["clip_z"][1] - 30):
            plate -= ycyl(sx * (p["clip_x"] + p["angle"][1] - p["angle"][0] + 12), ymid, zz, 2.75, plt + 2)
        for dz in p["shield_screw_dz"]:
            plate -= ycyl(sx * (ew / 2 + p["shield_gap"] - p["shield_flange"] / 2), ymid, z0 + dz, 1.65, plt + 2)
        for xx, zz in ((40.0, D["plate_top"] - 15), (75.0, D["plate_bot"] + 12)):
            plate -= ycyl(sx * xx, ymid, zz, 3.25, plt + 2)
    add("plate", "Back plate", plate, 12, "made", "mount")

    # 12 V-blocks, true 90 deg V; the design pole touches both faces
    vw, vd, vh = p["vblock"]
    ap = D["v_apex"]
    for key, zz in (("vblock_low", D["clamps"][0]), ("vblock_up", D["clamps"][1])):
        blk = bx(-vw / 2, vw / 2, y0p, y0p + vd, zz - vh / 2, zz + vh / 2)
        ya, m = y0p + ap, vd - ap + 2
        tri = b.Pos(0, 0, zz - vh / 2 - 1) * b.extrude(b.Polygon((0, ya), (m, ya + m), (-m, ya + m), align=None), vh + 2)
        blk -= tri
        for sx in (-1, 1):
            blk -= ycyl(sx * 18, y0p + 6, zz, 1.65, 12)                          # M4 tapped, 12 deep
        add(key, "V-block, " + ("lower" if key == "vblock_low" else "upper"), blk, 12, "made", "mount")

    # 12 band clamps: a stainless band round the back of the pole, through the plate slots and
    #   across the plate's front face, with its worm-drive housing behind the pole
    r = p["pole_od"] / 2
    bands = []
    for zz in D["clamps"]:
        inner = b.make_hull(b.Circle(r).edges() + (b.Pos(0, y0p - plt / 2) * b.Rectangle(2 * (xs - 1), plt)).edges())
        outer = b.offset(inner, bt_, kind=b.Kind.ARC)
        ring = b.Pos(0, 0, zz - bw_ / 2) * (b.extrude(outer, bw_) - b.extrude(inner, bw_))
        ring += box(0, r + bt_ + 5, zz, 16, 10, bw_ + 4)
        bands.append(ring)
    add("bands", "Band clamps (2)", fuse(bands), 12, "bought", "mount")

    # 5 bracket, both sides
    side = _side_bracket(p)
    for name, s in side.items():
        key = name.replace(" ", "_")
        add(key + "_r", name.capitalize() + ", right", s, 5, "made", "bracket")
        add(key + "_l", name.capitalize() + ", left", mirror_x(s), 5, "made", "bracket")
    B = bracket_points(p)
    xc, at, bt = p["clip_x"], p["angle"][1], p["bar"][1]
    fix = []
    for key in ("post_low", "post_up"):
        fix.append(_bolt_x(xc, xc + at + bt, *B[key]))
    fix.append(_bolt_x(xc - bt, xc + at, *B["strut_foot"]))
    fix.append(_bolt_x(xc + at, xc + at + bt + at, *B["post_head"]))
    fix.append(_bolt_x(xc - bt, xc + at, *B["strut_head"]))
    xa = xc + at - p["angle"][0] + 12
    yfr = y0p - plt
    for zz in (z0 + p["clip_z"][0] + 17, z0 + p["clip_z"][1] - 30):
        fix.append(_bolt_y(y0p, yfr - at, xa, zz))
    fr = fuse(fix)
    add("bracket_bolts", "M6 and M5 bolts, bracket", fr + mirror_x(fr), 13, "fixing", None)

    # 4 panel: framed module (frame wall, back lip, laminate) and junction box
    pw, pl, pt = p["panel"]
    fw, lip = p["frame"]
    F = _panel_frame(p)
    frame = bx(-pw / 2, pw / 2, -pl / 2, pl / 2, -pt / 2, pt / 2) - bx(-pw / 2 + fw, pw / 2 - fw, -pl / 2 + fw, pl / 2 - fw, -pt / 2 + 2, pt / 2 - 1.5)
    frame -= bx(-pw / 2 + lip, pw / 2 - lip, -pl / 2 + lip, pl / 2 - lip, -pt / 2 - 1, -pt / 2 + 2.01)
    frame -= bx(-pw / 2 + 4, pw / 2 - 4, -pl / 2 + 4, pl / 2 - 4, pt / 2 - 1.51, pt / 2 + 1)
    for sx in (-1, 1):                                  # holes drilled in the back lip for the clips
        for s_ in (1, -1):
            x_in = xc + at + bt if s_ > 0 else xc
            for xx in (x_in + 11, x_in + 23):
                frame -= zcyl(sx * xx, s_ * (pl / 2 - 6), -pt / 2 + 1, 2.25, 4)
    lam = bx(-pw / 2 + fw, pw / 2 - fw, -pl / 2 + fw, pl / 2 - fw, pt / 2 - 5.5, pt / 2 - 1.5)
    jb = bx(-30, 30, 20, 60, pt / 2 - 20.5, pt / 2 - 5.5)
    add("panel", "Solar panel, 6 W", F * (frame + lam + jb), 4, "bought", "panel")
    pfix = []
    for s_ in (1, -1):
        x_in = xc + at + bt if s_ > 0 else xc
        for xx in (x_in + 11, x_in + 23):
            yy = s_ * (pl / 2 - 6)
            pfix.append(zcyl(xx, yy, -pt / 2 - at - 1.2, 3.5, 2.4) + zcyl(xx, yy, -pt / 2, 1.9, 2 * at + 4.0)
                        + hexprism("z", xx, yy, -pt / 2 + 2 + 1.6, 7.0, 3.2))
    pf = F * fuse(pfix)
    add("panel_bolts", "M4 bolts, panel clips (8)", pf + mirror_x(pf), 13, "fixing", None)

    if shield:
        sh, screws = _shield(p)
        add("shield", "Sun shield", sh, 14, "made", "shield")
        add("shield_screws", "M4 thumb screws, shield (4)", screws, 14, "fixing", None)
    return C


def _shield(p=PARAMS):
    """Hot-climate sun shield option (BOM line 14): one folded 0.5 mm sheet with front, two sides,
    a top with a vent slot at the back and tabs folded down over the sides, and a fixing flange
    folded inward at the back edge of each side, held to the back plate by two M4 thumb screws.
    Open at the bottom, so air rises through the 15 mm gap."""
    D = derived(p)
    ew, ed, eh = p["enc"]
    t, g = p["shield_t"], p["shield_gap"]
    yb = p["plate_y0"] - p["plate"][2]                     # front face of the back plate
    yf = D["enc_front"] - g                                # inner face of the front sheet
    xo = ew / 2 + g                                        # inner face of the side sheets
    zlo, zhi = D["enc_bot"] + p["shield_low"], D["enc_top"] + g
    front = bx(-(xo + t), xo + t, yf - t, yf, zlo, zhi + t)
    parts = [front]
    ytop0, ytop1 = yf - t, yb - p["shield_slot"]
    parts.append(bx(-(xo + t), xo + t, ytop0, ytop1, zhi, zhi + t))
    fl = p["shield_flange"]
    screws = []
    for sx in (-1, 1):
        parts.append(bx(sx * xo, sx * (xo + t), yf, yb, zlo, zhi))
        parts.append(bx(sx * (xo + t), sx * (xo + 2 * t), yf - t, ytop1, zhi - 10, zhi + t))   # top tab
        flange = bx(sx * xo, sx * (xo - fl), yb - t, yb, zlo, zhi)
        xsc = sx * (xo - fl / 2)
        for dz in p["shield_screw_dz"]:
            flange -= ycyl(xsc, yb - t / 2, p["z0"] + dz, 2.25, t + 2)
            screws.append(ycyl(xsc, yb - t - 2.5, p["z0"] + dz, 6.0, 5.0) + ycyl(xsc, yb + 1.5, p["z0"] + dz, 1.6, 8.0))
        parts.append(flange)
    return fuse(parts), fuse(screws)


def build_shield(p=PARAMS):
    """The shield sheet only (for its mass in FND-CAL-001)."""
    return _shield(p)[0]


def shield_geometry(p=PARAMS):
    """Sheet area (m2) and outside size (mm) of the shield, for FND-CAL-001."""
    D = derived(p)
    ew, ed, eh = p["enc"]
    t, g = p["shield_t"], p["shield_gap"]
    w = ew + 2 * (g + t)
    d = (p["plate_y0"] - p["plate"][2]) - (D["enc_front"] - g - t)
    h = eh + g + t - p["shield_low"]
    area = (w * h + 2 * d * h + w * (d - p["shield_slot"]) + 2 * p["shield_flange"] * h) / 1e6
    return {"w": w, "d": d, "h": h, "area_m2": area, "front_m2": w * h / 1e6, "side_m2": d * h / 1e6}


def bracket_geometry(p=PARAMS):
    """Hole-to-hole lengths (mm) and angles from horizontal (deg) of one side frame, for FND-CAL-001.
    The post is measured from its lower foot bolt."""
    B = bracket_points(p)
    out = {}
    for key, a, c in (("post", "post_low", "post_head"), ("strut", "strut_foot", "strut_head")):
        (y0, z0), (y1, z1) = B[a], B[c]
        L = math.hypot(y1 - y0, z1 - z0)
        out[key] = {"L": L, "angle": math.degrees(math.atan2(z1 - z0, abs(y1 - y0))), "foot": (y0, z0), "head": (y1, z1),
                    "bar_len": L + p["bar"][0]}
    return out


def build_parts(p=PARAMS):
    """Return {BOM key: solid} for the BOM lines with geometry (line 13, hardware, has none).
    Fixings are left out."""
    C = build_components(p)
    out = {}
    for c in C.values():
        if c.group:
            out[c.group] = c.shape if c.group not in out else out[c.group] + c.shape
    return out


def pole_context(p=PARAMS, length=600.0):
    """Stub of the site pole (grey on the drawing and renders); not in the BOM."""
    return zcyl(0, 0, p["z0"] + 240, p["pole_od"] / 2, length)


def assembly(p=PARAMS, with_pole=False):
    b = _b3d()
    parts = build_parts(p)
    kids = list(parts.values()) + ([pole_context(p)] if with_pole else [])
    return b.Compound(children=kids)


# ------------------------------------------------------------------ constructability checks
def _vol(a, b_):
    try:
        s = a & b_
        return s.volume if s is not None else 0.0
    except Exception:
        return float("nan")


def _gap(a, b_):
    return a.distance_to(b_)


def checks(p=PARAMS):
    """Pairs that must not overlap, and the gap or contact between them (mm). Returns a list of
    (description, overlap volume mm3, gap mm, expectation, ok)."""
    C = build_components(p, shield=True)
    pole = pole_context(p, length=900)
    S = lambda k: C[k].shape  # noqa: E731
    rows = []

    def chk(desc, a, b_, expect):
        """expect: 'touch' (no overlap, gap 0) or a minimum clearance in mm."""
        v = _vol(a, b_)
        gp = _gap(a, b_)
        ok = v < 1e-3 and (gp < 0.05 if expect == "touch" else gp >= expect - 1e-6)
        rows.append((desc, v, gp, expect, ok))

    for k in ("vblock_low", "vblock_up"):
        chk(f"{C[k].name} on the back plate", S(k), S("plate"), "touch")
        chk(f"{C[k].name} on the pole (V faces)", S(k), pole, "touch")
        chk(f"{C[k].name} clear of the band", S(k), S("bands"), 1.0)
    chk("Band on the pole", S("bands"), pole, "touch")
    chk("Band through the plate slots and across its front", S("bands"), S("plate"), "touch")
    chk("Enclosure body on the back plate", S("body"), S("plate"), "touch")
    chk("Lugs on the back plate", S("lugs"), S("plate"), "touch")
    chk("Lugs against the enclosure", S("lugs"), S("body"), "touch")
    chk("Lid on the body", S("lid"), S("body"), "touch")
    chk("Internal plate on the bosses", S("mplate"), S("body"), "touch")
    for k in ("cell", "power", "ctrl", "connectors"):
        chk(f"{C[k].name} on the internal plate", S(k), S("mplate"), "touch")
        chk(f"{C[k].name} clear of the lid", S(k), S("lid"), 1.0)
    for k in ("glands", "ports", "vent", "antenna"):
        chk(f"{C[k].name} in the bottom face", S(k), S("body"), "touch")
        chk(f"{C[k].name} clear of the internal plate", S(k), S("mplate"), 1.0)
        chk(f"{C[k].name} clear of the connector strip", S(k), S("connectors"), 1.0)
    # penetrations apart from each other (outside flanges and inside nuts)
    names = ("glands", "ports", "vent", "antenna")
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            chk(f"{C[a].name} apart from {C[b_].name}", S(a), S(b_), 4.0)
    pen = {k: v for k, v in p["pens"].items()}
    D = derived(p)
    ypen = {k: (x, D["enc_back"] - p["pen_rows"][row]) for k, (x, row, _, _) in pen.items()}
    ks = list(pen)
    for i, a in enumerate(ks):
        for b_ in ks[i + 1:]:
            (xa, ya), (xb, yb) = ypen[a], ypen[b_]
            gapf = math.hypot(xa - xb, ya - yb) - (pen[a][3] + pen[b_][3]) / 2
            rows.append((f"Flange gap {a} to {b_}", 0.0, gapf, 8.0, gapf >= 8.0 - 1e-6))
    for side in ("r", "l"):
        chk(f"Plate clip ({side}) on the back plate", S(f"plate_clip_{side}"), S("plate"), "touch")
        chk(f"Post ({side}) on the plate clip", S(f"post_{side}"), S(f"plate_clip_{side}"), "touch")
        chk(f"Strut ({side}) on the plate clip", S(f"strut_{side}"), S(f"plate_clip_{side}"), "touch")
        chk(f"Post ({side}) on the high panel clip", S(f"post_{side}"), S(f"high_panel_clip_{side}"), "touch")
        chk(f"Strut ({side}) on the low panel clip", S(f"strut_{side}"), S(f"low_panel_clip_{side}"), "touch")
        chk(f"High panel clip ({side}) on the panel frame", S(f"high_panel_clip_{side}"), S("panel"), "touch")
        chk(f"Low panel clip ({side}) on the panel frame", S(f"low_panel_clip_{side}"), S("panel"), "touch")
        chk(f"Post ({side}) clear of the back plate", S(f"post_{side}"), S("plate"), 1.0)
        chk(f"Strut ({side}) clear of the back plate", S(f"strut_{side}"), S("plate"), 1.0)
        chk(f"Post ({side}) clear of the panel", S(f"post_{side}"), S("panel"), 0.5)
        chk(f"Strut ({side}) clear of the panel", S(f"strut_{side}"), S("panel"), 0.5)
        chk(f"Strut ({side}) clear of the enclosure", S(f"strut_{side}"), S("body") + S("lid"), 1.0)
        chk(f"Strut ({side}) clear of the post", S(f"strut_{side}"), S(f"post_{side}"), 0.5)
        chk(f"Plate clip ({side}) clear of the lugs", S(f"plate_clip_{side}"), S("lugs"), 1.0)
        chk(f"Plate clip ({side}) clear of the band", S(f"plate_clip_{side}"), S("bands"), 1.0)
        chk(f"Strut ({side}) clear of the shield", S(f"strut_{side}"), S("shield"), 3.0)
        chk(f"Plate clip ({side}) clear of the shield", S(f"plate_clip_{side}"), S("shield"), 1.0)
    chk("Bracket bolts clear of the enclosure and shield", S("bracket_bolts"), S("body") + S("lid") + S("shield"), 1.0)
    chk("Shield flanges on the back plate", S("shield"), S("plate"), "touch")
    chk("Shield clear of the enclosure (15 mm air gap, flanges beside it)", S("shield"), S("body") + S("lid"), 2.5)
    chk("Shield thumb screws clear of the enclosure", S("shield_screws"), S("body"), 1.0)
    chk("Shield clear of the lugs", S("shield"), S("lugs"), 1.0)
    chk("Shield clear of the lug screws", S("shield"), S("lug_screws"), 1.0)
    chk("Shield thumb screws on the flanges", S("shield_screws"), S("shield"), "touch")
    chk("Panel clear of the enclosure and shield", S("panel"), S("body") + S("lid") + S("shield"), 50.0)
    chk("Band clear of the enclosure", S("bands"), S("body"), 5.0)
    return rows


def print_checks(p=PARAMS):
    rows = checks(p)
    bad = 0
    for desc, v, gp, exp, ok in rows:
        e = "touch" if exp == "touch" else f">= {exp:g} mm"
        print(f"  {'ok ' if ok else 'BAD'}  {desc:58s} overlap {v:8.3f} mm3  gap {gp:7.2f} mm  ({e})")
        bad += not ok
    print(f"constructability checks: {len(rows) - bad} of {len(rows)} pass")
    return bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(1 if print_checks() else 0)
    from build123d import Compound, export_step, export_stl
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True)
    (out / "stl").mkdir(exist_ok=True)
    C = build_components(shield=True)
    core = ("body", "lid", "lugs", "vent", "glands", "ports", "antenna", "mplate", "mplate_screws", "cell", "power", "ctrl", "connectors", "lug_screws")
    mount = [k for k, c in C.items() if c.bom in (5, 12) or k in ("bracket_bolts", "panel_bolts")]
    base = [c.shape for k, c in C.items() if c.bom != 14]
    groups = {
        "fieldnode-assembly": base + [pole_context()],
        "fieldnode-core": [C[k].shape for k in core],
        "fieldnode-mount": [C[k].shape for k in mount],
        "fieldnode-shield": [C["shield"].shape, C["shield_screws"].shape],
    }
    for name, shapes in groups.items():
        c = Compound(children=shapes)
        export_step(c, str(out / "step" / f"{name}.step"))
        export_stl(c, str(out / "stl" / f"{name}.stl"))
        bb = c.bounding_box()
        print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    D = derived()
    print(f"panel overhang beyond lid {D['overhang_front']:.1f} mm, front edge {D['clear_top']:.1f} mm above enclosure top; "
          f"top of panel {D['overall_top']:.0f} mm above ground; clamp span {D['clamp_span']:.0f} mm")
    print(f"V-block: apex {D['v_apex']:.2f} mm from the plate, mouth {D['v_mouth']:.1f} mm, design pole touches at {D['v_contact']:.1f} mm")
    sg = shield_geometry()
    print(f"sun shield option: {sg['w']:.0f} x {sg['d']:.0f} x {sg['h']:.0f} mm, sheet {sg['area_m2']:.4f} m2")
    for k, v in bracket_geometry().items():
        print(f"bracket {k}: {v['L']:.1f} mm between holes at {v['angle']:.1f} deg; bar {v['bar_len']:.0f} mm")
    print_checks()
