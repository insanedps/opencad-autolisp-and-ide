"""
Dialog and GUI Controls Test Script for OpenCAD Studio Python Runner.

Commands registered:
  • TESTDLG  - Full configuration dialog demonstrating vertical stack and oc.row layouts
  • TESTROW  - Compact side-by-side dimensions dialog
  • TESTALERT- Quick alert and confirm popup dialogs

Run by typing command name (e.g. `TESTDLG`, `TESTROW`, `TESTALERT`) or `PY test_dialog`.
"""

import opencad as oc

@oc.command("TESTDLG")
def test_full_dialog(*args):
    """Demonstrate full declarative modal dialog with various controls."""
    res = oc.dialog(
        "Mechanical Part Generator",
        oc.info_text("Configure dimensions and material for the parametric part:"),
        oc.row(
            part_name=oc.text("Part-001", label="Part Name"),
            material=oc.choice(["Aluminum 6061", "Steel 4140", "Brass 360", "Titanium Gr5"], default="Aluminum 6061", label="Material"),
        ),
        oc.row(
            radius=oc.number(25.0, min=1.0, max=500.0, step=0.5, label="Outer Radius (mm)"),
            inner_radius=oc.number(10.0, min=0.0, max=400.0, step=0.5, label="Bore Radius (mm)"),
        ),
        oc.row(
            part_color=oc.color("cyan", label="Display Color"),
            create_bore=oc.checkbox(True, label="Create Bore"),
        ),
        submit_label="Generate Part",
        cancel_label="Cancel",
    )

    if not res:
        oc.info("Dialog cancelled by user.")
        return

    oc.info(f"Generating part: {res.part_name} [{res.material}]")
    oc.info(f"Outer radius: {res.radius}, Bore radius: {res.inner_radius}")

    # Generate concentric circles
    center = (0.0, 0.0, 0.0)
    oc.add_circle(center, res.radius, color=res.part_color)
    if res.create_bore and res.inner_radius > 0.0:
        oc.add_circle(center, res.inner_radius, color="white")

    oc.info("Part geometry created successfully!")


@oc.command("TESTROW")
def test_row_dialog(*args):
    """Demonstrate horizontal side-by-side row controls."""
    cfg = oc.dialog(
        "Rectangle Dimensions",
        oc.row(
            width=oc.number(100.0, min=1.0, label="Width"),
            height=oc.number(50.0, min=1.0, label="Height"),
            draw_diagonals=oc.checkbox(False, label="Draw Diagonals"),
        ),
        submit_label="Draw Rectangle",
    )

    if not cfg:
        oc.info("Cancelled.")
        return

    w = cfg.width
    h = cfg.height
    oc.add_line((0.0, 0.0), (w, 0.0))
    oc.add_line((w, 0.0), (w, h))
    oc.add_line((w, h), (0.0, h))
    oc.add_line((0.0, h), (0.0, 0.0))

    if cfg.draw_diagonals:
        oc.add_line((0.0, 0.0), (w, h), color="red")
        oc.add_line((0.0, h), (w, 0.0), color="red")

    oc.info(f"Rectangle ({w} x {h}) created!")


@oc.command("TESTALERT")
def test_alerts(*args):
    """Demonstrate quick alert and confirm dialogs."""
    oc.alert("Welcome to OpenCAD Studio Plugin GUI Dialogs!", title="Welcome")
    
    ok = oc.confirm("Would you like to generate a sample circle at origin?", title="Generate Geometry")
    if ok:
        oc.add_circle((0.0, 0.0, 0.0), 50.0, color="green")
        oc.info("Sample circle created at (0, 0, 0).")
    else:
        oc.info("Circle generation skipped.")


@oc.command("TESTFIELDS")
def test_fields_dialog(*args):
    """Demonstrate generic high-level properties section using oc.fields."""
    cfg = oc.dialog(
        "Shaft Specifications",
        oc.fields(
            "Primary Dimensions",
            diameter=oc.number(40.0, min=5.0, label="Shaft Diameter (mm)"),
            length=oc.number(120.0, min=10.0, label="Total Length (mm)"),
            chamfer=oc.number(2.0, min=0.0, label="Chamfer Size (mm)"),
        ),
        oc.fields(
            "Material & Finish",
            material=oc.choice(["AISI 1045", "Stainless 304", "Brass C360"], default=0, label="Alloy"),
            heat_treated=oc.checkbox(True, label="Heat Treated"),
        ),
        submit_label="Create Shaft",
    )
    if not cfg:
        oc.info("Shaft dialog cancelled.")
        return

    oc.info(f"Primary dimensions: Diameter={cfg.primary_dimensions.diameter}, Length={cfg.primary_dimensions.length}")
    oc.info(f"Material: {cfg.material_finish.material}, Heat treated: {cfg.material_finish.heat_treated}")
    oc.info("Shaft specifications recorded!")


@oc.command("TESTTABLE")
def test_table_dialog(*args):
    """Demonstrate interactive editable data table using oc.table."""
    res = oc.dialog(
        "Bill of Materials Editor",
        oc.info_text("Edit parts list, add or remove items:"),
        bom=oc.table(
            headers=["Part Name", "Qty", "Material", "Notes"],
            rows=[
                ["Mounting Bracket", "2", "Steel 4140", "Powder coated"],
                ["Hex Bolt M8x30", "8", "Grade 8.8", "Zinc plated"],
                ["Lock Nut M8", "8", "Steel", "Nylon insert"],
                ["Flat Washer M8", "16", "Steel", "Standard DIN 125"],
            ],
            label="Assembly BOM Table",
            allow_add=True,
            allow_delete=True,
        ),
        width=600.0,
        submit_label="Save BOM",
    )
    if not res:
        oc.info("Table dialog cancelled.")
        return

    oc.info(f"BOM submitted with {len(res.bom)} items:")
    for row in res.bom:
        oc.info(f"  • {row[0]}: Qty={row[1]}, Material={row[2]} ({row[3]})")


def run(args):
    test_full_dialog(*args)


if __name__ == "__main__":
    test_full_dialog()
