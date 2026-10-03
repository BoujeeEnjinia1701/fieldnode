"""FieldNode general arrangement sheet FND-DWG-001, Rev P4 (TRL 3; FND-DDR-002, FND-DDR-003 and FND-DEC-001 applied).

Run from the repo root:  python cad/src/sheets.py
Writes cad/drawings/FND-DWG-001.svg, .pdf and .png from the parametric model in
cad/src/model.py with .kit/drawing.py. Dimensions are taken from PARAMS and derived(), so
they follow any parameter change. The concept blueprint in media/ is FND-DWG-010.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from drawing import Sheet, _viewbox, _t, M, TB_Y, INK, MUTED  # noqa: E402
from model import PARAMS as P, assembly, derived, bracket_geometry, shield_geometry  # noqa: E402

DATE = "2026-09-25"
DATE_P3 = "2026-09-30"
DATE_P4 = "2026-10-02"


def safe_project_views(part, workdir, line_weight=0.35):
    """Same views as drawing.project_views, but edge by edge, so that a degenerate edge from the
    hidden-line projection is skipped instead of stopping the export."""
    from build123d import ExportSVG, LineType, Unit
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    bb = part.bounding_box()
    c = bb.center()
    d = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
    setups = {"front": ((c.X, c.Y - d, c.Z), (0, 0, 1)), "top": ((c.X, c.Y, c.Z + d), (0, 1, 0)),
              "right": ((c.X + d, c.Y, c.Z), (0, 0, 1)), "iso": ((c.X + d, c.Y - d, c.Z + d * 0.8), (0, 0, 1))}
    out, skipped = {}, 0
    for name, (origin, up) in setups.items():
        visible, hidden = part.project_to_viewport(origin, up, (c.X, c.Y, c.Z))
        ex = ExportSVG(unit=Unit.MM, line_weight=line_weight)
        ex.add_layer("Visible", line_color=0x111827)
        ex.add_layer("Hidden", line_color=0x6B7280, line_type=LineType.ISO_DASH, line_weight=line_weight / 2)
        for layer, edges in (("Visible", visible), ("Hidden", hidden if name != "iso" else [])):
            for e in edges:
                try:
                    ex.add_shape(e, layer=layer)
                except (AssertionError, ValueError, ZeroDivisionError):
                    skipped += 1
        p = workdir / f"{name}.svg"
        ex.write(str(p))
        out[name] = p
    print(f"projected views; skipped {skipped} degenerate edges")
    return out


def ortho_cells(sheet, views, names=("front", "top", "right")):
    """Repeat Sheet.add_ortho's layout arithmetic to find where each view lands (x, y, w, h)."""
    ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
    gap, lab = 14, 12
    dims = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
    fw, fh = dims["front"]
    tw, th = dims["top"]
    rw, rh = dims["right"]
    k = sheet.scale
    dl = 11                     # room add_ortho leaves for its overall dimensions (kit 1.7)
    ax += (aw - (k * (max(fw, tw) + rw) + gap + dl)) / 2 + dl
    ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab + dl)) / 2 + dl
    colw = k * max(fw, tw)
    front_y = ay + k * th + lab + gap
    row_h = k * max(fh, rh)
    return {"top": (ax, ay, colw, k * th), "front": (ax, front_y, colw, row_h),
            "right": (ax + colw + gap, front_y, k * rw, row_h)}


def dim_h(x1, x2, y, text):
    a = 1.4
    return [f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x1:.2f} {y:.2f} l{a} -0.5 l0 1 Z" fill="{INK}"/>',
            f'<path d="M{x2:.2f} {y:.2f} l{-a} -0.5 l0 1 Z" fill="{INK}"/>',
            _t((x1 + x2) / 2, y - 1.0, text, 2.3, 400, INK, "middle", mono=True)]


def dim_v(x, y1, y2, text, side=-1):
    a = 1.4
    cx, cy = x + side * 1.0, (y1 + y2) / 2
    return [f'<line x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x:.2f} {y1:.2f} l-0.5 {a} l1 0 Z" fill="{INK}"/>',
            f'<path d="M{x:.2f} {y2:.2f} l-0.5 {-a} l1 0 Z" fill="{INK}"/>',
            f'<g transform="rotate(-90 {cx:.2f} {cy:.2f})">{_t(cx, cy, text, 2.3, 400, INK, "middle", mono=True)}</g>']


def ext(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.13"/>'


def leader(x1, y1, x2, y2, text, anchor="start"):
    return [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.15"/>',
            f'<circle cx="{x1:.2f}" cy="{y1:.2f}" r="0.5" fill="{INK}"/>',
            _t(x2 + (1 if anchor == "start" else -1), y2 + 0.8, text, 2.1, 400, INK, anchor)]


def main():
    D = derived(P)
    work = ROOT / "cad" / "drawings" / "_views"
    asm = assembly(with_pole=True)
    views = safe_project_views(asm, work)
    bb = asm.bounding_box()
    s = Sheet(project="FieldNode", title="General arrangement", dwg_no="FND-DWG-001", rev="P4",
              author="Amish Chadha", date=DATE_P4, scale=0.1, theme="technical",
              material="Bought-in parts per bom/bom.csv; aluminium bracket and plate. PRELIMINARY, NOT FOR FABRICATION",
              revisions=[("P1", "Preliminary GA for TRL 3 (from cad/src/model.py)", DATE, "AC"),
                         ("P2", "FND-DDR-002: 9 V class panel; sun shield option (14)", DATE, "AC"),
                         ("P3", "FND-DDR-003: design for construction", DATE_P3, "AC"),
                         ("P4", "Port pinout, programming header (7), 915 MHz whip", DATE_P4, "AC")])
    s.add_ortho(views)
    k = s.scale
    c = ortho_cells(s, views)
    L = [_t(M + 12, M + 12, "PRELIMINARY, NOT FOR FABRICATION", 3.0, 600, INK)]
    ew, ed, eh = P["enc"]
    zl, zu = D["clamps"]

    # front view (from -Y): X to the right, Z up
    x, y, w, h = c["front"]
    X = lambda mx: x + (mx - bb.min.X) * k   # noqa: E731
    Z = lambda mz: y + h - (mz - bb.min.Z) * k   # noqa: E731
    xl = X(bb.min.X) - 17
    L += [ext(X(-ew / 2), Z(D["enc_bot"]), xl - 1, Z(D["enc_bot"])), ext(X(-ew / 2), Z(D["enc_top"]), xl - 1, Z(D["enc_top"]))]
    L += dim_v(xl, Z(D["enc_top"]), Z(D["enc_bot"]), f"{eh:.0f}")
    L += [ext(X(-P['plate'][0] / 2), Z(zl), xl - 15, Z(zl)), ext(X(-P['plate'][0] / 2), Z(zu), xl - 15, Z(zu))]
    L += dim_v(xl - 14, Z(zu), Z(zl), f"{D['clamp_span']:.0f} clamps")
    yd = Z(D["whip_tip"] - 12)
    L += dim_h(X(-ew / 2), X(ew / 2), yd, f"{ew:.0f}")
    L += [ext(X(-ew / 2), Z(D["enc_bot"]), X(-ew / 2), yd + 1), ext(X(ew / 2), Z(D["enc_bot"]), X(ew / 2), yd + 1)]
    L += dim_h(X(-P["panel"][0] / 2), X(P["panel"][0] / 2), Z(D["overall_top"]) - 4, f"{P['panel'][0]:.0f} panel")
    ax_ = P["pens"]["antenna"][0]
    L += leader(X(ax_), Z(D["whip_tip"] + 40), X(ax_) + 6, Z(D["whip_tip"] + 10), "915 MHZ WHIP (9)")
    px_ = P["pens"]["port_a"][0]
    L += leader(X(px_), Z(D["enc_bot"] - 14), X(-ew / 2) - 12, Z(D["enc_bot"] - 45), "PORTS A (LEFT) AND B, M12 5-PIN (10)", "end")
    gx_ = P["pens"]["gland_1"][0]
    L += leader(X(gx_), Z(D["enc_bot"] - 8), X(gx_) - 2, Z(D["enc_bot"] - 120), "2 x M16 GLANDS (3)", "end")

    # top view (from +Z): X to the right, Y up the sheet
    x, y, w, h = c["top"]
    Xt = lambda mx: x + (mx - bb.min.X) * k   # noqa: E731
    Yt = lambda my: y + h - (my - bb.min.Y) * k   # noqa: E731
    L += leader(Xt(0), Yt(0), Xt(bb.max.X) + 4, Yt(0) - 2, f"POLE AXIS, {P['pole_od']} OD (40 TO 60)")
    L.append(_t(Xt(bb.max.X) + 4, Yt(bb.min.Y), "NODE FACES -Y (TOWARD THE EQUATOR)", 1.9, 400, MUTED, "start"))

    # right view (from +X): +Y appears to the left... measured as drawn by project_to_viewport
    x, y, w, h = c["right"]
    Yr = lambda my: x + w - (my - bb.min.Y) * k   # noqa: E731
    Zr = lambda mz: y + h - (mz - bb.min.Z) * k   # noqa: E731
    yb = Zr(D["whip_tip"] - 12)
    L += dim_h(min(Yr(D["enc_front"]), Yr(D["enc_back"])), max(Yr(D["enc_front"]), Yr(D["enc_back"])), yb, f"{ed:.0f}")
    L += [ext(Yr(D["enc_front"]), Zr(D["enc_bot"]), Yr(D["enc_front"]), yb + 1), ext(Yr(D["enc_back"]), Zr(D["enc_bot"]), Yr(D["enc_back"]), yb + 1)]
    xr = max(Yr(bb.min.Y), Yr(bb.max.Y)) + 5
    L += [ext(Yr(0), Zr(D["overall_top"]), xr + 1, Zr(D["overall_top"])), ext(Yr(0), Zr(D["enc_bot"]), xr + 1, Zr(D["enc_bot"]))]
    L += dim_v(xr, Zr(D["overall_top"]), Zr(D["enc_bot"]), f"{D['overall_top'] - D['enc_bot']:.0f}", side=1)
    L.append(_t(Yr(D["panel_cy"]) - 14, Zr(D["overall_top"]) - 5, f"PANEL TILT {P['tilt']:.0f} DEG", 2.0, 400, INK, "middle"))

    s._layers += L
    s.add_svg(views["iso"], 276, 40, 140, 84, label="Isometric view", sublabel="Not to scale; grey pole stub is site supplied")
    bg = bracket_geometry()
    SG = shield_geometry()
    s.add_notes("Main dimensions and interfaces (mm)", [
        f"Enclosure IP65 {ew:.0f} x {ed:.0f} x {eh:.0f} (W x D x H); base {P['z0']:,.0f} above ground",
        f"Panel 6 W 9 V class, {P['panel'][0]:.0f} x {P['panel'][1]:.0f}, tilt {P['tilt']:.0f} deg; top {D['overall_top']:,.0f} above ground",
        f"Panel overhangs lid by {D['overhang_front']:.0f}; front edge {D['clear_top']:.0f} above enclosure",
        f"Back plate {P['plate'][0]:.0f} x {P['plate'][1]:.0f} x {P['plate'][2]:.0f} Al; V-blocks {P['vblock'][0]:.0f} x {P['vblock'][1]:.0f} x {P['vblock'][2]:.0f}, 90 deg V",
        f"Band clamps {P['band'][0]:.0f} wide, {D['clamp_span']:.0f} apart; poles 40 to 60 OD",
        f"Bracket bar {P['bar'][0]:.0f} x {P['bar'][1]:.0f}: posts {bg['post']['L']:.0f}, struts {bg['strut']['L']:.0f} between holes",
        "Enclosure on 4 lugs, M5; bracket on 30 x 30 x 3 angle clips, M6",
        f"Bottom face: 2 rows, {P['pen_rows'][0]:.0f} and {P['pen_rows'][1]:.0f} in from the back face",
        f"Whip 915 MHz (US915), {P['whip'][1]:.0f} long; tip {D['whip_tip']:,.0f} above ground",
        f"Option (14), not shown: shield {SG['w']:.0f} x {SG['d']:.0f} x {SG['h']:.0f}, {P['shield_gap']:.0f} gap, 4 thumb screws",
        "Ports A and B (10), M12 5-pin A-coded, pin positions per maker:",
        "  1 switched rail, 2 data A, 3 ground, 4 data B, 5 analog",
        f"Serial header (7) on the power board, pins {D['hdr_depth']:.0f} in from box front (lid off)",
        "Third-angle; front view from -Y; pole on Z axis; (n) = BOM line",
    ], x=276, y=135, width=146)
    out = s.save(ROOT / "cad" / "drawings" / "FND-DWG-001")
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {out} and .pdf, .png at scale 1:{1 / k:g}")


if __name__ == "__main__":
    main()
