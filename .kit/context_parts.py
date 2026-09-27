"""Shared scale-context parts for renders: a smooth clay forearm and hand.

Use in cad/src/product_model.py for wearables and handheld devices:

    import sys; sys.path.insert(0, ".kit")
    from context_parts import forearm_hand
    arm = forearm_hand(side="left", pose="flat")          # wrist at the origin, hand toward +X, back of hand +Z
    arm = Pos(x, y, z) * Rot(0, 0, 90) * arm               # place it with build123d locations

Coordinates in mm. The wrist centre is at the origin, the forearm runs along -X to the elbow, the hand
along +X, the back of the hand faces +Z. side="left" puts the thumb at +Y (palm down, as seen from above),
side="right" at -Y. pose="flat" rests the hand on a table; pose="grip" curls the fingers around a
cylinder of diameter grip_d centred at (grip_x, 0, -grip_d / 2 - 5) so a handle can be placed there.
Proportions follow an average adult (forearm 250 mm, hand 185 mm); this is a render prop, not anatomy.
"""
from math import radians, sin, cos
from build123d import (Plane, Ellipse, Circle, Sketch, loft, Solid, Sphere, Cylinder, Pos, Rot, Compound,
                       Vector, Location)


def _ellipse_section(x, a, b, z=0.0):
    pl = Plane(origin=(x, 0, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return pl * Ellipse(a / 2, b / 2)


def _capsule(p0, p1, r0, r1):
    """Tapered capsule from p0 to p1 (radii r0, r1)."""
    p0, p1 = Vector(*p0), Vector(*p1)
    d = p1 - p0
    L = d.length
    pl0 = Plane(origin=p0, z_dir=d.normalized())
    pl1 = Plane(origin=p1, z_dir=d.normalized())
    body = loft([pl0 * Circle(r0), pl1 * Circle(r1)])
    return body + Pos(*p0) * Sphere(r0) + Pos(*p1) * Sphere(r1)


def _finger(base, length, r, pose, side_sign, spread_deg=0.0, curl=None):
    """Three-segment finger from base, pointing +X, curled toward -Z in the grip pose."""
    segs = [0.45, 0.30, 0.25]
    if curl is None:
        curl = [8, 10, 8] if pose == "flat" else [55, 70, 60]
    pts = [Vector(*base)]
    ang = 0.0
    yaw = radians(spread_deg)
    for s, c in zip(segs, curl):
        ang += radians(c)
        step = length * s
        dx = step * cos(ang) * cos(yaw)
        dy = step * cos(ang) * sin(yaw)
        dz = -step * sin(ang)
        pts.append(pts[-1] + Vector(dx, dy, dz))
    shape = None
    for i in range(3):
        r0 = r * (1.0 - 0.08 * i)
        r1 = r * (1.0 - 0.08 * (i + 1))
        seg = _capsule(tuple(pts[i]), tuple(pts[i + 1]), r0, r1)
        shape = seg if shape is None else shape + seg
    return shape


def forearm_hand(side="left", pose="flat", forearm_len=250.0, grip_d=40.0, include_forearm=True):
    s = 1 if side == "left" else -1
    parts = []
    if include_forearm:
        # forearm: elbow (-L) to wrist (0), elliptical sections, flatter at the wrist
        secs = [(-forearm_len, 78, 68), (-0.7 * forearm_len, 80, 66), (-0.35 * forearm_len, 70, 52), (0.0, 60, 40)]
        parts.append(loft([_ellipse_section(x, a, b) for x, a, b in secs]))
    # palm: wrist to knuckles, widening and flattening
    palm_secs = [(0.0, 60, 40), (25, 76, 34), (60, 84, 30), (88, 82, 26)]
    palm = loft([_ellipse_section(x, a, b, z=0.0) for x, a, b in palm_secs])
    parts.append(palm)
    # fingers: index to little, from the knuckle line
    fingers = [(+0.33, 76, 9.2, 4), (+0.11, 84, 9.4, 1), (-0.11, 80, 9.0, -2), (-0.33, 64, 8.0, -6)]
    for yf, L, r, spread in fingers:
        base = (86, s * yf * 80 * 0.95, -2.0)
        parts.append(_finger(base, L, r, pose, s, spread_deg=s * spread))
    # thumb: from the side of the palm, angled forward and down
    tb = (22, s * 34, -6.0)
    thumb_curl = [20, 12, 10] if pose == "flat" else [35, 45, 40]
    parts.append(_finger(tb, 62, 10.5, pose, s, spread_deg=s * 38, curl=thumb_curl))
    shape = parts[0]
    for p in parts[1:]:
        try:
            shape = shape + p
        except Exception:
            shape = Compound(children=[shape, p])
    if not shape.is_valid:
        shape = Compound(children=parts)
    return shape


if __name__ == "__main__":
    import time
    for pose in ("flat", "grip"):
        t = time.time()
        h = forearm_hand(pose=pose)
        bb = h.bounding_box()
        print(pose, h.is_valid, round(bb.size.X), round(bb.size.Y), round(bb.size.Z), f"{time.time()-t:.1f}s")
