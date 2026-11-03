"""
Rubber-Band Preview Modes Test Script for OpenCAD Studio.

Commands registered:
  • RBLINE    - Test Line rubber-band (default cyan & custom red)
  • RBCIRCLE  - Test Circle rubber-band (centered at picked point)
  • RBARC3P   - Test 3-Point Arc rubber-band (circumcircle passing through 2 points and cursor)
  • RBARCCS   - Test Center-Start Arc rubber-band (sweeping from start to cursor angle)
  • RBTARC    - Test Tangent Arc rubber-band (smooth tangent arc from a base point)
  • RBCUSTOM  - Test Custom rubber-band (box preview)
  • RBALL     - Run all preview modes sequentially

Run by typing any command name above (e.g. `RBLINE`, `RBCIRCLE`, `RBALL`) or `PY test_rubberband`.
"""

import math
import opencad as oc

@oc.command("RBLINE")
def test_rb_line(*args):
    """Test line rubber-band with default cyan and custom red colors."""
    oc.info("=== Testing Line Rubber-Band ===")
    p1 = oc.get_point("Pick line start point: ")
    if not p1:
        oc.info("Cancelled.")
        return

    # 1. Default cyan line rubber-band using base_point shorthand
    oc.info("Move cursor to see default CYAN line rubber-band.")
    p2 = oc.get_point("Pick second point (Cyan): ", base_point=p1)
    if not p2:
        oc.info("Cancelled.")
        return
    oc.add_line(p1, p2)

    # 2. Custom color line rubber-band using color argument
    oc.info("Move cursor to see custom RED line rubber-band.")
    p3 = oc.get_point("Pick third point (Red): ", base_point=p2, color="red")
    if p3:
        oc.add_line(p2, p3, color="red")
        oc.info("Line rubber-band test complete!")


@oc.command("RBCIRCLE")
def test_rb_circle(*args):
    """Test circle rubber-band."""
    oc.info("=== Testing Circle Rubber-Band ===")
    center = oc.get_point("Pick circle center: ")
    if not center:
        oc.info("Cancelled.")
        return

    oc.info("Move cursor to see dynamic YELLOW CIRCLE rubber-band resizing in real time.")
    rim_pt = oc.get_point(
        "Pick radius point: ",
        rubber_band=("circle", center),
        color="yellow",
    )
    if not rim_pt:
        oc.info("Cancelled.")
        return

    radius = math.hypot(rim_pt[0] - center[0], rim_pt[1] - center[1])
    if radius > 1e-6:
        oc.add_circle(center, radius, color="yellow")
        oc.info(f"Circle created with radius {radius:.2f}!")


@oc.command("RBARC3P")
def test_rb_arc3p(*args):
    """Test 3-point arc rubber-band."""
    oc.info("=== Testing 3-Point Arc Rubber-Band ===")
    p1 = oc.get_point("Pick first arc point: ")
    if not p1:
        return
    p2 = oc.get_point("Pick second arc point: ", base_point=p1)
    if not p2:
        return

    oc.info("Move cursor to see MAGENTA 3-POINT ARC rubber-band passing through all 3 points.")
    p3 = oc.get_point(
        "Pick third arc point: ",
        rubber_band=("arc_3p", p1, p2),
        color="magenta",
    )
    if not p3:
        return

    # Solve circumcircle to add arc entity
    d = 2 * (p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1]))
    if abs(d) > 1e-9:
        ux = ((p1[0]**2 + p1[1]**2)*(p2[1] - p3[1]) + (p2[0]**2 + p2[1]**2)*(p3[1] - p1[1]) + (p3[0]**2 + p3[1]**2)*(p1[1] - p2[1])) / d
        uy = ((p1[0]**2 + p1[1]**2)*(p3[0] - p2[0]) + (p2[0]**2 + p2[1]**2)*(p1[0] - p3[0]) + (p3[0]**2 + p3[1]**2)*(p2[0] - p1[0])) / d
        r = math.hypot(p1[0] - ux, p1[1] - uy)
        a1 = math.atan2(p1[1] - uy, p1[0] - ux)
        a3 = math.atan2(p3[1] - uy, p3[0] - ux)
        if a1 < 0: a1 += 2*math.pi
        if a3 < 0: a3 += 2*math.pi
        oc.add_arc((ux, uy, 0.0), r, min(a1, a3), max(a1, a3), color="magenta")
    oc.info("3-Point Arc test complete!")


@oc.command("RBARCCS")
def test_rb_arccs(*args):
    """Test Center-Start arc rubber-band."""
    oc.info("=== Testing Center-Start Arc Rubber-Band ===")
    center = oc.get_point("Pick arc center: ")
    if not center:
        return
    start = oc.get_point("Pick arc start point: ", base_point=center)
    if not start:
        return

    oc.info("Move cursor to see GREEN CENTER-START ARC sweeping as cursor moves.")
    end = oc.get_point(
        "Pick endpoint / sweep angle: ",
        rubber_band=("arc_center_start", center, start),
        color="green",
    )
    if not end:
        return

    r = math.hypot(start[0] - center[0], start[1] - center[1])
    sa = math.atan2(start[1] - center[1], start[0] - center[0])
    ea = math.atan2(end[1] - center[1], end[0] - center[0])
    if sa < 0: sa += 2*math.pi
    if ea < 0: ea += 2*math.pi
    oc.add_arc(center, r, min(sa, ea), max(sa, ea), color="green")
    oc.info("Center-Start Arc test complete!")


@oc.command("RBTARC")
def test_rb_tarc(*args):
    """Test standalone Tangent Arc rubber-band."""
    oc.info("=== Testing Tangent Arc Rubber-Band ===")
    start = oc.get_point("Pick tangent arc start point: ")
    if not start:
        return
    tangent_ref = oc.get_point("Pick direction for initial tangent: ", base_point=start)
    if not tangent_ref:
        return

    tx = tangent_ref[0] - start[0]
    ty = tangent_ref[1] - start[1]
    tlen = math.hypot(tx, ty)
    if tlen < 1e-9:
        oc.info("Direction cannot be zero length.")
        return
    tangent = (tx / tlen, ty / tlen, 0.0)

    oc.info("Move cursor to see CYAN TANGENT ARC rubber-band.")
    end = oc.get_point(
        "Pick endpoint of tangent arc: ",
        rubber_band=("tangent_arc", start, tangent),
        color="cyan",
    )
    if not end:
        return

    # Solve tangent arc center
    qx = end[0] - start[0]
    qy = end[1] - start[1]
    qlen = math.hypot(qx, qy)
    nx = -tangent[1]
    ny = tangent[0]
    dot = qx * nx + qy * ny
    if abs(dot) > 1e-9:
        h = (qlen * qlen) / (2.0 * dot)
        cx = start[0] + h * nx
        cy = start[1] + h * ny
        r = abs(h)
        a_start = math.atan2(start[1] - cy, start[0] - cx)
        a_end = math.atan2(end[1] - cy, end[0] - cx)
        if a_start < 0: a_start += 2*math.pi
        if a_end < 0: a_end += 2*math.pi
        if h > 0:
            oc.add_arc((cx, cy, 0.0), r, a_start, a_end, color="cyan")
        else:
            oc.add_arc((cx, cy, 0.0), r, a_end, a_start, color="cyan")
    oc.info("Tangent Arc test complete!")


@oc.command("RBCUSTOM")
def test_rb_custom(*args):
    """Test custom rectangle/box rubber-band preview."""
    oc.info("=== Testing Rectangle / Box Rubber-Band ===")
    c1 = oc.get_point("Pick first corner: ")
    if not c1:
        return

    oc.info("Move cursor to see dynamic ORANGE RECTANGLE box preview.")
    c2 = oc.get_point(
        "Pick opposite corner: ",
        rubber_band=("rectangle", c1),
        color="orange",
    )
    if not c2:
        return
    oc.add_line((c1[0], c1[1]), (c2[0], c1[1]), color="orange")
    oc.add_line((c2[0], c1[1]), (c2[0], c2[1]), color="orange")
    oc.add_line((c2[0], c2[1]), (c1[0], c2[1]), color="orange")
    oc.add_line((c1[0], c2[1]), (c1[0], c1[1]), color="orange")
    oc.info("Rectangle box created!")


@oc.command("RBALL")
def test_all(*args):
    """Run all rubber-band tests in sequence."""
    test_rb_line()
    test_rb_circle()
    test_rb_arc3p()
    test_rb_arccs()
    test_rb_tarc()
    test_rb_custom()
    oc.info("All rubber-band tests completed!")


def run(args):
    test_all(*args)


if __name__ == "__main__":
    test_all()
