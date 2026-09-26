"""FieldNode parametric model (build123d), TRL 3, massing-plus level of detail. Revised for FND-DDR-002.

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl:
    fieldnode-assembly.step / .stl   the whole node on a stub of its 48.3 mm design pole
    fieldnode-core.step / .stl       enclosure, lid, penetrations and the parts inside
    fieldnode-mount.step / .stl      back plate, V-blocks, band clamps and panel bracket
    fieldnode-shield.step / .stl     hot-climate sun shield option (BOM line 14), not in the base
                                     node or the assembly (FND-DDR-002)

Axes: the site pole is the Z axis (x = y = 0), Z is up with the ground at z = 0, and the
node faces -Y (toward the equator), so the panel tilts toward -Y and shades the enclosure
below it. Main dimensions and interfaces only: enclosure envelope and penetrations, internal
plate and the parts on it, panel size, tilt and position, bracket members, back plate,
V-blocks and clamp positions for 40 to 60 mm poles. Not fabrication detail; not for
fabrication. The same PARAMS feed docs/04-calcs/sizing.py (FND-CAL-001), the drawing
FND-DWG-001 (cad/src/sheets.py) and the concept media (cad/src/concept_media.py).
"""
import math
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # site interface: pole on the Z axis (design case 48.3 mm OD, 1.5 in nominal pipe)
    "pole_od": 48.3, "pole_range": (40.0, 60.0),
    # 1, 2 enclosure: outside W (X) x D (Y) x H (Z), wall, lid depth; bottom height above ground
    "enc": (150.0, 90.0, 200.0), "enc_wall": 3.0, "lid_d": 12.0, "z0": 1750.0,
    # 12 back plate (W x H x t), rear face distance in front of the pole axis, bottom below z0
    "plate": (180.0, 320.0, 3.0), "plate_y0": -42.0, "plate_drop": 40.0,
    # 12 V-blocks (width x height, 90 deg V) and stainless band clamps (width); clamp heights above z0
    "vblock": (50.0, 30.0), "band_w": 12.0, "clamp_dz": (-20.0, 230.0),
    # 4 solar panel 6 W (X x slope x thickness), tilt from horizontal, center (y, height above z0)
    "panel": (290.0, 200.0, 17.0), "tilt": 40.0, "panel_c": (-115.0, 385.0),
    # 5 bracket: aluminium flat bar (width x thickness), post and strut x positions,
    #   attachment points on the panel underside (local slope coordinate), feet above z0
    "bar": (25.0, 3.0), "bracket_x": 80.0, "post_ly": 80.0, "strut_ly": -60.0,
    "post_foot_dz": 260.0, "strut_foot_dz": 210.0,
    # 11 internal plate (W x H x t); 6 cell 32700 (dia x length); 7 power board; 8 controller carrier
    "mplate": (130.0, 180.0, 3.0), "cell": (32.0, 70.0),
    "power": (80.0, 60.0, 10.0), "ctrl": (70.0, 45.0, 8.0),
    # bottom-face penetrations: x positions of 10 M12 ports, 3 M16 glands, 9 antenna bulkhead
    "port_x": (-52.0, -22.0), "gland_x": (8.0, 34.0), "ant_x": 58.0,
    "m12_d": (16.0, 22.0), "m16_d": (20.0, 24.0),
    "whip": (10.0, 190.0),            # whip diameter and length below the bulkhead
    "vent_d": 18.0,                   # ePTFE vent (part of item 1), bottom face, rear right
    # 14 hot-climate sun shield option (FND-DDR-002): white aluminium sheet thickness, air gap to the
    #   enclosure front, sides and top, open bottom, and a vent slot at the back of the top sheet
    #   (clears the bracket strut feet); drop below the enclosure top to the shield's lower edge
    "shield_t": 0.5, "shield_gap": 15.0, "shield_slot": 30.0, "shield_low": 10.0,
}

BOM = {  # model key: (BOM line, name)
    "body": (1, "Enclosure body with membrane vent"),
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
}
OPTIONS = {  # option parts, not in the base node (FND-DDR-002)
    "shield": (14, "Sun shield, hot-climate option"),
}


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
    return {
        "enc_back": enc_back, "enc_front": enc_front, "enc_yc": (enc_back + enc_front) / 2,
        "enc_bot": z0, "enc_top": z0 + eh, "enc_zc": z0 + eh / 2,
        "plate_bot": z0 - p["plate_drop"], "plate_top": z0 - p["plate_drop"] + pl,
        "panel_cy": pcy, "panel_cz": pcz, "panel_low": low, "panel_high": high,
        "panel_area_m2": p["panel"][0] * p["panel"][1] / 1e6,
        "overhang_front": enc_front - low[0],                      # plan overhang of the panel beyond the lid
        "clear_top": low[1] - (z0 + eh),                           # panel front edge above the enclosure top
        "clamps": clamps, "clamp_span": clamps[1] - clamps[0],
        "overall_top": high[1] + p["panel"][2] / 2 * math.cos(t),
        "whip_tip": z0 - 20 - p["whip"][1],
        "vblock_depth": -p["plate_y0"] - p["pole_od"] / 2 + 4,     # V-block from plate to pole surface, plus seat
        "enc_area": {"front": ew * eh / 1e6, "side": ed * eh / 1e6, "top": ew * ed / 1e6, "bottom": ew * ed / 1e6},
    }


def _b3d():
    import build123d as b
    return b


def box(cx, cy, cz, sx, sy, sz):
    b = _b3d()
    return b.Pos(cx, cy, cz) * b.Box(sx, sy, sz)


def zcyl(x, y, z, r, h):
    b = _b3d()
    return b.Pos(x, y, z) * b.Cylinder(r, h)


def bar(a, c, w, t):
    """Flat bar of width w and thickness t (thickness along X) from point a to point c."""
    b = _b3d()
    a, c = b.Vector(*a), b.Vector(*c)
    d = c - a
    pl = b.Plane(origin=a, x_dir=(1, 0, 0), z_dir=d.normalized())
    return pl * b.Box(t, w, d.length, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))


def fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def on_panel(ly, p=PARAMS, lz=None):
    """(y, z) of a point on the panel underside at local slope coordinate ly (mm)."""
    t = math.radians(p["tilt"])
    lz = -p["panel"][2] / 2 if lz is None else lz
    pcy, pcz = p["panel_c"][0], p["z0"] + p["panel_c"][1]
    return pcy + ly * math.cos(t) - lz * math.sin(t), pcz + ly * math.sin(t) + lz * math.cos(t)


def build_parts(p=PARAMS):
    """Return {key: solid} for BOM lines 1 to 12 (line 13, hardware, has no geometry)."""
    b = _b3d()
    D = derived(p)
    ew, ed, eh = p["enc"]
    w, ld = p["enc_wall"], p["lid_d"]
    z0, zc = p["z0"], D["enc_zc"]
    parts = {}

    # 1 enclosure body, open to -Y, with the ePTFE vent on the bottom face
    bd = ed - ld
    ybody = D["enc_back"] - bd / 2
    body = box(0, ybody, zc, ew, bd, eh) - box(0, ybody - w, zc, ew - 2 * w, bd, eh - 2 * w)
    body = body + zcyl(ew / 2 - 17, D["enc_back"] - 18, z0 - 4, p["vent_d"] / 2, 8)
    parts["body"] = body
    # 2 lid
    ylid = D["enc_front"] + ld / 2
    parts["lid"] = box(0, ylid, zc, ew, ld, eh) - box(0, ylid + w, zc, ew - 2 * w, ld, eh - 2 * w)

    # 11 internal plate just inside the back wall, and the parts it carries
    mw, mh, mt = p["mplate"]
    in_back = D["enc_back"] - w
    parts["mplate"] = box(0, in_back - mt / 2, zc, mw, mt, mh)
    mf = in_back - mt
    cd, cl = p["cell"]
    parts["cell"] = zcyl(-38, mf - cd / 2 - 4, z0 + 75, cd / 2, cl) + box(-38, mf - 5, z0 + 75, cd + 6, 10, cl + 10)
    pw_, ph_, pt_ = p["power"]
    parts["power"] = (box(22, mf - pt_ / 2, z0 + 70, pw_, pt_, ph_)
                      + box(30, mf - pt_ - 6, z0 + 62, 22, 12, 18)       # inductor and terminal block
                      + box(5, mf - pt_ - 4, z0 + 82, 14, 8, 10))
    cw, ch, ct = p["ctrl"]
    parts["ctrl"] = box(10, mf - ct / 2, z0 + 150, cw, ct, ch) + box(0, mf - ct - 3, z0 + 150, 24, 6, 20)

    # bottom-face penetrations, on the body's center line in Y
    yb = ybody - 5
    r_in, r_fl = p["m16_d"][0] / 2, p["m16_d"][1] / 2
    parts["glands"] = fuse(zcyl(x, yb, z0 - 9, r_in, 18) + zcyl(x, yb, z0 - 6, r_fl, 6) for x in p["gland_x"])
    r_in, r_fl = p["m12_d"][0] / 2, p["m12_d"][1] / 2
    parts["ports"] = fuse(zcyl(x, yb, z0 - 11, r_in, 22) + zcyl(x, yb, z0 - 8, r_fl, 6) for x in p["port_x"])
    wd, wl = p["whip"]
    parts["antenna"] = (zcyl(p["ant_x"], ybody + 8, z0 - 10, 9, 20)
                        + zcyl(p["ant_x"], ybody + 8, z0 - 20 - wl / 2, wd / 2, wl))

    # 12 pole mounting kit: back plate, two V-blocks and two band clamps on the design pole
    plw, plh, plt = p["plate"]
    plate = box(0, p["plate_y0"] - plt / 2, D["plate_bot"] + plh / 2, plw, plt, plh)
    pr = p["pole_od"] / 2
    vw, vh = p["vblock"]
    depth = D["vblock_depth"]
    kit = plate
    for zz in D["clamps"]:
        vb = box(0, p["plate_y0"] + depth / 2, zz, vw, depth, vh)
        vb = vb - zcyl(0, 0, zz, pr, vh + 2)                         # seat on the pole (massing of the V)
        band = zcyl(0, 0, zz, pr + 2, p["band_w"]) - zcyl(0, 0, zz, pr, p["band_w"] + 2)
        kit = kit + vb + band
    parts["mount"] = kit

    # 4 panel, tilted toward -Y
    pcy, pcz = D["panel_cy"], D["panel_cz"]
    parts["panel"] = b.Pos(0, pcy, pcz) * b.Rot(p["tilt"], 0, 0) * b.Box(*p["panel"])

    # 5 bracket: rear posts and front struts from the back plate to the panel underside
    bw, bt = p["bar"]
    yf = p["plate_y0"] - plt
    members = []
    for x in (-p["bracket_x"], p["bracket_x"]):
        yb_, zb_ = on_panel(p["post_ly"], p)
        ys_, zs_ = on_panel(p["strut_ly"], p)
        members.append(bar((x, yf - bt / 2, z0 + p["post_foot_dz"]), (x, yb_, zb_), bw, bt))
        members.append(bar((x, yf - bt / 2, z0 + p["strut_foot_dz"]), (x, ys_, zs_), bw, bt))
    parts["bracket"] = fuse(members)
    return parts


def build_shield(p=PARAMS):
    """Hot-climate sun shield option (BOM line 14): front, two sides and a top sheet standing off
    the enclosure by shield_gap on all exposed faces; open at the bottom and with a slot at the
    back of the top, so air rises through the gap. Fixed to the back plate. Not in the base node."""
    D = derived(p)
    ew, ed, eh = p["enc"]
    t, g = p["shield_t"], p["shield_gap"]
    yb = p["plate_y0"] - p["plate"][2]                     # front face of the back plate
    yf = D["enc_front"] - g                                # inner face of the front sheet
    xo = ew / 2 + g                                        # inner face of the side sheets
    zlo, zhi = D["enc_bot"] + p["shield_low"], D["enc_top"] + g
    h = zhi - zlo
    front = box(0, yf - t / 2, zlo + h / 2, 2 * (xo + t), t, h)
    sides = [box(sx * (xo + t / 2), (yb + yf - t) / 2, zlo + h / 2, t, yb - (yf - t), h) for sx in (-1, 1)]
    ytop0, ytop1 = yf - t, yb - p["shield_slot"]
    top = box(0, (ytop0 + ytop1) / 2, zhi + t / 2, 2 * (xo + t), ytop1 - ytop0, t)
    return fuse([front, *sides, top])


def shield_geometry(p=PARAMS):
    """Sheet area (m2) and outside size (mm) of the shield, for FND-CAL-001."""
    D = derived(p)
    ew, ed, eh = p["enc"]
    t, g = p["shield_t"], p["shield_gap"]
    w = ew + 2 * (g + t)
    d = (p["plate_y0"] - p["plate"][2]) - (D["enc_front"] - g - t)
    h = eh + g + t - p["shield_low"]
    area = (w * h + 2 * d * h + w * (d - p["shield_slot"])) / 1e6
    return {"w": w, "d": d, "h": h, "area_m2": area, "front_m2": w * h / 1e6, "side_m2": d * h / 1e6}


def bracket_geometry(p=PARAMS):
    """Member lengths (mm) and angles from horizontal (deg) of one side frame, for FND-CAL-001."""
    D = derived(p)
    yf = p["plate_y0"] - p["plate"][2]
    out = {}
    for key, ly, dz in (("post", p["post_ly"], p["post_foot_dz"]), ("strut", p["strut_ly"], p["strut_foot_dz"])):
        y1, z1 = on_panel(ly, p)
        y0, z0 = yf, p["z0"] + dz
        L = math.hypot(y1 - y0, z1 - z0)
        out[key] = {"L": L, "angle": math.degrees(math.atan2(z1 - z0, abs(y1 - y0))), "foot": (y0, z0), "head": (y1, z1)}
    return out


def pole_context(p=PARAMS, length=600.0):
    """Stub of the site pole (grey on the drawing and renders); not in the BOM."""
    return zcyl(0, 0, p["z0"] + 240, p["pole_od"] / 2, length)


def assembly(p=PARAMS, with_pole=False):
    b = _b3d()
    parts = build_parts(p)
    kids = list(parts.values()) + ([pole_context(p)] if with_pole else [])
    return b.Compound(children=kids)


if __name__ == "__main__":
    from build123d import Compound, export_step, export_stl
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True)
    (out / "stl").mkdir(exist_ok=True)
    P = build_parts()
    groups = {
        "fieldnode-assembly": list(P.values()) + [pole_context()],
        "fieldnode-core": [P[k] for k in ("body", "lid", "glands", "ports", "antenna", "mplate", "cell", "power", "ctrl")],
        "fieldnode-mount": [P[k] for k in ("mount", "bracket")],
        "fieldnode-shield": [build_shield()],
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
    sg = shield_geometry()
    print(f"sun shield option: {sg['w']:.0f} x {sg['d']:.0f} x {sg['h']:.0f} mm, sheet {sg['area_m2']:.4f} m2")
    for k, v in bracket_geometry().items():
        print(f"bracket {k}: {v['L']:.0f} mm at {v['angle']:.0f} deg")
