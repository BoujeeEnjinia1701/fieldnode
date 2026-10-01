"""FieldNode prototype build plan pictures (FND-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|joints|steps|wiring ...]
With no argument it draws everything. Every picture is drawn from cad/src/model.py
(build_components), so the pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/FND-DWG-101 to 109        making sketches for the made and drilled components
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring with wire sizes (matplotlib)
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build_components, derived, bracket_points, bracket_geometry, pole_context, _panel_frame  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-09-30"
D = derived(P)
C = build_components(P, shield=True)
S = lambda *ks: _fuse([C[k].shape for k in ks])  # noqa: E731

COL = {"plate": "#A8A29E", "vblock": "#57534E", "band": "#9CA3AF", "body": "#D1D5DB", "lid": "#E5E7EB",
       "lugs": "#374151", "pens": "#1F2937", "ports": "#D4A017", "vent": "#F9FAFB", "antenna": "#374151",
       "mplate": "#94A3B8", "cell": "#C2410C", "power": "#16A34A", "ctrl": "#0F766E", "strip": "#7C3AED",
       "clip": "#1D4ED8", "post": "#0E7490", "strut": "#B45309", "pclip": "#6D28D9", "panel": "#1E3A8A",
       "shield": "#F5F5F4", "bolt": "#111827", "pole": "#9CA3AF"}


def _fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def part(name, shape, color, explode=(0, 0, 0), alpha=1.0):
    return Part(name, shape, color, None, tuple(explode), alpha)


def pole(length=900):
    return part("Pole stub (site supplied)", pole_context(P, length), COL["pole"])


# ----------------------------------------------------------------- named parts, in build order
def made():
    return {
        "plate": part("Back plate", C["plate"].shape, COL["plate"]),
        "vblocks": part("V-blocks (2)", S("vblock_low", "vblock_up"), COL["vblock"]),
        "body": part("Enclosure body, drilled", S("body", "vent"), COL["body"]),
        "pens": part("Glands, ports, antenna", S("glands", "ports", "antenna"), COL["pens"]),
        "lugs": part("Enclosure lugs (4) and M5 screws", S("lugs", "lug_screws"), COL["lugs"]),
        "mplate": part("Internal plate", C["mplate"].shape, COL["mplate"]),
        "modules": part("Cell, modules, connector strip", S("cell", "power", "ctrl", "connectors"), COL["power"]),
        "lid": part("Lid", C["lid"].shape, COL["lid"]),
        "clips": part("Plate clips (2)", S("plate_clip_r", "plate_clip_l"), COL["clip"]),
        "posts": part("Posts (2)", S("post_r", "post_l"), COL["post"]),
        "struts": part("Struts (2)", S("strut_r", "strut_l"), COL["strut"]),
        "pclips": part("Panel clips (4)", S("high_panel_clip_r", "high_panel_clip_l", "low_panel_clip_r", "low_panel_clip_l"), COL["pclip"]),
        "panel": part("Solar panel", C["panel"].shape, COL["panel"]),
        "bands": part("Band clamps (2)", C["bands"].shape, COL["band"]),
        "shield": part("Sun shield (hot sites)", S("shield", "shield_screws"), COL["shield"]),
    }


# ----------------------------------------------------------------- overview
def overview():
    M = made()
    off = {"plate": (0, 0, 0), "vblocks": (0, 110, 0), "body": (0, -170, -40), "pens": (0, -170, -230),
           "lugs": (-230, -60, 0), "mplate": (0, -330, -20), "modules": (0, -420, -20), "lid": (0, -560, -140),
           "clips": (0, -60, 170), "posts": (0, -60, 330), "struts": (0, -250, 300), "pclips": (0, -60, 490),
           "panel": (0, -60, 630), "bands": (0, 300, 0), "shield": (330, -300, -120)}
    order = ["plate", "vblocks", "body", "pens", "lugs", "mplate", "modules", "lid", "clips", "posts", "struts",
             "pclips", "panel", "bands", "shield"]
    parts = []
    for k in order:
        p = M[k]
        p.explode = off[k]
        parts.append(p)
    return bv.overview(parts, OUT / "overview.png", "FieldNode prototype: every component, pulled apart",
                       subtitle="Numbered in build order; 15 is the hot-climate option. Seen from the front right and above",
                       elev=18, azim=-50, size=(11, 8.5), dpi=150)


# ----------------------------------------------------------------- making sketches
def flat(shape, origin, x_dir, z_dir):
    import build123d as b
    return b.Plane(origin=origin, x_dir=x_dir, z_dir=z_dir).to_local_coords(shape)


def sheets():
    import build123d as b
    M = made()
    ctx = [pole(700)]
    base = dict(project="FieldNode", date=DATE)
    out = []
    B = bracket_points(P)
    bg = bracket_geometry(P)
    z0 = P["z0"]
    plb = D["plate_bot"]

    # 101 back plate
    out.append(bv.component_sheet(
        Part("Back plate", C["plate"].shape, COL["plate"]), [M["vblocks"], M["body"], M["clips"]] + ctx,
        dwg_no="FND-DWG-101", title="FieldNode back plate: making sketch", material="Aluminium sheet 3 mm, 5052 or 6061 class",
        notes=["Blank 180 x 320 mm, 3 mm aluminium. Front view is the face the box sits on.",
               "Heights from the bottom edge; sideways from the centre line.",
               "Window 100 x 150 mm, 6 mm corner radius, 65 to 215 mm up: drill the",
               "  corners 12 mm, cut between with a jigsaw, file straight.",
               "Band slots 3 x 15 mm at 51 mm each side, centred 20 and 270 mm up:",
               "  chain drill 3 mm, file square. The band goes through these.",
               "V-block screws 4.5 mm at 18 mm each side, 20 and 270 mm up;",
               "  countersink from the front so the screw heads sit flush.",
               "Lug screws 5.5 mm at 62 mm each side, 31 and 249 mm up.",
               "Plate clip screws 5.5 mm at 65 mm each side, 275 and 305 mm up.",
               "Shield screws: drill 3.3 mm and tap M4 at 84 mm each side, 80 and 220 mm up.",
               "Wall holes 6.5 mm at 40 mm each side 305 mm up, 75 mm each side 12 mm up.",
               "Deburr every hole and edge; round the corners to about 2 mm.",
               "Check: lay the V-blocks, lugs and clips on it and look through each hole."],
        inset_view=(22, 72), **base))

    # 102 V-block
    vb = C["vblock_low"].shape
    out.append(bv.component_sheet(
        Part("V-block", vb, COL["vblock"]), [M["plate"], M["bands"], pole(200)],
        dwg_no="FND-DWG-102", title="FieldNode V-block (make 2): making sketch", material="Aluminium flat bar 60 x 40 mm, 6082 or 6061",
        view_shape=b.Pos(0, 0, -D["clamps"][0]) * vb, inset_view=(30, 60),
        notes=["Make two. Saw a 20 mm slice off 60 x 40 mm bar; saw and file it to",
               "  60 wide x 33 deep x 20 tall. The flat back goes on the back plate.",
               "Scribe a 90 degree V on both 60 x 33 faces with a 45 degree square:",
               "  50.3 mm wide at the front face, point 7.8 mm from the back face.",
               "Saw just inside both lines, file to the lines, keep the V faces flat.",
               "Break the V's sharp front edges 0.5 mm so they cannot score the pole.",
               "Drill 3.3 mm, 14 mm deep, and tap M4 12 deep in the back face,",
               "  at 18 mm each side of centre, half way up (10 mm).",
               "Fit: two M4 countersunk screws from the front of the plate.",
               "The 48.3 mm pole touches both V faces 24.9 mm from the plate,",
               "  about 8 mm inside the front face. 40 to 60 mm poles also seat.",
               "Check: on a 48 mm tube the block must not rock; hold it to light,",
               "  light should show at the bottom of the V, not along the faces."],
        **base))

    # 103 plate clip
    clip = C["plate_clip_r"].shape
    out.append(bv.component_sheet(
        Part("Plate clip", clip, COL["clip"]), [M["plate"], M["posts"], M["struts"], M["body"]],
        dwg_no="FND-DWG-103", title="FieldNode plate clip (make 2, a left and a right): making sketch",
        material="Aluminium equal angle 30 x 30 x 3 mm", view_shape=b.Pos(0, 0, -(z0 + P["clip_z"][0])) * clip,
        notes=["Cut two 77 mm lengths of 30 x 30 x 3 angle; square and deburr the ends.",
               "Flat leg (goes on the plate): two 5.5 mm holes, 12 mm in from its free edge,",
               "  17 and 47 mm up from the bottom end.",
               "Upright leg (stands forward): three 6.6 mm holes, measured from the",
               "  back of the angle (the face on the plate) and up from the bottom end:",
               "  strut foot 17 back, 14 up; post 18 back, 44 up; post 13.7 back, 67.6 up.",
               "Right and left clips are mirror images: drill the upright legs as a",
               "  pair clamped back to back so the holes line up.",
               "Fit: flat leg on the plate front, upright leg 80 to 83 mm from the",
               "  centre line, bottom end 258 mm up the plate; M5 screws from behind.",
               "The post bolts to the outside of the upright leg, the strut to the inside.",
               "Check: the clip sits flat on the plate and its upright leg is square."],
        **base))

    # 104 post and 105 strut, laid flat
    for key, dwg, n, L, note in (("post", "FND-DWG-104", "post", bg["post"]["bar_len"], [
            f"Cut two {bg['post']['bar_len']:.0f} mm lengths of 20 x 3 mm flat bar.",
            "Round both ends to a 10 mm radius (file to a scribed circle).",
            "Drill 6.6 mm: one hole 10 mm from each end (161.2 mm apart) and a",
            "  third 24 mm from the lower hole, on the centre line.",
            "Drill the two posts clamped together so the holes match.",
            "Fit: the lower end bolts to the outside of the plate clip with two M6",
            "  bolts, which hold the post rigid. The upper end bolts to the high",
            "  panel clip with one M6 bolt, which is the panel's hinge.",
            "The post leans back 10 degrees from vertical and passes 2 mm in front",
            "  of the plate's top edge.",
            "Check: hole centres 161 mm and 24 mm apart, within 0.5 mm."]),
            ("strut", "FND-DWG-105", "strut", bg["strut"]["bar_len"], [
            f"Cut two {bg['strut']['bar_len']:.0f} mm lengths of 20 x 3 mm flat bar.",
            "Round both ends to a 10 mm radius.",
            "Drill 6.6 mm, 10 mm from each end: 129.2 mm between centres.",
            "  This length sets the panel tilt of 40 degrees.",
            "Drill the two struts clamped together so the holes match.",
            "Fit: the lower end bolts to the inside of the plate clip, the upper",
            "  end to the inside of the low panel clip; one M6 bolt each end.",
            "The strut rises at 38 degrees and passes 10 mm above the sun shield.",
            "Check: hole centres 129.2 mm apart, within 0.5 mm; a shorter strut",
            "  tips the panel steeper, a longer one flatter."])):
        sh = C[f"{key}_r"].shape
        a = B["post_low"] if key == "post" else B["strut_foot"]
        c = B["post_head"] if key == "post" else B["strut_head"]
        ln = math.hypot(c[0] - a[0], c[1] - a[1])
        u = (0, (c[0] - a[0]) / ln, (c[1] - a[1]) / ln)
        x0 = P["clip_x"] + (P["angle"][1] if key == "post" else -P["bar"][1])
        fl = flat(sh, (x0, a[0], a[1]), u, (1, 0, 0))
        out.append(bv.component_sheet(
            Part(n.capitalize(), sh, COL[key]), [M["clips"], M["pclips"], M["panel"], M["plate"], M["posts" if key == "strut" else "struts"]],
            dwg_no=dwg, title=f"FieldNode {n} (make 2): making sketch", material="Aluminium flat bar 20 x 3 mm, 6063 class",
            view_shape=fl, inset_view=(15, -20), notes=note, **base))

    # 106 panel clip, in panel coordinates
    F = _panel_frame(P)
    pc = F.inverse() * C["high_panel_clip_r"].shape
    out.append(bv.component_sheet(
        Part("Panel clip", C["high_panel_clip_r"].shape, COL["pclip"]), [M["panel"], M["posts"], M["struts"]],
        dwg_no="FND-DWG-106", title="FieldNode panel clip (make 4): making sketch", material="Aluminium equal angle 30 x 30 x 3 mm",
        view_shape=pc, inset_view=(-40, 10),
        notes=["Cut four 30 mm lengths of 30 x 30 x 3 angle; deburr.",
               "Flat leg (goes on the panel frame's back lip): two 4.5 mm holes,",
               "  6 mm from one end, 11 and 23 mm from the back of the upright leg.",
               "Upright leg: one 6.6 mm hole at mid-length (15 mm), 16.5 mm out",
               "  from the face that sits on the lip.",
               "All four clips are the same. On each side one goes at the panel's high",
               "  edge (post), one at its low edge (strut); the drilled end lines up",
               "  with the panel edge, the flat leg points outward.",
               "Fit: M4 bolts through the clip and the frame lip, nut inside the frame.",
               "  Drill the lip through the clip; keep clear of the glass and cells.",
               "Check the panel you buy has a back lip at least 12 mm wide;",
               "  if not, stop and see open question 3 in the plan."],
        **base))

    # 107 internal plate
    out.append(bv.component_sheet(
        Part("Internal plate", C["mplate"].shape, COL["mplate"]), [M["body"], M["modules"]],
        dwg_no="FND-DWG-107", title="FieldNode internal plate: making sketch", material="ASA, 3D printed, 100 % infill",
        inset_view=(20, -60),
        notes=["Print flat, 130 x 180 x 3 mm, in ASA in an enclosed printer.",
               "Four 4.5 mm holes 10 mm in from each side and from top and bottom",
               "  (110 x 160 mm apart), to match the enclosure's four moulded bosses.",
               "  Measure your enclosure's bosses first and move the holes to suit.",
               "Finger slot 40 x 10 mm, 7 mm below the top edge, for lifting out.",
               "Lay out on the front: cell holder lower left, power modules lower right,",
               "  controller above, connector strip along the bottom edge.",
               "Mark each module's holes through the module; drill 3.2 mm for M3",
               "  screws on 6 mm nylon standoffs.",
               "Fit: four M4 screws into the bosses; the plate sits 6 mm off the back",
               "  wall and 7 mm above the floor, clear of the gland nuts.",
               "Check: flat within 0.5 mm; drops in and lifts out without force."],
        **base))

    # 108 enclosure body, drilled, drawn upside down so the top view shows the bottom face
    body = S("body", "vent")
    flip = b.Rot(180, 0, 0) * b.Pos(0, 0, -D["enc_zc"]) * C["body"].shape
    out.append(bv.component_sheet(
        Part("Enclosure body", body, COL["body"]), [M["plate"], M["pens"], M["lugs"]],
        dwg_no="FND-DWG-108", title="FieldNode enclosure body: drilling sketch", material="Bought IP65 polycarbonate box 150 x 90 x 200 mm",
        view_shape=flip, inset_view=(-25, -60),
        notes=["Drawn upside down: stand the box on its top, back face toward you;",
               "  the top view then shows the bottom face as you see it on the bench.",
               "Measure from the back face, and sideways from the centre line (left and",
               "  right as seen from the front). The drilling layout picture repeats this.",
               "Back row, 27 mm from the back face: gland 1 at 40 left, gland 2 at",
               "  8 left (16.2 mm holes), vent at 24 right (12.2 mm).",
               "Front row, 55 mm from the back face: port A at 54 left, port B at",
               "  22 left (16.2 mm), antenna at 30 right (6.5 mm).",
               "Every outside flange is at least 8 mm from the next one.",
               "Tape the face, pilot drill 3 mm slowly with wood behind, open out with",
               "  a step drill, light pressure. No solvents: polycarbonate crazes.",
               "Deburr inside and out. Check each hole size on the part's datasheet",
               "  before the last step of the drill.",
               "Fit the lugs (the maker's kit) to the four back corners as the maker says."],
        **base))

    # 109 sun shield
    sh = C["shield"].shape
    out.append(bv.component_sheet(
        Part("Sun shield", sh, "#E7E5E4"), [M["plate"], M["body"], M["lid"], M["clips"], M["struts"]],
        dwg_no="FND-DWG-109", title="FieldNode sun shield (hot sites only): making sketch",
        material="White powder-coated aluminium sheet 0.5 mm", view_shape=b.Pos(0, 0, -z0) * sh, inset_view=(24, -58),
        notes=["One blank, folded: front 181 x 206 mm in the middle; a side 106 mm",
               "  wide on each long edge; a top 76 mm deep on the top edge (the 30 mm",
               "  vent slot at the back is simply the top being short); 10 mm tabs",
               "  on the ends of the top; a 12 mm flange on the back of each side.",
               "Cut with snips; drill 3 mm relief holes where bend lines cross.",
               "Fold the sides back 90 degrees, then the top, then the tabs down over",
               "  the sides; rivet each tab with two 3.2 mm rivets.",
               "Fold each flange 90 degrees inward; drill two 4.5 mm holes 6 mm",
               "  from the fold, 30 and 170 mm up from the lower edge.",
               "Fit: flanges flat on the plate, 3 mm beside the box; four M4 thumb",
               "  screws into the plate. 15 mm air gap on the front, sides and top.",
               "To open the lid: undo the four thumb screws, pull the shield forward.",
               "Check: the gap is 15 mm (plus or minus 2) all round."],
        **base))
    return out


# ----------------------------------------------------------------- joints
def joints():
    import build123d as b
    out = []
    z1 = D["clamps"][1]
    win = lambda sh, x0, x1, y0, y1, z0_, z1_: sh & (b.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0_ + z1_) / 2) * b.Box(x1 - x0, y1 - y0, z1_ - z0_))  # noqa: E731
    # 01 V-block, pole and band (top-down, cut at the clamp height)
    box_ = (-80, 80, -60, 45, z1 - 10, z1 + 6)
    out.append(bv.joint([
        part("Pole (site supplied)", win(pole_context(P, 900), *box_), COL["pole"]),
        part("Back plate", win(C["plate"].shape, *box_), COL["plate"]),
        part("V-block", win(C["vblock_up"].shape, *box_), COL["vblock"]),
        part("Band clamp, through the plate slots", win(C["bands"].shape, *box_), COL["band"])],
        OUT / "joint-01.png", "Joint 1: V-block, pole and band clamp",
        subtitle="Cut level with the upper clamp, seen from above. The pole bears on both V faces; the band pulls it in",
        elev=80, azim=-90, size=(8, 6)))
    # 02 lugs on the plate
    box_ = (20, 95, -60, -35, D["enc_top"] - 15, D["enc_top"] + 30)
    out.append(bv.joint([
        part("Back plate", win(C["plate"].shape, *box_), COL["plate"]),
        part("Enclosure body", win(C["body"].shape, *box_), COL["body"]),
        part("Lug (maker's kit)", win(C["lugs"].shape, *box_), COL["lugs"]),
        part("M5 screw from behind, nyloc nut in front", win(C["lug_screws"].shape, *box_), COL["bolt"])],
        OUT / "joint-02.png", "Joint 2: enclosure lug on the back plate (top right corner)",
        subtitle="The box back sits flat on the plate; each lug is held by one M5 screw", elev=35, azim=-60, size=(8, 6)))
    # 03 bottom face from below
    box_ = (-80, 80, -130, -40, D["enc_bot"] - 30, D["enc_bot"] + 12)
    out.append(bv.joint([
        part("Enclosure bottom", win(C["body"].shape, *box_), COL["body"]),
        part("Glands (back row)", win(C["glands"].shape, *box_), COL["pens"]),
        part("Vent (back row)", win(C["vent"].shape, *box_), "#64748B"),
        part("Sensor ports (front row)", win(C["ports"].shape, *box_), COL["ports"]),
        part("Antenna bulkhead (front row)", win(C["antenna"].shape, *box_), COL["antenna"])],
        OUT / "joint-03.png", "Joint 3: the bottom face, seen from below",
        subtitle="Two rows, 27 and 55 mm from the back face; outside flanges at least 8 mm apart", elev=-55, azim=-70, size=(8, 6)))
    # 04 internal plate on a boss, cut open
    zc = D["enc_zc"]
    box_ = (15, 70, -110, -40, zc - 104, zc - 62)
    out.append(bv.joint([
        part("Enclosure body", win(C["body"].shape, *box_), COL["body"]),
        part("Internal plate", win(C["mplate"].shape, *box_), COL["mplate"]),
        part("M4 screw into the moulded boss", win(C["mplate_screws"].shape, *box_), COL["bolt"]),
        part("Connector strip", win(C["connectors"].shape, *box_), COL["strip"]),
        part("Gland nut on the floor", win(C["glands"].shape + C["vent"].shape, *box_), COL["pens"])],
        OUT / "joint-04.png", "Joint 4: internal plate on its bosses (box cut open beside the lower right boss)",
        subtitle="Seen from the right. Plate 6 mm off the back wall, 7 mm above the floor, clear of the gland nuts", elev=12, azim=10, size=(8, 6)))
    # 05 plate clip with post and strut
    zlo, zhi = D["enc_top"] + 5, D["plate_top"] + 30
    box_ = (40, 100, -100, -38, zlo, zhi)
    out.append(bv.joint([
        part("Back plate", win(C["plate"].shape, *box_), COL["plate"]),
        part("Plate clip", win(C["plate_clip_r"].shape, *box_), COL["clip"]),
        part("Post (outside the clip, 2 bolts)", win(C["post_r"].shape, *box_), COL["post"]),
        part("Strut (inside the clip, 1 bolt)", win(C["strut_r"].shape, *box_), COL["strut"]),
        part("M6 and M5 bolts", win(C["bracket_bolts"].shape, *box_), COL["bolt"])],
        OUT / "joint-05.png", "Joint 5: plate clip, post foot and strut foot (right side)",
        subtitle="Seen from the front right. Every face that meets another is flat and bolted", elev=15, azim=-30, size=(8, 6)))
    # 06 and 07 panel clips, seen from under the panel
    for n, key, mem, memname, ly in ((6, "high_panel_clip_r", "post_r", "Post", P["head_ly"][0]),
                                     (7, "low_panel_clip_r", "strut_r", "Strut", P["head_ly"][1])):
        yc, zc_ = [v for v in __import__("model").on_panel(ly, P, -15)]
        box_ = (60, 125, yc - 40, yc + 40, zc_ - 40, zc_ + 40)
        out.append(bv.joint([
            part("Panel frame (back lip)", win(C["panel"].shape, *box_), COL["panel"]),
            part(("High" if n == 6 else "Low") + " panel clip", win(C[key].shape, *box_), COL["pclip"]),
            part(memname, win(C[mem].shape, *box_), COL[mem[:-2]]),
            part("M4 bolts through the lip, M6 hinge bolt", win(C["panel_bolts"].shape + C["bracket_bolts"].shape, *box_), COL["bolt"])],
            OUT / f"joint-0{n}.png", f"Joint {n}: {memname.lower()} head on the {'high' if n == 6 else 'low'} panel clip (right side)",
            subtitle="Seen from below and outside. The clip bolts to the frame's back lip, never to the glass",
            elev=-30, azim=-20, size=(8, 6)))
    # 08 shield flange
    box_ = (68, 95, -80, -40, P["z0"] + 150, P["z0"] + 215)
    out.append(bv.joint([
        part("Back plate", win(C["plate"].shape, *box_), COL["plate"]),
        part("Enclosure body", win(C["body"].shape, *box_), COL["body"]),
        part("Sun shield side and flange", win(C["shield"].shape, *box_), "#D6D3D1"),
        part("M4 thumb screw", win(C["shield_screws"].shape, *box_), COL["bolt"])],
        OUT / "joint-08.png", "Joint 8: sun shield flange on the back plate (right side, upper screw)",
        subtitle="The flange is folded in from the side sheet and lies flat on the plate, 3 mm beside the box",
        elev=15, azim=-80, size=(8, 6)))
    return out


# ----------------------------------------------------------------- assembly steps
def steps():
    M = made()
    out = []

    def st(n, done, new, title, sub, **kw):
        out.append(bv.step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))

    def mv(p, e):
        q = Part(p.name, p.shape, p.color, None, tuple(e), p.alpha)
        return q
    pl = M["plate"]
    st(1, [pl], [mv(part("Upper V-block", C["vblock_up"].shape, COL["vblock"]), (0, 90, 0)),
                 mv(part("Lower V-block", C["vblock_low"].shape, COL["vblock"]), (0, 90, 0))], "V-blocks onto the back plate",
       "Two M4 countersunk screws each, from the front of the plate, threadlocker. Seen from behind",
       elev=20, azim=60)
    st(2, [part("Enclosure body", C["body"].shape, COL["body"])],
       [mv(part("Glands and vent (back row)", S("glands", "vent"), COL["pens"]), (0, 0, -100)),
        mv(part("Sensor ports (front row)", C["ports"].shape, COL["ports"]), (0, 0, -60)),
        mv(part("Antenna bulkhead and whip", C["antenna"].shape, COL["antenna"]), (0, 0, -150))],
       "fit the glands, vent, ports and antenna",
       "Each goes in from below with its seal outside; nut inside, maker's torque. Seen from below",
       elev=-30, azim=-60, label_done=False)
    vb = M["vblocks"]
    st(3, [pl, vb], [mv(M["body"], (0, -120, 0)), mv(M["pens"], (0, -120, 0)), mv(M["lugs"], (0, -40, 0))],
       "enclosure onto the back plate",
       "Lugs on the box corners; box back flat on the plate; four M5 screws from behind, nyloc nuts in front",
       elev=18, azim=-55)
    st(4, [M["mplate"]], [mv(part("Cell holder (no cell yet, fuse out)", C["cell"].shape, COL["cell"]), (0, -70, 0)),
                          mv(part("Power modules", C["power"].shape, COL["power"]), (0, -70, 0)),
                          mv(part("Controller", C["ctrl"].shape, COL["ctrl"]), (0, -70, 0)),
                          mv(part("Connector strip", C["connectors"].shape, COL["strip"]), (0, -70, 0))],
       "build the internal plate",
       "Each on M3 screws and 6 mm nylon standoffs; then wire them as the wiring diagram shows",
       elev=15, azim=-40, label_done=True)
    box_done = [pl, vb, M["body"], M["pens"], M["lugs"]]
    st(5, box_done, [mv(part("Internal plate with modules", S("mplate", "cell", "power", "ctrl", "connectors", "mplate_screws"), COL["mplate"]), (0, -180, 0))],
       "internal plate into the enclosure",
       "Four M4 screws into the bosses; plug in the panel, port and gland leads at the strip; fresh desiccant",
       elev=18, azim=-55, label_done=False)
    inside = part("Internal plate with modules", S("mplate", "cell", "power", "ctrl", "connectors"), COL["mplate"])
    st(6, box_done + [inside], [mv(M["lid"], (0, -150, 0))], "close the lid",
       "Gasket clean and seated, no wire across it; tighten the captive screws evenly in a cross pattern",
       elev=18, azim=-55, label_done=False)
    closed = box_done + [M["lid"]]
    st(7, closed, [mv(M["clips"], (0, -60, 0))], "plate clips onto the back plate",
       "Two M5 screws each from behind, nyloc nuts in front; upright legs forward",
       elev=20, azim=-45, label_done=False)
    st(8, closed + [M["clips"]], [mv(M["posts"], (0, 0, 120)), mv(M["struts"], (0, -60, 60))],
       "posts and struts onto the plate clips",
       "Post outside the clip on two M6 bolts (tight); strut inside on one M6 bolt (snug for now)",
       elev=15, azim=-40, label_done=False)
    st(9, [M["panel"]], [mv(M["pclips"], _panel_down(40))],
       "panel clips onto the panel frame",
       "Panel face down on a soft cloth; drill the back lip through each clip; two M4 bolts each, nuts inside the frame",
       elev=-50, azim=70, label_done=False)
    st(10, closed + [M["clips"], M["posts"], M["struts"]], [mv(part("Panel with its clips", S("panel", "high_panel_clip_r", "high_panel_clip_l", "low_panel_clip_r", "low_panel_clip_l"), COL["panel"]), (0, -80, 160))],
       "panel onto the posts and struts",
       "One M6 bolt at each post head (the hinge), one at each strut head; check 40 degrees, then tighten all",
       elev=15, azim=-45, label_done=False)
    full = closed + [M["clips"], M["posts"], M["struts"], M["pclips"], M["panel"]]
    st(11, full, [mv(M["shield"], (0, -160, 0))], "sun shield (hot sites only)",
       "Slide it over the box from the front; flanges flat on the plate; four M4 thumb screws, finger tight",
       elev=18, azim=-40, label_done=False)
    st(12, full, [mv(M["bands"], (0, 160, 0))], "onto the pole with the band clamps",
       "Seen from behind. Pole in both V-blocks; each band round the pole, through its two slots, across the plate front",
       context=[pole(640)], elev=22, azim=65, label_done=False)
    return out


def _panel_down(d):
    t = math.radians(P["tilt"])
    return (0, d * math.sin(t), -d * math.cos(t))


# ----------------------------------------------------------------- drilling layouts
def _holes(face):
    """Openings in a flat face, from the model: (kind, cx, cz or cy, width, height)."""
    out = []
    for w in face.inner_wires():
        bb = w.bounding_box()
        edges = w.edges()
        circ = len(edges) == 1 or all(e.geom_type == "CIRCLE" for e in edges) and len(edges) <= 2
        out.append(("circle" if circ else "slot", bb.center(), bb.size))
    return out


def layouts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch
    INK, MUT, AC = "#111827", "#4B5563", "#0F766E"
    res = []
    # back plate, seen from the front (the face the enclosure sits on)
    pl = C["plate"].shape
    yf = D["plate_front"]
    face = [f for f in pl.faces() if abs(f.center().Y - yf) < 0.01 and f.area > 1e4][0]
    H = _holes(face)
    zb = D["plate_bot"]
    names = {3.3: "M4 tapped (drill 3.3)", 4.5: "4.5, countersunk", 5.5: "5.5", 6.5: "6.5 wall"}
    fig = plt.figure(figsize=(9.5, 11), dpi=150)
    ax = fig.add_axes([0.08, 0.07, 0.62, 0.84]); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(Rectangle((-90, 0), 180, 320, fc="#F5F5F4", ec=INK, lw=1.2))
    ax.axvline(0, color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    xs, zs = set(), set()
    for kind, c, sz in H:
        x, z = c.X, c.Z - zb
        if kind == "circle":
            d = sz.X
            ax.add_patch(plt.Circle((x, z), d / 2, fc="white", ec=INK, lw=1))
            ax.plot([x - d / 2 - 2, x + d / 2 + 2], [z, z], color=MUT, lw=0.4); ax.plot([x, x], [z - d / 2 - 2, z + d / 2 + 2], color=MUT, lw=0.4)
        else:
            r = 6 if sz.X > 50 else 0
            ax.add_patch(FancyBboxPatch((x - sz.X / 2 + r, z - sz.Z / 2 + r), sz.X - 2 * r, sz.Z - 2 * r, boxstyle=f"round,pad={r}", fc="white", ec=INK, lw=1))
        if x > 0.5:
            xs.add(round(x, 1))
        if not (kind == "slot" and sz.X > 50):
            zs.add(round(z, 1))
        else:
            zs.add(round(z - sz.Z / 2, 1)); zs.add(round(z + sz.Z / 2, 1)); xs.add(round(sz.X / 2, 1))
    for i, x in enumerate(sorted(xs)):
        yl = -12 - 9 * (i % 2)
        ax.plot([x, x], [0, yl + 3], color=AC, lw=0.4, ls=":")
        ax.text(x, yl, f"{x:g}", ha="center", va="top", fontsize=7.5, color=AC)
    ax.text(0, -36, "sideways from the centre line, mm (same each side)", ha="center", fontsize=8, color=MUT)
    for i, z in enumerate(sorted(zs)):
        xl = -96 - 16 * (i % 2)
        ax.plot([xl + 2, -90], [z, z], color=AC, lw=0.4, ls=":")
        ax.text(xl, z, f"{z:g}", ha="right", va="center", fontsize=7.5, color=AC)
    ax.text(-128, 160, "up from the bottom edge, mm", rotation=90, ha="center", va="center", fontsize=8, color=MUT)
    ax.set_xlim(-135, 100); ax.set_ylim(-42, 330)
    fig.text(0.04, 0.975, "Back plate: hole and cut-out positions", fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.04, 0.95, "Seen from the front (the face the enclosure sits on). Full size figures in mm, taken from the model.", fontsize=8.5, color=MUT, va="top")
    key = ["Window 100 x 150, 6 mm corners", "  (behind the enclosure, saves weight)", "Band slots 3 x 15, at 51", "V-block screws 4.5, countersunk", "  from the front, at 18",
           "Lug screws 5.5, at 62", "Plate clip screws 5.5, at 65", "Shield screws M4 tapped", "  (drill 3.3), at 84", "Wall holes 6.5, at 40 and 75",
           "", "Heights: 20 and 270 are the", "  two band clamps (250 apart)"]
    fig.text(0.72, 0.86, "What each opening is (mm)", fontsize=9, fontweight="bold", color=INK, va="top")
    for i, t in enumerate(key):
        fig.text(0.72, 0.83 - i * 0.022, t, fontsize=8, color=INK, va="top")
    fig.text(0.04, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.96, 0.015, "github.com/BoujeeEnjinia1701/fieldnode", fontsize=7, color=AC, ha="right", family="monospace")
    fig.savefig(OUT / "plate-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "plate-holes.png")

    # enclosure bottom face, seen from below, with the front of the box at the bottom of the page
    body = C["body"].shape
    face = [f for f in body.faces() if abs(f.center().Z - P["z0"]) < 0.01 and f.area > 5e3][0]
    H = _holes(face)
    yb = D["enc_back"]
    ew, ed = P["enc"][0], P["enc"][1] - P["lid_d"]
    lbl = {}
    for k, (x, row, dt, df) in P["pens"].items():
        lbl[(round(x), row)] = {"gland_1": "Gland 1, panel lead", "gland_2": "Gland 2, fixed-cable sensor", "vent": "Vent",
                                "port_a": "Port A", "port_b": "Port B", "antenna": "Antenna"}[k], df
    fig = plt.figure(figsize=(11, 7), dpi=150)
    ax = fig.add_axes([0.05, 0.1, 0.9, 0.75]); ax.set_aspect("equal"); ax.set_axis_off()
    # looking up from below with the back face at the top: x to the right as seen from the front
    ax.add_patch(Rectangle((-ew / 2, 0), ew, ed, fc="#F3F4F6", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-ew / 2, ed), ew, P["lid_d"], fc="white", ec=MUT, lw=0.8, ls="--"))
    ax.text(0, ed + P["lid_d"] / 2, "lid (do not drill)", ha="center", va="center", fontsize=7.5, color=MUT)
    ax.text(-ew / 2 + 2, -2, "back face (goes against the back plate), toward you", ha="left", va="top", fontsize=8, color=MUT)
    ax.axvline(0, ymin=0.05, ymax=0.95, color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    for kind, c, sz in H:
        x, yy = c.X, yb - c.Y
        row = 0 if abs(yy - P["pen_rows"][0]) < 1 else 1
        name, df = lbl[(round(x), row)]
        ax.add_patch(plt.Circle((x, yy), df / 2, fc="none", ec=MUT, lw=0.6, ls="--"))
        ax.add_patch(plt.Circle((x, yy), sz.X / 2, fc="white", ec=INK, lw=1.1))
        ax.plot([x - df / 2 - 2, x + df / 2 + 2], [yy, yy], color=MUT, lw=0.4); ax.plot([x, x], [yy - df / 2 - 2, yy + df / 2 + 2], color=MUT, lw=0.4)
        ax.text(x, yy + (-df / 2 - 1.5 if row == 0 else df / 2 + 1.5), f"{name}\n{sz.X:.1f} hole, {x:+g}",
                ha="center", va="top" if row == 0 else "bottom", fontsize=7, color=INK, linespacing=1.2, zorder=3,
                bbox=dict(boxstyle="round,pad=0.15", fc="#F3F4F6", ec="none"))
    for r in P["pen_rows"]:
        ax.plot([ew / 2, ew / 2 + 14], [r, r], color=AC, lw=0.5, ls=":")
        ax.text(ew / 2 + 15, r, f"{r:g} from the back face", va="center", fontsize=8, color=AC)
    ax.set_xlim(-ew / 2 - 10, ew / 2 + 70); ax.set_ylim(-12, ed + P["lid_d"] + 4)
    fig.text(0.03, 0.97, "Enclosure bottom face: drilling layout", fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.03, 0.93, "Box standing upside down on its top, back face toward you. Sideways positions from the centre line, + to the right as seen from the front.\n"
             "Solid circle: the hole to drill. Dashed circle: the outside flange of the part that goes in it.", fontsize=8.2, color=MUT, va="top")
    fig.text(0.03, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.97, 0.015, "github.com/BoujeeEnjinia1701/fieldnode", fontsize=7, color=AC, ha="right", family="monospace")
    fig.savefig(OUT / "base-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "base-holes.png")
    return res


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.2), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 72); ax.set_axis_off()
    INK, MUT = "#111827", "#4B5563"
    ax.text(2, 70, "FieldNode prototype: block-level wiring", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 66.6, "Bought modules wired at block level; no circuit board is laid out. Wire sizes are stranded copper; ferrules on every screw terminal.",
            fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, "github.com/BoujeeEnjinia1701/fieldnode", fontsize=7, color="#0F766E", ha="right", family="monospace")
    # the internal plate outline
    ax.add_patch(FancyBboxPatch((23, 12), 83, 49, boxstyle="round,pad=0.4", fc="#F8FAFC", ec="#94A3B8", lw=1, ls="--"))
    ax.text(24.5, 59.8, "On the internal plate (lifts out after unplugging the connector strip)", fontsize=8, color=MUT, va="top")
    B = {}

    def blk(key, x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8))
        ax.text(x + w / 2, y + h - 1.4, title, ha="center", va="top", fontsize=9, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 4.3, sub, ha="center", va="top", fontsize=7.2, color=MUT, linespacing=1.3)
        B[key] = (x, y, w, h)

    def wire(pts, color, lw=2.0):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)

    def lab(x, y, text, color, ha="left"):
        ax.text(x, y, text, fontsize=7.2, color=color, ha=ha, va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    RED, BLU, GRY, RF, BLK = "#B91C1C", "#1D4ED8", "#6B7280", "#374151", "#111827"
    blk("panel", 3, 44, 15, 12, "Solar panel", "6 W, 9 V class,\n1 m lead", "#1E3A8A")
    blk("chg", 27, 44, 16, 12, "Charger module", "MPPT, 1S LiFePO4,\nset to 3.6 V", "#16A34A")
    blk("prot", 50, 44, 16, 12, "Protection board", "1S LiFePO4\nthresholds", "#16A34A")
    blk("buck", 72, 44, 13, 12, "3.3 V converter", "always on", "#16A34A")
    blk("ctrl", 88, 38, 13, 18, "Controller", "STM32WL LoRa\nmodule, 16 MB\nflash, status LED", "#0F766E")
    blk("cell", 33, 24, 16, 12, "LiFePO4 cell", "3.2 V, 6 Ah, holder\nwith 5 A fuse, NTC", "#C2410C")
    blk("boost", 63, 24, 17, 12, "Port rail converters", "5 V or 12 V boost,\none per port", "#16A34A")
    blk("ptc", 86, 24, 13, 10, "Rail fuses", "resettable, 0.5 A\nhold, one per rail", "#7C3AED")
    blk("strip", 26, 14, 78, 4, "", "", "#7C3AED")
    ax.text(65, 16, "Connector strip (plug and socket): the plate unplugs here", ha="center", va="center", fontsize=8, fontweight="bold", color=INK)
    blk("ports", 107, 12, 11, 20, "", "", "#D4A017")
    ax.text(112.5, 22, "Sensor ports A, B (M12)\nand gland 2 cable", rotation=90, ha="center", va="center", fontsize=7.6, fontweight="bold", color=INK)
    blk("ant", 107, 44, 11, 12, "Antenna", "bulkhead\nand whip", RF)
    # panel: through gland 1 to the strip, then to the charger input
    wire([(10.5, 44), (10.5, 16), (26, 16)], RED); lab(11.5, 30, "panel lead through\ngland 1, 0.5 mm²", RED)
    wire([(29, 18), (29, 44)], RED); lab(28.4, 40.5, "PV in,\n0.5 mm²", RED, "right")
    # charger to protection (pack side), cell through its fuse to protection (cell side)
    wire([(43, 51), (50, 51)], RED); lab(46.5, 53, "0.75 mm²", RED, "center")
    ax.text(46.5, 49.3, "BAT to P", fontsize=6.8, color=MUT, ha="center", va="center")
    wire([(49, 30), (57, 30), (57, 44)], RED); lab(56.4, 40, "cell to B, 0.75 mm²,\n5 A fuse at the holder", RED, "right")
    wire([(39, 36), (39, 44)], GRY, 1.2); lab(38.4, 40.5, "NTC,\n0.25 mm²", GRY, "right")
    # load bus
    wire([(66, 51), (72, 51)], RED); lab(69, 53, "0.75 mm²", RED, "center")
    ax.text(69, 49.3, "load bus", fontsize=6.8, color=MUT, ha="center", va="center")
    wire([(69, 51), (69, 36)], RED); lab(69.6, 40.5, "0.5 mm²", RED)
    wire([(85, 51), (88, 51)], RED); lab(86.5, 53, "0.5 mm²", RED, "center")
    wire([(80, 29), (86, 29)], RED); lab(83, 31, "0.5 mm²", RED, "center")
    wire([(92.5, 24), (92.5, 18)], RED); lab(84, 21, "rails 0.5 mm²", RED)
    wire([(102.5, 38), (102.5, 18)], BLU); lab(99.2, 36.4, "signals\n0.25 mm²", BLU)
    wire([(91, 38), (91, 37.2), (76, 37.2), (76, 36)], GRY, 1.2); lab(76.5, 38.6, "enable, 0.25 mm²", GRY)
    wire([(101, 50), (107, 50)], RF, 1.2); lab(104, 53, "RF pigtail", RF, "center")
    wire([(104, 16), (107, 16)], BLK)
    ax.text(28, 9.6, "Safety: fuse out and cell out until the stop points in section 6 of the plan are passed. Never charge below 0 °C or above 45 °C.",
            fontsize=7.6, color="#B45309", fontweight="bold")
    ax.text(28, 6.2, "Red: power. Blue: signal (I2C, UART or RS-485, analog; port pinout still open). Grey: sensing and control. "
            "All circuits are extra-low voltage: 3.6 V cell, 12 V highest rail.", fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    what = sys.argv[1:] or ["overview", "sheets", "layouts", "joints", "steps", "wiring"]
    fns = {"overview": overview, "sheets": sheets, "layouts": layouts, "joints": joints, "steps": steps, "wiring": wiring}
    for w in what:
        r = fns[w]()
        print(w, "->", r)
