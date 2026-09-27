"""FieldNode product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: the light grey IP65 enclosure with filleted corners,
side ribs, a parting line with the dark lid gasket showing, four captive lid screws, a clear
window in the lid showing the controller and LoRa module with its lit green status light, a lid
label with port markings, two M12 sensor sockets (one capped, one with a sensor plug), two M16
glands (panel lead and blanked), the ePTFE vent, the whip antenna on its bulkhead; the 6 W panel
with an aluminium frame, cell grid and junction box on the flat-bar bracket with its angle clips
and bolts; and the pole kit (back plate with keyhole slots, 90 deg V-blocks, stainless band clamps
with worm housings). Inside: the ASA mounting plate, the LiFePO4 cell in its fused holder, the
power board and the controller carrier (illustrative envelopes from model.py). Context is a short
section of the 48.3 mm design pole, the panel lead and a sensor cable tied to the pole.
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every main dimension and interface comes from PARAMS, derived(), build_parts() and on_panel() in
model.py, with the same axes: the pole is the Z axis, Z is up with the ground at z = 0 and the node
faces -Y. Differences from model.py (lid window, vent position) are recorded in docs/REVIEW.md
(session 2026-09-26) as proposed, awaiting Amish.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Align, Axis, Box, Cylinder, Plane, Pos, RegularPolygon, Rot, Solid, Sphere, Text,
                       Vector, extrude, fillet)
from model import PARAMS, derived, build_parts, on_panel

_FONT = Path(__file__).resolve().parents[2] / ".kit" / "fonts" / "IBMPlexSans-SemiBold.ttf"

TITLE = "FieldNode: solar-powered outdoor sensor node core"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "context"], "explode": False, "el": 30, "az": -40,
     "note": "Product render from the front right and above (about 30 deg elevation); 6 W panel over the "
             "enclosure on a short section of pole, controller and lit status light behind the lid window, "
             "M12 sensor ports and whip antenna underneath"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): panel and bracket above; "
             "lid, gasket and enclosure base at centre; mounting plate, LiFePO4 cell, power board, controller "
             "and LoRa module at right; ports, glands and antenna below; pole kit behind"},
    {"name": "detail", "groups": ["shell", "internal"], "explode": False, "el": 8, "az": -32,
     "note": "Detail from the front right, just above the enclosure base (about 8 deg elevation), without the "
             "pole: lid label and window, M12 sensor ports A (open) and B (capped), glands, vent and antenna"},
]

# Colours (restrained product palette, shared with the other FieldNode renders; kit accent)
C_SHELL = "#DADDE1"      # light grey polycarbonate
C_LID = "#E6E8EB"
C_DARK = "#2B2F36"
C_BLACK = "#1C1F24"
C_ACCENT = "#0F766E"
C_ALU = "#C3C8CE"
C_ALU2 = "#AEB4BB"
C_STEEL = "#9CA3AB"
C_CELLS = "#1B2735"
C_GRID = "#C9CDD3"
C_PCB = "#166534"
C_PCB_DARK = "#14532D"
C_CHIP = "#111827"
C_CELL = "#2F4F6F"
C_ASA = "#3A3F47"
C_WINDOW = "#DCEBF5"
C_LABEL = "#F4F4F2"
C_LED_G = "#22C55E"
C_POLE = "#A7ADB4"
C_CABLE = "#23272D"
C_DESICCANT = "#E9E4D4"

# Appearance-only positions (mm)
VENT_XY = (30.0, -63.0)  # moved from model.py (58, -63), which overlaps the antenna bulkhead; see REVIEW
POLE_Z = (1560.0, 2250.0)


def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _box(cx, cy, cz, sx, sy, sz):
    return Pos(cx, cy, cz) * Box(sx, sy, sz)


def _bx(x0, x1, y0, y1, z0, z1):
    return _box((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0)


def _zcyl(x, y, z, r, h):
    return Pos(x, y, z) * Cylinder(r, h)


def _ycyl(x, y, z, r, h):
    return Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(r, h)


def _xcyl(x, y, z, r, h):
    return Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(r, h)


def _rod(a, c, r):
    a, c = Vector(*a), Vector(*c)
    d = c - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


def _pipe(points, r):
    """Round cable through `points` with spherical joints."""
    out = None
    for a, c in zip(points, points[1:]):
        seg = _rod(a, c, r)
        out = seg if out is None else out + seg
    for q in points[1:-1]:
        out += Pos(*q) * Sphere(r)
    return out


def _bezier(p0, p1, p2, p3, n=8):
    """Points along a cubic Bezier from p0 to p3 (for smooth cable bends)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * d
                         for a, b, c, d in zip(p0, p1, p2, p3)))
    return pts


def _hex_z(x, y, z, af, h):
    return Pos(x, y, z - h / 2) * extrude(RegularPolygon(af / 1.732, 6), amount=h)


def _hex_x(x, y, z, af, h):
    return Pos(x - h / 2, y, z) * extrude(Plane.YZ * RegularPolygon(af / 1.732, 6), amount=h)


def _hex_y(x, y, z, af, h):
    return Pos(x, y - h / 2, z) * extrude(Plane.XZ * RegularPolygon(af / 1.732, 6), amount=-h)


def _fmin(s, axis):
    return s.faces().sort_by(axis)[0].edges()


def _fmax(s, axis):
    return s.faces().sort_by(axis)[-1].edges()


def _text_ny(txt, size, x, y, z, h=0.3):
    """Raised text on a face that looks toward -Y, centred on (x, z)."""
    t = extrude(Text(txt, font_size=size, font_path=str(_FONT), align=(Align.CENTER, Align.CENTER)), amount=h)
    pl = Plane(origin=(x, y, z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return pl * t


def _union(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def _knurl_cap(x, y, z_top, r, h, n=18, groove=0.8):
    """Knurled round cap hanging below z_top (vertical grooves round the rim)."""
    cap = _zcyl(x, y, z_top - h / 2, r, h)
    cap = _fillet_try(cap, _fmin(cap, Axis.Z), [1.2, 0.8, 0.5])
    for k in range(n):
        a = 2 * math.pi * k / n
        cap -= _box(x + r * math.cos(a), y + r * math.sin(a), z_top - h / 2 - 1.0, groove, groove, h - 3.0)
    return cap


def product_parts(P=PARAMS):
    D = derived(P)
    model = build_parts(P)
    out = []

    def add(name, shape, color, material, bom, group, explode):
        out.append({"name": name, "shape": shape, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(float(v) for v in explode)})

    ew, ed, eh = P["enc"]
    wt = P["enc_wall"]
    z0 = P["z0"]
    zc = D["enc_zc"]
    y_back, y_front = D["enc_back"], D["enc_front"]        # -45 (on the back plate) and -135 (lid face)
    ys = y_front + P["lid_d"]                               # parting line, as model.py
    ybody = y_back - (ed - P["lid_d"]) / 2
    yb = ybody - 5                                          # port and gland line, as model.py
    ya = ybody + 8                                          # antenna bulkhead line, as model.py
    R = P["pole_od"] / 2

    E_BODY = (0, 0, 0)
    E_GASKET = (0, -120, 0)
    E_LID = (0, -230, 0)
    E_DOWN = (0, 0, -80)
    E_PAN = (0, 60, 330)
    E_BRK = (0, 30, 170)
    E_MOUNT = (0, 170, 150)
    E_CELL = (190, -60, -80)
    E_PWR = (290, -80, -70)
    E_IN = (300, 40, -30)

    # ------------------------------------------------------------ enclosure body (BOM 1)
    outer = _bx(-ew / 2, ew / 2, y_front, y_back, z0, z0 + eh)
    outer = _fillet_try(outer, outer.edges().filter_by(Axis.Y), [9.0, 7.0, 5.0])
    outer = _fillet_try(outer, _fmin(outer, Axis.Y), [3.0, 2.0, 1.0])
    body = outer & _bx(-200, 200, ys + 0.3, y_back + 1, z0 - 10, z0 + eh + 10)
    body -= _bx(-ew / 2 + wt, ew / 2 - wt, ys, y_back - wt, z0 + wt, z0 + eh - wt)
    for sx in (-1, 1):                                      # vertical side ribs (texture)
        for k in range(5):
            body -= _box(sx * ew / 2, ys + 14 + 11 * k, zc, 1.6, 3.0, eh - 50)
    for sx in (-1, 1):                                      # lid screw bosses at the parting line
        for sz in (-1, 1):
            x, z = sx * (ew / 2 - 11), zc + sz * (eh / 2 - 11)
            body += _ycyl(x, ys + 10, z, 5.0, 20.0) - _ycyl(x, ys + 10, z, 1.6, 22.0)
    for x in P["port_x"]:                                   # holes in the bottom face
        body -= _zcyl(x, yb, z0 + wt / 2, P["m12_d"][0] / 2, wt + 2)
    for x in P["gland_x"]:
        body -= _zcyl(x, yb, z0 + wt / 2, P["m16_d"][0] / 2, wt + 2)
    body -= _zcyl(P["ant_x"], ya, z0 + wt / 2, 6.0, wt + 2)
    body -= _zcyl(VENT_XY[0], VENT_XY[1], z0 + wt / 2, 6.0, wt + 2)
    add("Enclosure base (IP65 polycarbonate)", body, C_SHELL, "plastic", 1, "shell", E_BODY)

    # ------------------------------------------------------------ lid (BOM 2), window, gasket, screws
    lid = outer & _bx(-200, 200, y_front - 1, ys - 0.3, z0 - 10, z0 + eh + 10)
    lid -= _bx(-ew / 2 + wt, ew / 2 - wt, y_front + wt, ys, z0 + wt, z0 + eh - wt)
    wx0, wx1, wz0, wz1 = -48.0, 48.0, z0 + 118.0, z0 + 176.0
    win = _bx(wx0, wx1, y_front - 1, y_front + wt + 1, wz0, wz1)
    win = _fillet_try(win, win.edges().filter_by(Axis.Y), [6.0, 4.0])
    lid -= win
    lid -= _ycyl(56.0, y_front + wt / 2, z0 + 14.0, 2.6, wt + 2)             # status light pipe hole
    add("Enclosure lid (polycarbonate)", lid, C_LID, "plastic", 2, "shell", E_LID)
    pane = _bx(wx0 - 3, wx1 + 3, y_front + wt, y_front + wt + 1.5, wz0 - 3, wz1 + 3)
    pane = _fillet_try(pane, pane.edges().filter_by(Axis.Y), [8.0, 6.0])
    add("Lid window (clear polycarbonate)", pane, C_WINDOW, "clear", 2, "shell", E_LID)
    bez = _bx(wx0 - 4, wx1 + 4, y_front - 0.8, y_front, wz0 - 4, wz1 + 4)
    bez = _fillet_try(bez, bez.edges().filter_by(Axis.Y), [9.0, 7.0])
    bez -= _bx(wx0, wx1, y_front - 3, y_front + 1, wz0, wz1)
    add("Lid window trim", bez, C_DARK, "plastic", 2, "shell", E_LID)

    gasket = (_bx(-ew / 2 + 1.0, ew / 2 - 1.0, ys - 0.3, ys + 0.3, z0 + 1.0, z0 + eh - 1.0)
              - _bx(-ew / 2 + wt, ew / 2 - wt, ys - 1, ys + 1, z0 + wt, z0 + eh - wt))
    gasket = _fillet_try(gasket, gasket.edges().filter_by(Axis.Y), [7.0, 5.0, 2.0])
    add("Lid gasket (EPDM)", gasket, C_BLACK, "rubber", 2, "shell", E_GASKET)

    scr = None
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * (ew / 2 - 11), zc + sz * (eh / 2 - 11)
            s = _ycyl(x, y_front - 0.6, z, 3.4, 1.2)
            s = _fillet_try(s, _fmin(s, Axis.Y), [0.5, 0.3])
            s -= _box(x, y_front - 1.2, z, 4.0, 1.0, 0.8)
            s -= _box(x, y_front - 1.2, z, 0.8, 1.0, 4.0)
            scr = s if scr is None else scr + s
    add("Captive lid screws (stainless)", scr, C_STEEL, "metal", 2, "shell", (0, -270, 0))

    # lid label (thin raised parts) below the window, port markings above the ports
    ly = y_front - 0.2
    lz = z0 + 66.0
    add("Lid label", _box(0, ly, lz, 112, 0.4, 70), C_LABEL, "paper", 2, "shell", E_LID)
    add("Lid label accent band", _box(0, ly - 0.3, lz + 27, 112, 0.3, 12), C_ACCENT, "painted", 2, "shell", E_LID)
    ink = _text_ny("FieldNode", 13.0, 0, ly - 0.2, lz + 5)
    ink += _text_ny("SOLAR LORAWAN SENSOR NODE", 5.2, 0, ly - 0.2, lz - 11)
    ink += _text_ny("2 x M12 SENSOR PORTS  ·  100 mW", 4.4, 0, ly - 0.2, lz - 21)
    ink += _box(0, ly - 0.35, lz - 29, 90, 0.3, 1.0)
    add("Lid label print", ink, C_DARK, "paper", 2, "shell", E_LID)
    add("Lid label band text", _text_ny("OPEN HARDWARE CORE", 6.0, 0, ly - 0.4, lz + 27, h=0.2), C_LABEL, "paper", 2,
        "shell", E_LID)
    marks = None
    for x, t in zip(P["port_x"], ("A", "B")):
        m = _text_ny(t, 8.0, x, y_front - 0.1, z0 + 14, h=0.4)
        m += _box(x, y_front - 0.3, z0 + 6.5, 6.0, 0.4, 1.2)
        marks = m if marks is None else marks + m
    add("Port markings A and B", marks, C_ACCENT, "painted", 2, "shell", E_LID)

    # status light pipe on the lid, lit from the controller's LED
    lx_, lz_ = 56.0, z0 + 14.0
    lbez = _ycyl(lx_, y_front - 0.8, lz_, 4.5, 1.6) - _ycyl(lx_, y_front - 0.8, lz_, 2.6, 3.0)
    add("Status light bezel", lbez, C_DARK, "plastic", 2, "shell", E_LID)
    dome = Pos(lx_, y_front + 0.4, lz_) * Sphere(3.0) & _bx(lx_ - 5, lx_ + 5, y_front - 2.6, y_front + wt, lz_ - 5, lz_ + 5)
    add("Status light pipe, green (lit)", dome, C_LED_G, "emissive", 8, "shell", E_LID)

    # ------------------------------------------------------------ bottom face: ports, glands, vent, antenna
    socks, caps, inserts = None, None, None
    for i, x in enumerate(P["port_x"]):
        s = _hex_z(x, yb, z0 - 2.0, P["m12_d"][1], 4.0)                    # panel nut against the base
        s += _zcyl(x, yb, z0 - 4.0 - 9.0, P["m12_d"][0] / 2, 18.0)           # threaded barrel, to z0 - 22
        s -= _zcyl(x, yb, z0 - 21.0, 5.6, 4.0)
        socks = s if socks is None else socks + s
        ins = _zcyl(x, yb, z0 - 20.5, 5.6, 3.0)
        for k in range(5):
            a = 2 * math.pi * k / 4 if k < 4 else 0.0
            rr = 3.0 if k < 4 else 0.0
            ins -= _zcyl(x + rr * math.cos(a + 0.785), yb + rr * math.sin(a + 0.785), z0 - 22.0, 0.6, 2.0)
        inserts = ins if inserts is None else inserts + ins
        if i == 1:                                                            # port B capped
            c = _knurl_cap(x, yb, z0 - 8.0, 10.0, 17.0)
            caps = c
    add("M12 sensor sockets (ports A and B)", socks, C_STEEL, "metal", 10, "shell", E_DOWN)
    add("M12 socket inserts", inserts, C_BLACK, "plastic", 10, "shell", E_DOWN)
    add("M12 sealing cap (port B)", caps, C_DARK, "rubber", 10, "shell", (0, 0, -120))
    tether = _pipe([(P["port_x"][1] + 9.5, yb, z0 - 14), (P["port_x"][1] + 12, yb - 4, z0 - 5),
                    (P["port_x"][1] + 12, yb - 4, z0 - 1.5)], 0.9)
    add("M12 cap tether", tether, C_DARK, "rubber", 10, "shell", (0, 0, -120))

    gl = None
    for k, x in enumerate(P["gland_x"]):
        g = _hex_z(x, yb, z0 - 3.0, P["m16_d"][1], 6.0)
        dome = _zcyl(x, yb, z0 - 12.0, 9.5, 12.0)
        dome = _fillet_try(dome, _fmin(dome, Axis.Z), [3.0, 2.0])
        for j in range(6):
            a = math.pi * j / 3
            dome -= _box(x + 9.5 * math.cos(a), yb + 9.5 * math.sin(a), z0 - 12.0, 1.2, 1.2, 8.0)
        g += dome
        gl = g if gl is None else gl + g
    add("M16 cable glands (panel lead, blanked)", gl, C_BLACK, "plastic", 3, "shell", E_DOWN)

    vx, vy = VENT_XY
    vent = _zcyl(vx, vy, z0 - 1.5, 6.5, 3.0)
    vcap = _zcyl(vx, vy, z0 - 7.0, P["vent_d"] / 2, 5.0)
    vcap = _fillet_try(vcap, _fmin(vcap, Axis.Z), [2.0, 1.2])
    add("ePTFE pressure vent", vent + vcap, C_DARK, "plastic", 1, "shell", E_DOWN)

    wd, wl = P["whip"]
    ax = P["ant_x"]
    base = _hex_z(ax, ya, z0 - 2.5, 16.0, 5.0) + _zcyl(ax, ya, z0 - 12.5, 7.5, 15.0)
    base = _fillet_try(base, _fmin(base, Axis.Z), [1.5, 1.0])
    base += _zcyl(ax, ya, z0 - 20 + 1.0, 9.0, 2.0)                           # bulkhead collar, model.py r = 9
    add("Antenna bulkhead and base", base, C_STEEL, "metal", 9, "shell", E_DOWN)
    whip = _zcyl(ax, ya, z0 - 20 - wl / 2, wd / 2, wl)
    whip = _fillet_try(whip, _fmin(whip, Axis.Z), [4.0, 2.5])
    whip += _zcyl(ax, ya, z0 - 20 - 5.0, wd / 2 + 0.8, 10.0)
    add("Whip antenna (sub-GHz)", whip, C_BLACK, "rubber", 9, "shell", (0, 0, -150))

    # ------------------------------------------------------------ inside (BOM 6, 7, 8, 11), model.py envelopes
    mw, mh, mt = P["mplate"]
    in_back = y_back - wt
    mf = in_back - mt
    mp = _bx(-mw / 2, mw / 2, mf, in_back, zc - mh / 2, zc + mh / 2)
    mp = _fillet_try(mp, mp.edges().filter_by(Axis.Y), [6.0, 4.0])
    for x, z in ((-52, zc - 78), (52, zc - 78), (-52, zc + 78), (52, zc + 78)):
        mp -= _ycyl(x, (mf + in_back) / 2, z, 2.5, mt + 2)
    mp -= _bx(-10, 10, mf - 1, in_back + 1, zc + 70, zc + 84)                # lift-out grip slot
    add("Internal mounting plate (ASA)", mp, C_ASA, "plastic", 11, "internal", E_IN)

    cd, cl = P["cell"]
    cy_ = mf - cd / 2 - 4
    cz_ = z0 + 75
    cell = _zcyl(-38, cy_, cz_, cd / 2, cl - 4)
    cell = _fillet_try(cell, cell.edges(), [1.5, 1.0])
    add("LiFePO4 cell (32700, 6 Ah)", cell, C_CELL, "painted", 6, "internal", E_CELL)
    term = _zcyl(-38, cy_, cz_ + cl / 2 - 1.2, cd / 2 - 2, 2.4) + _zcyl(-38, cy_, cz_ - cl / 2 + 1.2, cd / 2 - 2, 2.4)
    term += _zcyl(-38, cy_, cz_ + cl / 2 + 0.8, 4.0, 1.6)
    add("Cell terminals", term, C_ALU, "metal", 6, "internal", E_CELL)
    holder = _bx(-38 - (cd + 6) / 2, -38 + (cd + 6) / 2, mf - 10, mf, cz_ - (cl + 10) / 2, cz_ + (cl + 10) / 2)
    holder -= _zcyl(-38, cy_, cz_, cd / 2 + 0.3, cl + 4)
    holder = _fillet_try(holder, holder.edges().filter_by(Axis.Y), [2.0, 1.0])
    for dz in (-20, 20):                                                     # retaining straps round the cell
        holder += _zcyl(-38, cy_, cz_ + dz, cd / 2 + 1.2, 6.0) - _zcyl(-38, cy_, cz_ + dz, cd / 2, 8.0)
    add("Fused cell holder", holder, C_DARK, "plastic", 6, "internal", E_CELL)
    fuse_ = _bx(-38 - 5, -38 + 5, mf - 14, mf - 6, cz_ + cl / 2 + 8, cz_ + cl / 2 + 22)
    fuse_ = _fillet_try(fuse_, fuse_.edges(), [1.0, 0.5])
    add("Inline fuse holder", fuse_, "#B91C1C", "plastic", 6, "internal", E_CELL)

    pw_, ph_, pt_ = P["power"]
    pcb_t = 1.6
    py0 = mf - 3.0                                                           # standoff gap
    pcb = _bx(22 - pw_ / 2, 22 + pw_ / 2, py0 - pcb_t, py0, z0 + 70 - ph_ / 2, z0 + 70 + ph_ / 2)
    pcb = _fillet_try(pcb, pcb.edges().filter_by(Axis.Y), [2.0, 1.0])
    add("Power board PCB (MPPT, protection)", pcb, C_PCB, "plastic", 7, "internal", E_PWR)
    pf = py0 - pcb_t
    pc = _bx(30 - 11, 30 + 11, mf - pt_ - 12, pf, z0 + 62 - 9, z0 + 62 + 9)  # inductor, model.py envelope
    pc = _fillet_try(pc, pc.edges().filter_by(Axis.Y), [2.0, 1.0])
    pc += _bx(-4, 6, pf - 2.0, pf, z0 + 80, z0 + 90) + _bx(40, 52, pf - 1.5, pf, z0 + 82, z0 + 92)
    pc += _bx(-12, -2, pf - 1.2, pf, z0 + 50, z0 + 58) + _bx(50, 58, pf - 3, pf, z0 + 48, z0 + 56)
    pc += _ycyl(8, pf - 6, z0 + 56, 4.0, 12.0)                               # capacitor
    add("Power board components", pc, C_CHIP, "plastic", 7, "internal", E_PWR)
    tb = _bx(5 - 7, 5 + 7, mf - pt_ - 8, pf, z0 + 82 - 5, z0 + 82 + 5)       # terminal block, model.py envelope
    add("Power board terminal block", tb, "#2E7D5B", "plastic", 7, "internal", E_PWR)

    cw, ch, ct = P["ctrl"]
    cpcb = _bx(10 - cw / 2, 10 + cw / 2, py0 - pcb_t, py0, z0 + 150 - ch / 2, z0 + 150 + ch / 2)
    cpcb = _fillet_try(cpcb, cpcb.edges().filter_by(Axis.Y), [2.0, 1.0])
    E_CTRL = (E_IN[0] + 20, E_IN[1] - 170, E_IN[2] + 10)
    add("Controller carrier PCB", cpcb, C_PCB_DARK, "plastic", 8, "internal", E_CTRL)
    cf = py0 - pcb_t
    mod = _bx(-12, 12, mf - ct - 6, cf, z0 + 140, z0 + 160)                  # LoRa module, model.py envelope
    add("LoRa module (STM32WL class)", mod, C_CHIP, "plastic", 8, "internal", (E_CTRL[0], E_CTRL[1] - 40, E_CTRL[2]))
    can = _bx(-10.5, 10.5, mf - ct - 7, mf - ct - 6, z0 + 141.5, z0 + 158.5)
    add("LoRa module shield can", can, C_ALU, "metal", 8, "internal", (E_CTRL[0], E_CTRL[1] - 40, E_CTRL[2]))
    cc = _bx(22, 32, cf - 1.2, cf, z0 + 150, z0 + 160) + _bx(32, 40, cf - 1.2, cf, z0 + 138, z0 + 146)
    cc += _bx(18, 38, cf - 2.5, cf, z0 + 132, z0 + 137)                      # SPI flash and connector
    cc += _ycyl(-18, cf - 1.0, z0 + 162, 1.6, 2.0)                           # u.FL
    add("Controller components", cc, C_CHIP, "plastic", 8, "internal", E_CTRL)
    led = _bx(36, 40, cf - 1.4, cf, z0 + 164, z0 + 167)
    add("Status light, green (lit)", led, C_LED_G, "emissive", 8, "internal", E_CTRL)
    pig = _pipe(_bezier((-18, cf - 2, z0 + 162), (-18, -84, z0 + 150), (P["ant_x"], -84, z0 + 60),
                        (P["ant_x"], ya, z0 + wt + 1), n=10), 1.0)
    add("Antenna pigtail", pig, C_CABLE, "rubber", 9, "internal", E_CTRL)

    des = _bx(40, 62, mf - 6, mf, z0 + 108, z0 + 128)
    des = _fillet_try(des, des.edges(), [1.5, 1.0])
    add("Desiccant pack", des, C_DESICCANT, "fabric", 13, "internal", (E_IN[0] + 60, E_IN[1] - 60, E_IN[2] + 40))

    # ------------------------------------------------------------ solar panel (BOM 4)
    pw, pl, pt = P["panel"]
    pan = Pos(0, D["panel_cy"], D["panel_cz"]) * Rot(P["tilt"], 0, 0)
    frame = Box(pw, pl, pt)
    frame = _fillet_try(frame, frame.edges().filter_by(Axis.Z), [5.0, 3.0])
    frame -= Pos(0, 0, pt / 2 - 2) * Box(pw - 14, pl - 14, 5)
    frame -= Pos(0, 0, -pt / 2 + 6) * Box(pw - 8, pl - 8, 12.02)
    add("Solar panel frame (anodized aluminium)", pan * frame, C_ALU, "metal", 4, "shell", E_PAN)
    lam = Pos(0, 0, pt / 2 - 3.2) * Box(pw - 14, pl - 14, 2.4)
    lam = lam + Pos(0, 0, -pt / 2 + 11.5) * Box(pw - 8, pl - 8, 1.0)
    add("Solar cells (6 W monocrystalline)", pan * lam, C_CELLS, "screen", 4, "shell", E_PAN)
    grid = None
    zt = pt / 2 - 1.85
    for k in range(1, 6):
        g = Pos(-(pw - 14) / 2 + k * (pw - 14) / 6, 0, zt) * Box(0.9, pl - 16, 0.3)
        grid = g if grid is None else grid + g
    for k in range(1, 4):
        grid += Pos(0, -(pl - 14) / 2 + k * (pl - 14) / 4, zt) * Box(pw - 16, 0.9, 0.3)
    add("Solar cell grid lines", pan * grid, C_GRID, "metal", 4, "shell", E_PAN)
    JX, JLY = 110.0, 30.0
    jb = Pos(JX, JLY, -pt / 2 + 11.0 - 6.0) * Box(40, 40, 10)
    jb = _fillet_try(jb, jb.edges().filter_by(Axis.Z), [3.0, 2.0])
    add("Panel junction box", pan * jb, C_BLACK, "plastic", 4, "shell", E_PAN)
    add("Panel badge", pan * (Pos(-pw / 2 + 40, -pl / 2 + 3.5, pt / 2 - 0.1) * Box(40, 3.0, 0.4)), C_ACCENT,
        "painted", 4, "shell", E_PAN)

    # ------------------------------------------------------------ bracket (BOM 5): model.py bars, clips, bolts
    brk = model["bracket"]
    add("Panel tilt bracket (aluminium flat bar)", brk, C_ALU2, "metal", 5, "shell", E_BRK)
    bw, bt = P["bar"]
    yf = P["plate_y0"] - P["plate"][2]
    clips, bolts = None, None
    for sx in (-1, 1):
        x = sx * P["bracket_x"]
        for ly, dz in ((P["post_ly"], P["post_foot_dz"]), (P["strut_ly"], P["strut_foot_dz"])):
            a = Vector(x, yf - bt / 2, z0 + dz)
            hy, hz = on_panel(ly, P)
            d = (Vector(x, hy, hz) - a).normalized()
            p = a + d * 16.0
            xi = x - sx * (bt / 2 + 1.5)                                     # clip leg beside the bar, inboard
            leg = _box(xi, (yf + p.Y - 10) / 2, p.Z, 3.0, yf - (p.Y - 10), 24.0)
            foot = _box(x - sx * 8.0, yf - 1.5, p.Z, 16.0, 3.0, 24.0)
            c = leg + foot
            c = _fillet_try(c, c.edges().filter_by(Axis.X), [1.0, 0.5])
            clips = c if clips is None else clips + c
            b = _hex_x(x + sx * (bt / 2 + 2.0), p.Y, p.Z, 10.0, 4.0)
            b += _xcyl(xi - sx * 2.5, p.Y, p.Z, 5.0, 2.0)                    # washer face on the clip
            bolts = b if bolts is None else bolts + b
            # panel end: small tab and bolt on the frame underside
            hp = pan * Pos(x, ly, -pt / 2 - 4.0) * Box(3.0, 30.0, 8.0)
            clips += hp
            bolts += pan * (Pos(x + sx * 3.5, ly, -pt / 2 - 4.0) * Rot(0, 90, 0) * Cylinder(4.5, 4.0))
    add("Bracket angle clips", clips, C_ALU2, "metal", 5, "shell", E_BRK)
    add("M6 bracket bolts", bolts, C_STEEL, "metal", 13, "shell", (E_BRK[0], E_BRK[1], E_BRK[2]))

    # ------------------------------------------------------------ pole mounting kit (BOM 12)
    plw, plh, plt = P["plate"]
    pb_, ptop_ = D["plate_bot"], D["plate_top"]
    plate = _bx(-plw / 2, plw / 2, P["plate_y0"] - plt, P["plate_y0"], pb_, ptop_)
    plate = _fillet_try(plate, plate.edges().filter_by(Axis.Y), [10.0, 8.0, 5.0])
    for x in (-plw / 2 + 14, plw / 2 - 14):                                  # wall-mount keyhole slots
        for z in (pb_ + 16, ptop_ - 16):
            plate -= _ycyl(x, P["plate_y0"] - plt / 2, z, 4.5, plt + 2)
            plate -= _box(x, P["plate_y0"] - plt / 2, z + 6, 5.0, plt + 2, 12.0)
    for z in D["clamps"]:                                                    # band slots
        for sx in (-1, 1):
            plate -= _box(sx * 33, P["plate_y0"] - plt / 2, z, 6.0, plt + 2, P["band_w"] + 2)
    add("Back plate (aluminium)", plate, C_ALU, "metal", 12, "shell", E_MOUNT)

    vw, vh = P["vblock"]
    depth = D["vblock_depth"]
    vy0, vy1 = P["plate_y0"], P["plate_y0"] + depth
    vbs = None
    apex = -R * math.sqrt(2)                                                 # 90 deg V touching the pole
    for z in D["clamps"]:
        vb = _bx(-vw / 2, vw / 2, vy0, vy1, z - vh / 2, z + vh / 2)
        vb = _fillet_try(vb, vb.edges().filter_by(Axis.Y), [3.0, 2.0])
        vcut = Pos(0, apex, z) * Rot(0, 0, 45) * Box(80, 80, vh + 2, align=(Align.MIN, Align.MIN, Align.CENTER))
        vb -= vcut
        vbs = vb if vbs is None else vbs + vb
    add("V-blocks (aluminium)", vbs, C_ALU2, "metal", 12, "shell", (0, 210, 150))

    bands, heads = None, None
    band_w = P["band_w"]
    for z in D["clamps"]:
        ring = _zcyl(0, 0, z, R + 1.0, band_w) - _zcyl(0, 0, z, R, band_w + 2)
        ring &= _bx(-40, 40, -R * 0.7, 40, z - 10, z + 10)
        xs = R * math.sqrt(1 - 0.49) + 0.5
        run = None
        for sx in (-1, 1):
            r_ = _bx(sx * xs - 0.5, sx * xs + 0.5, P["plate_y0"] - plt - 1.0, -R * 0.7 + 0.5, z - band_w / 2, z + band_w / 2)
            run = r_ if run is None else run + r_
        front = _bx(-xs - 0.5, xs + 0.5, P["plate_y0"] - plt - 1.0, P["plate_y0"] - plt, z - band_w / 2, z + band_w / 2)
        hous = _box(0, P["plate_y0"] - plt - 6.0, z, 16, 10, band_w + 4)
        hous = _fillet_try(hous, hous.edges().filter_by(Axis.Z), [2.0, 1.0])
        c = ring + run + front + hous
        bands = c if bands is None else bands + c
        h = _hex_x(8 + 2.0, P["plate_y0"] - plt - 6.0, z, 8.0, 4.0) + _xcyl(8 + 0.5, P["plate_y0"] - plt - 6.0, z, 3.0, 1.0)
        heads = h if heads is None else heads + h
    add("Stainless band clamps", bands, C_STEEL, "metal", 12, "shell", (0, 250, 150))
    add("Band clamp worm screws", heads, C_ALU2, "metal", 12, "shell", (0, 250, 150))

    # ------------------------------------------------------------ context (not in the BOM)
    pz0, pz1 = POLE_Z
    pole = _zcyl(0, 0, (pz0 + pz1) / 2, R, pz1 - pz0)
    pole = _fillet_try(pole, _fmin(pole, Axis.Z), [1.0, 0.5])
    add("Site pole section (48.3 mm galvanized)", pole, C_POLE, "metal", None, "context", (0, 0, 0))
    pcap = _zcyl(0, 0, pz1 + 6, R + 1.5, 12.0)
    pcap = _fillet_try(pcap, _fmax(pcap, Axis.Z), [5.0, 3.0])
    add("Pole cap", pcap, C_DARK, "plastic", None, "context", (0, 0, 0))

    # panel lead: gland 1 down, back behind the antenna, up the right side to the junction box
    gx = P["gland_x"][0]
    jy, jz = on_panel(JLY - 20.0, P, lz=-pt / 2 - 8.0)
    pts = _bezier((gx, yb, z0 - 17), (gx, yb, z0 - 50), (40, -54, z0 - 45), (70, -54, z0 - 40))
    pts += _bezier((70, -54, z0 - 40), (88, -54, z0 - 38), (88, -54, z0 - 30), (88, -54, z0 - 5))[1:]
    pts += [(88, -54, z0 + 200)]
    pts += _bezier((88, -54, z0 + 200), (88, -54, z0 + 260), (JX, jy + 10, jz - 40), (JX, jy, jz))[1:]
    lead = _pipe(pts, 3.0)
    add("Panel lead", lead, C_CABLE, "rubber", 4, "context", (0, 0, 0))
    # sensor cable: M12 plug in port A, down and tied to the pole
    px_ = P["port_x"][0]
    plug = _knurl_cap(px_, yb, z0 - 10.0, 9.5, 16.0, n=16)
    plug += _zcyl(px_, yb, z0 - 36.0, 7.0, 20.0)
    plug = _fillet_try(plug, _fmin(plug, Axis.Z), [3.0, 2.0])
    add("Sensor plug (M12, port A)", plug, C_BLACK, "plastic", None, "context", (0, 0, 0))
    pts = _bezier((px_, yb, z0 - 46), (px_, yb, z0 - 110), (-12, -27.5, z0 - 90), (-12, -27.5, z0 - 150), n=10)
    scab = _pipe(pts + [(-12, -27.5, pz0 + 2)], 3.0)
    add("Sensor cable", scab, C_CABLE, "rubber", None, "context", (0, 0, 0))
    tz = z0 - 165
    ties = _zcyl(0, 0, tz, R + 7.5, 3.5) - _zcyl(0, 0, tz, R, 5.0)
    ties += _box(-12, -R - 8.5, tz, 5, 4, 6)
    add("Cable tie", ties, C_BLACK, "plastic", 13, "context", (0, 0, 0))
    return out


if __name__ == "__main__":
    for p in product_parts():
        s = p["shape"]
        print(f"{p['name']:42s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:8.2f} cm3")
