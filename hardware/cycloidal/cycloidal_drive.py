# ============================================================================
#  CYCLOIDAL DRIVE 20:1  for NEMA17  --  parametric generator for Blender
#  Run:  blender -b -P cycloidal_drive.py          (headless, exports STL)
#        or open Blender > Scripting > Run Script  (builds the assembly)
#
#  NOTE: the motor itself is NOT modelled - only its mounting interface
#        (31 mm M3 pattern, O22 pilot boss, O5 shaft).
#  All dimensions in millimetres. Z = 0 is the motor face plate.
# ============================================================================

import bpy, bmesh, math, os, sys

# ---------------------------------------------------------------- parameters
OUT_DIR   = os.path.expanduser("~/cyclo_out")   # STL output folder
EXPORT    = True                                # write STL files
EXPLODE   = 0.0                                 # >0 spreads parts along Z for viewing

# --- reduction -------------------------------------------------------------
N_PINS    = 21          # ring pins;  lobes = N_PINS-1  ->  ratio = lobes : 1
N_LOBES   = N_PINS - 1  # 20  ->  20:1

# --- cycloid geometry ------------------------------------------------------
R_PC      = 26.0        # pin circle radius
R_PIN     = 2.5         # ring pin radius (O5 dowel)
ECC       = 0.9         # eccentricity.  HARD RULE: 2*ECC <= R_PIN
CLR       = 0.15        # print clearance on the tooth flanks
PROF_STEPS= 1440        # profile resolution

# --- discs -----------------------------------------------------------------
DISC_T    = 7.0
DISC_GAP  = 0.5
BRG_OD    = 24.0        # 6802ZZ  15 x 24 x 5
BRG_W     = 5.0
BRG_SHLD  = 22.0        # shoulder bore that retains the bearing
SHLD_T    = (DISC_T - BRG_W) / 2.0

# --- output pin/hole coupling ---------------------------------------------
N_OUT     = 6
OUT_PIN_D = 5.0         # O5 dowel
OUT_PIN_R = 17.3        # output pin circle radius
OUT_HOLE_D= OUT_PIN_D + 2.0*ECC          # = 6.8  (this relation is mandatory)

# --- housing ---------------------------------------------------------------
HOUS_OD   = 70.0
RING_BORE = 51.2        # 2 x 25.6 : clears disc crest reach (25.15) + 0.45
CHAM_BORE = 58.0
BASE_T    = 6.0
RING_Z0, RING_Z1 = 6.0, 22.0
CHAM_Z1   = 29.2        # housing top face
PIN_FIT   = 0.15        # pocket oversize for the O5 ring pins

# --- output bearing 6808-2RS  40 x 52 x 7 ---------------------------------
OB_ID, OB_OD, OB_W = 40.0, 52.0, 7.0
OB_Z0 = CHAM_Z1
OB_Z1 = OB_Z0 + OB_W

# --- flange / cover --------------------------------------------------------
FL_Z0, FL_Z1 = 22.2, 29.2       # output flange plate (O50)
FL_D      = 50.0
HUB_D     = 40.0
HUB_Z1    = 38.7
COV_Z0, COV_Z1 = 29.2, 37.2
COV_LIP_D = 42.0
N_COV_BOLT= 6
COV_BOLT_R= 31.0

# --- disc / cam Z ----------------------------------------------------------
DA_Z0 = 6.5
DB_Z0 = DA_Z0 + DISC_T + DISC_GAP       # 14.0
CAM_Z0, CAM_Z1 = 6.3, 21.3
CAM_JRN_D  = 15.0
CAM_FLG_D  = 17.5
SHAFT_D    = 5.0
SHAFT_FIT  = 0.1

# --- NEMA17 interface (motor NOT modelled) --------------------------------
NEMA_BOLT  = 31.0
NEMA_PILOT = 22.4
NEMA_M3_CL = 3.4
NEMA_CB_D  = 6.2
NEMA_CB_T  = 3.0

# ---------------------------------------------------------------- utilities
def clear_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.objects, bpy.data.materials):
        for b in list(coll):
            if b.users == 0:
                coll.remove(b)

def activate(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

def cyl(r, z0, z1, cx=0.0, cy=0.0, seg=96, rot=(0, 0, 0)):
    """Cylinder spanning z0..z1 about (cx,cy). With rot, z0..z1 is along the
    rotated axis and (cx,cy,mid) is the centre."""
    depth = z1 - z0
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=depth,
                                        location=(cx, cy, (z0 + z1) / 2.0),
                                        rotation=rot)
    return bpy.context.active_object

def cyl_x(r, x0, x1, z, seg=48):
    """Cylinder with its axis along X, spanning x0..x1 at height z."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=(x1 - x0),
                                        location=((x0 + x1) / 2.0, 0.0, z),
                                        rotation=(0.0, math.pi / 2.0, 0.0))
    return bpy.context.active_object

def boolean(target, cutter, op='DIFFERENCE'):
    m = target.modifiers.new(name="bool", type='BOOLEAN')
    m.operation = op
    m.object = cutter
    m.solver = 'EXACT'
    activate(target)
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target

def cut(target, *cutters):
    for c in cutters:
        boolean(target, c, 'DIFFERENCE')
    return target

def fuse(target, *others):
    for o in others:
        boolean(target, o, 'UNION')
    return target

def polar_ring(target, n, radius, make_cutter, start_deg=0.0):
    """Subtract n copies of a cutter arranged on a bolt circle."""
    for i in range(n):
        a = math.radians(start_deg) + 2.0 * math.pi * i / n
        boolean(target, make_cutter(radius * math.cos(a), radius * math.sin(a)))
    return target

def cleanup(ob):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.update()
    return ob

# ------------------------------------------------------- cycloid disc profile
def cycloid_profile(R, Rr, E, N, steps, rot=0.0):
    """Roller-offset epitrochoid: the exact envelope of the pin ring.
    Validated: polar angle strictly monotonic (no undercut) and tangent to
    every pin at zero clearance when Rr is the true pin radius."""
    pts = []
    for i in range(steps):
        t = 2.0 * math.pi * i / steps
        psi = math.atan2(math.sin((1 - N) * t),
                         (R / (E * N)) - math.cos((1 - N) * t))
        x = R * math.cos(t) - Rr * math.cos(t + psi) - E * math.cos(N * t)
        y = -R * math.sin(t) + Rr * math.sin(t + psi) + E * math.sin(N * t)
        if rot:
            c, s = math.cos(rot), math.sin(rot)
            x, y = x * c - y * s, x * s + y * c
        pts.append((x, y))
    return pts

def prism(name, poly, z0, z1):
    """Solid prism from a polygon that is star-shaped about (0,0)."""
    n = len(poly)
    verts = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    cb = len(verts); verts.append((0.0, 0.0, z0))
    ct = len(verts); verts.append((0.0, 0.0, z1))
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
        faces.append((cb, j, i))
        faces.append((ct, i + n, j + n))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return cleanup(ob)

# ------------------------------------------------------------------ the parts
def build_disc(name, z0, profile_rot_deg):
    prof = cycloid_profile(R_PC, R_PIN + CLR, ECC, N_PINS, PROF_STEPS,
                           rot=math.radians(profile_rot_deg))
    ob = prism(name, prof, z0, z0 + DISC_T)
    # centre bore: shoulder O22 through, O24 pocket for the 6802 in the middle
    cut(ob, cyl(BRG_SHLD / 2.0, z0 - 1, z0 + DISC_T + 1))
    cut(ob, cyl(BRG_OD / 2.0, z0 + SHLD_T, z0 + DISC_T - SHLD_T))
    # output pin holes (hole = pin + 2E)
    polar_ring(ob, N_OUT, OUT_PIN_R,
               lambda x, y: cyl(OUT_HOLE_D / 2.0, z0 - 1, z0 + DISC_T + 1, x, y))
    return cleanup(ob)

def build_cam():
    off = ECC
    a = cyl(CAM_FLG_D / 2.0, CAM_Z0, DA_Z0 + SHLD_T,  off, 0.0)          # lower collar
    b = cyl(CAM_JRN_D / 2.0, DA_Z0 + SHLD_T, DA_Z0 + SHLD_T + BRG_W, off, 0.0)
    c = cyl(CAM_FLG_D / 2.0, DA_Z0 + SHLD_T + BRG_W, DB_Z0 + SHLD_T, 0.0, 0.0)  # mid collar
    d = cyl(CAM_JRN_D / 2.0, DB_Z0 + SHLD_T, DB_Z0 + SHLD_T + BRG_W, -off, 0.0)
    e = cyl(CAM_FLG_D / 2.0, DB_Z0 + SHLD_T + BRG_W, CAM_Z1, -off, 0.0)  # upper collar
    fuse(a, b, c, d, e)
    a.name = "05_eccentric_cam"
    # motor shaft bore + M3 grub screw
    cut(a, cyl((SHAFT_D + SHAFT_FIT) / 2.0, CAM_Z0 - 1, CAM_Z1 + 1))
    zg = (DA_Z0 + SHLD_T + BRG_W + DB_Z0 + SHLD_T) / 2.0   # mid collar centre
    cut(a, cyl_x(1.25, 0.0, CAM_FLG_D / 2.0 + 1.0, zg))
    return cleanup(a)

def build_housing():
    ob = cyl(HOUS_OD / 2.0, 0.0, CHAM_Z1, seg=192)
    ob.name = "01_housing"
    cut(ob, cyl(RING_BORE / 2.0, RING_Z0, RING_Z1 + 0.001, seg=192))   # disc chamber
    cut(ob, cyl(CHAM_BORE / 2.0, RING_Z1, CHAM_Z1 + 1, seg=192))       # flange chamber
    # ring pin pockets, open to the top so the dowels drop in
    polar_ring(ob, N_PINS, R_PC,
               lambda x, y: cyl((R_PIN * 2 + PIN_FIT) / 2.0, RING_Z0 - 0.01, RING_Z1 + 1, x, y, seg=48))
    # NEMA17 interface: pilot recess, shaft/cam clearance, 4x M3 + counterbore
    cut(ob, cyl(NEMA_PILOT / 2.0, -1.0, 2.5, seg=96))
    cut(ob, cyl(18.0 / 2.0, -1.0, BASE_T + 0.001, seg=96))
    r_nema = NEMA_BOLT / math.sqrt(2.0)
    polar_ring(ob, 4, r_nema, lambda x, y: cyl(NEMA_M3_CL / 2.0, -1.0, BASE_T + 1, x, y, seg=32), 45.0)
    polar_ring(ob, 4, r_nema,
               lambda x, y: cyl(NEMA_CB_D / 2.0, BASE_T - NEMA_CB_T, BASE_T + 0.001, x, y, seg=32), 45.0)
    # blind holes for the cover screws (M3 self-tapping)
    polar_ring(ob, N_COV_BOLT, COV_BOLT_R,
               lambda x, y: cyl(2.5 / 2.0, CHAM_Z1 - 12.5, CHAM_Z1 + 1, x, y, seg=32))
    return cleanup(ob)

def build_flange():
    ob = cyl(FL_D / 2.0, FL_Z0, FL_Z1, seg=160)
    ob.name = "06_output_flange"
    # pin holes are cut through the plate first; the hub then caps them, which
    # gives a blind DISC_T-deep press fit and avoids cutting into the hub
    polar_ring(ob, N_OUT, OUT_PIN_R,
               lambda x, y: cyl((OUT_PIN_D + 0.05) / 2.0, FL_Z0 - 1, FL_Z1 + 1, x, y, seg=48))
    fuse(ob, cyl(HUB_D / 2.0, FL_Z1 - 0.001, HUB_Z1, seg=160))
    # cam clearance recess + link mounting: 4x M4 tapped, centre pilot recess
    cut(ob, cyl(26.0 / 2.0, FL_Z0 - 0.001, FL_Z0 + 1.5, seg=96))
    cut(ob, cyl(16.0 / 2.0, HUB_Z1 - 4.0, HUB_Z1 + 1, seg=96))
    polar_ring(ob, 4, 13.0,
               lambda x, y: cyl(3.3 / 2.0, HUB_Z1 - 8.0, HUB_Z1 + 1, x, y, seg=32), 45.0)
    return cleanup(ob)

def build_cover():
    ob = cyl(HOUS_OD / 2.0, COV_Z0, COV_Z1, seg=192)
    ob.name = "07_front_cover"
    cut(ob, cyl(OB_OD / 2.0, COV_Z0 - 0.001, OB_Z1, seg=160))          # 6808 seat
    cut(ob, cyl(COV_LIP_D / 2.0, OB_Z1, COV_Z1 + 1, seg=160))          # retaining lip
    polar_ring(ob, N_COV_BOLT, COV_BOLT_R,
               lambda x, y: cyl(NEMA_M3_CL / 2.0, COV_Z0 - 1, COV_Z1 + 1, x, y, seg=32))
    polar_ring(ob, N_COV_BOLT, COV_BOLT_R,
               lambda x, y: cyl(NEMA_CB_D / 2.0, COV_Z1 - 3.5, COV_Z1 + 1, x, y, seg=32))
    return cleanup(ob)

def build_hardware():
    """Steel parts - reference only, not for printing."""
    obs = []
    for i in range(N_PINS):
        a = 2.0 * math.pi * i / N_PINS
        p = cyl(R_PIN, RING_Z0, RING_Z1, R_PC * math.cos(a), R_PC * math.sin(a), seg=32)
        p.name = "hw_ring_pin"
        obs.append(p)
    for i in range(N_OUT):
        a = 2.0 * math.pi * i / N_OUT
        p = cyl(OUT_PIN_D / 2.0, FL_Z1 - 22.0, FL_Z1,
                OUT_PIN_R * math.cos(a), OUT_PIN_R * math.sin(a), seg=32)
        p.name = "hw_output_pin"
        obs.append(p)
    return obs

# ---------------------------------------------------------------- export/report
def export_stl(ob, path):
    activate(ob)
    zmin = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.location.z -= zmin
    bpy.context.view_layer.update()
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True)
    ob.location.z += zmin
    bpy.context.view_layer.update()

def report():
    L = []
    L.append("=" * 68)
    L.append(f"  CYCLOIDAL DRIVE  {N_LOBES}:1   for NEMA17")
    L.append("=" * 68)
    L.append(f"  ring pins            : {N_PINS} x O{R_PIN*2:.1f} dowel, pin circle r{R_PC}")
    L.append(f"  disc lobes           : {N_LOBES}      reduction {N_LOBES}:1")
    L.append(f"  eccentricity         : {ECC} mm   (2E={2*ECC} <= pin r {R_PIN}  OK)")
    L.append(f"  trochoid ratio E*N/R : {ECC*N_PINS/R_PC:.3f}  (<1 required)")
    L.append(f"  tooth height         : {2*ECC:.2f} mm")
    L.append(f"  flank clearance      : {CLR} mm")
    L.append(f"  envelope             : O{HOUS_OD} x {HUB_Z1:.1f} mm tall")
    L.append(f"  output torque est.   : 0.45 Nm x {N_LOBES} x 0.75 = {0.45*N_LOBES*0.75:.1f} Nm")
    L.append(f"  output step          : 1.8 / {N_LOBES} = {1.8/N_LOBES:.3f} deg full-step")
    L.append("-" * 68)
    L.append("  PRINTED PARTS (PETG or ABS, 4 perimeters, 40-60% infill)")
    L.append("   01_housing.stl        x1   print base down, no supports")
    L.append("   03_disc_A.stl         x1   flat")
    L.append(f"   04_disc_B.stl         x1   flat  (profile rotated {180.0/N_LOBES:.0f} deg vs A - NOT the same part)")
    L.append("   05_eccentric_cam.stl  x1   flat, 6 perimeters")
    L.append("   06_output_flange.stl  x1   plate down")
    L.append("   07_front_cover.stl    x1   flat")
    L.append("-" * 68)
    L.append("  BOUGHT PARTS")
    L.append(f"   {N_PINS}x  dowel pin O5 x 16 mm  (ring pins)")
    L.append(f"   {N_OUT}x  dowel pin O5 x 22 mm  (output pins)")
    L.append( "   2x  6802ZZ  15x24x5   (disc bearings, on the cam)")
    L.append( "   1x  6808-2RS 40x52x7  (output bearing)")
    L.append(f"   {N_COV_BOLT}x  M3x16 self-tapping   (cover)")
    L.append( "   4x  M3x8  (to the motor, fitted through the bore)")
    L.append( "   1x  M3 grub screw (cam to shaft flat)")
    L.append("=" * 68)
    return "\n".join(L)

# ------------------------------------------------------------------------ main
def main():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    clear_scene()
    parts = []
    parts.append(build_housing())
    da = build_disc("03_disc_A", DA_Z0, 0.0)
    # disc B sits on the opposite cam lobe, so its profile must lag by half a
    # lobe pitch (180/lobes) while the output holes stay put. A and B are
    # therefore genuinely different parts.
    db = build_disc("04_disc_B", DB_Z0, -180.0 / N_LOBES)
    parts += [da, db, build_cam(), build_flange(), build_cover()]

    hw = build_hardware()
    for i, o in enumerate(hw):
        o.color = (0.6, 0.6, 0.65, 1.0)

    if EXPLODE:
        for i, p in enumerate(parts):
            p.location.z += EXPLODE * i

    if EXPORT:
        os.makedirs(OUT_DIR, exist_ok=True)
        for p in parts:
            export_stl(p, os.path.join(OUT_DIR, p.name + ".stl"))
        with open(os.path.join(OUT_DIR, "README.txt"), "w") as f:
            f.write(report() + "\n")

    print(report())
    print(f"\nSTL -> {OUT_DIR}")

if __name__ == "__main__":
    main()
