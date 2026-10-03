"""FieldNode product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: the light grey IP65 enclosure with filleted corners,
side ribs, a parting line with the dark lid gasket showing, four captive lid screws, a clear
window in the lid showing the controller and LoRa module with its lit green status light, a lid
label with port markings, two M12 sensor sockets (one capped, one with a sensor plug), two M16
glands (panel lead and blanked), the ePTFE vent, the whip antenna on its bulkhead; the 6 W panel
with an aluminium frame, cell grid and junction box on the bracket of the constructable design
(angle clips on the back plate and on the panel frame's back lip, flat-bar posts and struts, M6
bolts); and the pole kit (back plate with its window, band slots and fixing holes, four enclosure
lugs, 90 deg V-blocks, stainless band clamps through the plate slots). Inside: the ASA mounting
plate, the LiFePO4 cell in its fused holder, the power board with its serial programming header,
the controller carrier and the plug-in connector strip (envelopes from model.py). Context is a short
section of the 48.3 mm design pole, the panel lead and a sensor cable tied to the pole.
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every main dimension and interface comes from PARAMS, derived(), build_components() and on_panel()
in model.py, with the same axes: the pole is the Z axis, Z is up with the ground at z = 0 and the
node faces -Y. The mount, bracket, lugs, bands, internal plate, programming header and connector
strip are the model.py solids themselves. Updated 2026-10-02 to the constructable design
(FND-DDR-003) and the 2026-10-02 decisions (FND-DEC-001). Remaining differences from model.py
(lid window, label, rounded corners) are recorded in docs/REVIEW.md as proposed, awaiting Amish.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Align, Axis, Box, Cylinder, Plane, Pos, RegularPolygon, Rot, Solid, Sphere, Text,
                       Vector, extrude, fillet)
from model import PARAMS, derived, build_components, on_panel

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
             "and LoRa module at right; ports, glands and antenna below; pole mounting kit (back plate, V-blocks and "
             "band clamps) behind"},
    # rendered with --focus on the enclosure (see docs/REVIEW.md, 2026-10-02) so the frame closes in on the ports
    {"name": "detail", "groups": ["shell", "internal"], "explode": False, "el": 12, "az": -32,
     "note": "Detail from the front right, slightly above (about 12 deg elevation), close on the enclosure "
             "without the pole: lid label and window, M12 sensor ports A (open) and B (capped), glands, vent "
             "and antenna base"},
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
POLE_Z = (1560.0, 2250.0)
C_STRIP = "#2E7D5B"
C_HEADER = "#111827"


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
    C = build_components(P)
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
    R = P["pole_od"] / 2
    # bottom-face penetrations in two rows, as model.py: name -> (x, y, thread dia, flange dia)
    PEN = {k: (x, y_back - P["pen_rows"][row], dt, df) for k, (x, row, dt, df) in P["pens"].items()}
    ports_xy = [PEN["port_a"][:2], PEN["port_b"][:2]]
    glands_xy = [PEN["gland_1"][:2], PEN["gland_2"][:2]]
    ax, ya = PEN["antenna"][:2]

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
    for x, y, dt, df in PEN.values():                       # holes in the bottom face, as model.py
        body -= _zcyl(x, y, z0 + wt / 2, dt / 2, wt + 2)
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
    for (x, _), t in zip(ports_xy, ("A", "B")):
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
    for i, (x, yb) in enumerate(ports_xy):
        df = PEN["port_a"][3]
        s = _hex_z(x, yb, z0 - 2.0, df, 4.0)                                 # panel nut against the base
        s += _zcyl(x, yb, z0 - 4.0 - 9.0, 8.0, 18.0)                         # threaded barrel, to z0 - 22
        s -= _zcyl(x, yb, z0 - 21.0, 5.6, 4.0)
        socks = s if socks is None else socks + s
        ins = _zcyl(x, yb, z0 - 20.5, 5.6, 3.0)
        for k in range(5):
            a = 2 * math.pi * k / 4 if k < 4 else 0.0
            rr = 3.0 if k < 4 else 0.0
            ins -= _zcyl(x + rr * math.cos(a + 0.785), yb + rr * math.sin(a + 0.785), z0 - 22.0, 0.6, 2.0)
        inserts = ins if inserts is None else inserts + ins
        if i == 1:                                                            # port B capped
            caps = _knurl_cap(x, yb, z0 - 8.0, 10.0, 17.0)
    add("M12 sensor sockets (ports A and B)", socks, C_STEEL, "metal", 10, "shell", E_DOWN)
    add("M12 socket inserts", inserts, C_BLACK, "plastic", 10, "shell", E_DOWN)
    add("M12 sealing cap (port B)", caps, C_DARK, "rubber", 10, "shell", (0, 0, -120))
    xb, yb_ = ports_xy[1]
    tether = _pipe([(xb + 9.5, yb_, z0 - 14), (xb + 12, yb_ - 4, z0 - 5), (xb + 12, yb_ - 4, z0 - 1.5)], 0.9)
    add("M12 cap tether", tether, C_DARK, "rubber", 10, "shell", (0, 0, -120))

    gl = None
    for x, yb in glands_xy:
        g = _hex_z(x, yb, z0 - 3.0, 22.0, 6.0)
        dome = _zcyl(x, yb, z0 - 12.0, 9.5, 12.0)
        dome = _fillet_try(dome, _fmin(dome, Axis.Z), [3.0, 2.0])
        for j in range(6):
            a = math.pi * j / 3
            dome -= _box(x + 9.5 * math.cos(a), yb + 9.5 * math.sin(a), z0 - 12.0, 1.2, 1.2, 8.0)
        g += dome
        gl = g if gl is None else gl + g
    add("M16 cable glands (panel lead, fixed-cable sensor)", gl, C_BLACK, "plastic", 3, "shell", E_DOWN)

    vx, vy, _, vdf = PEN["vent"]
    vent = _zcyl(vx, vy, z0 - 1.5, 6.5, 3.0)
    vcap = _zcyl(vx, vy, z0 - 7.0, vdf / 2, 5.0)
    vcap = _fillet_try(vcap, _fmin(vcap, Axis.Z), [2.0, 1.2])
    add("ePTFE pressure vent", vent + vcap, C_DARK, "plastic", 1, "shell", E_DOWN)

    wd, wl = P["whip"]
    base = _hex_z(ax, ya, z0 - 2.0, 16.0, 4.0) + _zcyl(ax, ya, z0 - 12.0, 7.0, 16.0)
    base = _fillet_try(base, _fmin(base, Axis.Z), [1.5, 1.0])
    add("Antenna bulkhead and base", base, C_STEEL, "metal", 9, "shell", E_DOWN)
    whip = _zcyl(ax, ya, z0 - 20 - wl / 2, wd / 2, wl)
    whip = _fillet_try(whip, _fmin(whip, Axis.Z), [4.0, 2.5])
    whip += _zcyl(ax, ya, z0 - 20 - 5.0, wd / 2 + 0.8, 10.0)
    add("Whip antenna (915 MHz)", whip, C_BLACK, "rubber", 9, "shell", (0, 0, -150))

    # ------------------------------------------------------------ inside (BOM 6, 7, 8, 11), model.py envelopes
    mt = P["mplate"][2]
    in_back = y_back - wt - P["boss"][2]                                     # internal plate on its bosses
    mf = in_back - mt
    add("Internal mounting plate (ASA)", C["mplate"].shape, C_ASA, "plastic", 11, "internal", E_IN)
    add("Internal plate screws", C["mplate_screws"].shape, C_STEEL, "metal", 13, "internal", E_IN)
    add("Plug-in connector strip and rail fuses", C["connectors"].shape, C_STRIP, "plastic", 15, "internal", E_IN)

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
    add("Power board terminal block", tb, C_STRIP, "plastic", 7, "internal", E_PWR)
    hx, hz, hl, hb, _ = P["prog_header"]
    riser = _bx(hx - hl / 2, hx + hl / 2, mf - pt_, pf, z0 + hz - hb / 2, z0 + hz + hb / 2)   # header body down to the PCB
    add("Serial programming header (6 pins, facing the lid)", C["prog_header"].shape + riser, C_HEADER, "plastic", 7, "internal", E_PWR)

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
    pig = _pipe(_bezier((-18, cf - 2, z0 + 162), (-18, -84, z0 + 150), (ax, -84, z0 + 60),
                        (ax, ya, z0 + wt + 8), n=10), 1.0)
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
    def grp(*keys):
        return _union(C[k].shape for k in keys)
    sides = ("r", "l")
    add("Bracket posts and struts (aluminium flat bar)", grp(*[f"{n}_{s_}" for n in ("post", "strut") for s_ in sides]),
        C_ALU2, "metal", 5, "shell", E_BRK)
    add("Bracket angle clips (plate and panel)", grp(*[f"{n}_{s_}" for n in ("plate_clip", "high_panel_clip", "low_panel_clip") for s_ in sides]),
        C_ALU2, "metal", 5, "shell", E_BRK)
    add("Bracket and panel clip bolts (stainless)", grp("bracket_bolts", "panel_bolts"), C_STEEL, "metal", 13, "shell", E_BRK)

    # ------------------------------------------------------------ pole mounting kit (BOM 12) and enclosure lugs (BOM 1)
    add("Back plate (aluminium)", C["plate"].shape, C_ALU, "metal", 12, "shell", E_MOUNT)
    add("Enclosure lugs (maker's kit)", C["lugs"].shape, C_DARK, "plastic", 1, "shell", E_MOUNT)
    add("Lug screws and nuts (stainless)", C["lug_screws"].shape, C_STEEL, "metal", 13, "shell", E_MOUNT)
    add("V-blocks (aluminium)", grp("vblock_low", "vblock_up"), C_ALU2, "metal", 12, "shell", (0, 210, 150))
    add("Stainless band clamps", C["bands"].shape, C_STEEL, "metal", 12, "shell", (0, 250, 150))

    # ------------------------------------------------------------ context (not in the BOM)
    pz0, pz1 = POLE_Z
    pole = _zcyl(0, 0, (pz0 + pz1) / 2, R, pz1 - pz0)
    pole = _fillet_try(pole, _fmin(pole, Axis.Z), [1.0, 0.5])
    add("Site pole section (48.3 mm galvanized)", pole, C_POLE, "metal", None, "context", (0, 0, 0))
    pcap = _zcyl(0, 0, pz1 + 6, R + 1.5, 12.0)
    pcap = _fillet_try(pcap, _fmax(pcap, Axis.Z), [5.0, 3.0])
    add("Pole cap", pcap, C_DARK, "plastic", None, "context", (0, 0, 0))

    # panel lead: gland 1 down, back behind the antenna, up the right side to the junction box
    gx, gy = glands_xy[0]
    xr = 95.0                                                                # outboard of the plate clips and posts
    jy, jz = on_panel(JLY - 20.0, P, lz=-pt / 2 - 8.0)
    pts = _bezier((gx, gy, z0 - 17), (gx, gy, z0 - 50), (40, -60, z0 - 45), (70, -60, z0 - 40))
    pts += _bezier((70, -60, z0 - 40), (xr, -60, z0 - 38), (xr, -60, z0 - 30), (xr, -60, z0 - 5))[1:]
    pts += [(xr, -60, z0 + 200)]
    pts += _bezier((xr, -60, z0 + 200), (xr, -60, z0 + 260), (JX, jy + 10, jz - 40), (JX, jy, jz))[1:]
    lead = _pipe(pts, 3.0)
    add("Panel lead", lead, C_CABLE, "rubber", 4, "context", (0, 0, 0))
    # sensor cable: M12 plug in port A, down and tied to the pole
    px_, yb = ports_xy[0]
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
