"""Cikloidni disk - nativna skripta za Autodesk Fusion.

Pokretanje: Utilities -> ADD-INS -> Scripts and Add-Ins -> Scripts -> Run.

Za razliku od cad/cycloidal_disc.py (CadQuery), ova skripta gradi geometriju
kroz Fusion API, pa nastaje pravo telo sa feature tree-om u timeline-u.

PAZNJA: Fusion API interno radi u CENTIMETRIMA. Sve vrednosti ispod su u
milimetrima i mnoze se konstantom MM pri predaji API-ju.
"""

import math
import traceback

import adsk.core
import adsk.fusion

# ---------------------------------------------------------------- parametri (mm)
PIN_CIRCLE_R = 50.0        # R  - poluprecnik kruga pinova prstena
PIN_R = 3.0                # Rr - poluprecnik pina
ECCENTRICITY = 1.0         # E  - ekscentricitet
PIN_COUNT = 36             # N  - broj pinova; prenosni odnos = N - 1
CLEARANCE = 0.08           # zazor profila, oduzima se od PIN_R

THICKNESS = 8.0
BORE_R = 11.0              # otvor za lezaj na ekscentru
OUT_HOLE_COUNT = 6
OUT_HOLE_CIRCLE_R = 26.0
OUT_PIN_R = 4.0

PROFILE_STEPS = 360        # tacaka kroz koje se provlaci splajn

MM = 0.1                   # mm -> cm (interne jedinice Fusiona)


def validate():
    """Isti uslovi kao u CadQuery verziji - prekid pre nego sto nastane los disk."""
    max_e = PIN_CIRCLE_R / PIN_COUNT
    if ECCENTRICITY >= max_e:
        raise ValueError(
            f"Ekscentricitet {ECCENTRICITY} mm je prevelik: mora biti ispod "
            f"R/N = {max_e:.3f} mm, inace profil ima podsecanje."
        )
    pitch = 2 * math.pi * PIN_CIRCLE_R / PIN_COUNT
    if pitch - 2 * PIN_R <= 0:
        raise ValueError(
            f"Pinovi se preklapaju: korak {pitch:.2f} mm, precnik pina {2 * PIN_R:.2f} mm."
        )
    hole_r = OUT_PIN_R + ECCENTRICITY
    if OUT_HOLE_CIRCLE_R + hole_r >= PIN_CIRCLE_R - PIN_R:
        raise ValueError("Izlazni otvori seku cikloidni profil.")
    if BORE_R + ECCENTRICITY >= OUT_HOLE_CIRCLE_R - hole_r:
        raise ValueError("Centralni otvor se preklapa sa izlaznim otvorima.")


def profile_points():
    """Hipocikloida sa ekvidistantom za poluprecnik pina."""
    R, E, N = PIN_CIRCLE_R, ECCENTRICITY, PIN_COUNT
    Rr = PIN_R - CLEARANCE

    pts = []
    for i in range(PROFILE_STEPS):
        t = 2 * math.pi * i / PROFILE_STEPS
        psi = math.atan2(math.sin((1 - N) * t), (R / (E * N)) - math.cos((1 - N) * t))
        x = R * math.cos(t) - Rr * math.cos(t + psi) - E * math.cos(N * t)
        y = -R * math.sin(t) + Rr * math.sin(t + psi) + E * math.sin(N * t)
        pts.append((x, y))
    return pts


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Otvori Design radno okruzenje pa pokreni ponovo.")
            return

        validate()

        root = design.rootComponent
        sketches = root.sketches
        extrudes = root.features.extrudeFeatures

        # --- 1. profil diska ------------------------------------------------
        sk = sketches.add(root.xYConstructionPlane)
        sk.name = f"Cikloidni profil {PIN_COUNT - 1}:1"

        pts = adsk.core.ObjectCollection.create()
        for x, y in profile_points():
            pts.add(adsk.core.Point3D.create(x * MM, y * MM, 0))
        # ponovljena prva tacka zatvara splajn
        first = profile_points()[0]
        pts.add(adsk.core.Point3D.create(first[0] * MM, first[1] * MM, 0))

        sk.sketchCurves.sketchFittedSplines.add(pts)

        ext_in = extrudes.createInput(
            sk.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        )
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(THICKNESS * MM))
        disc = extrudes.add(ext_in)
        disc.bodies.item(0).name = f"Cikloidni disk {PIN_COUNT - 1}-1"

        # --- 2. centralni otvor i izlazni otvori ----------------------------
        sk2 = sketches.add(root.xYConstructionPlane)
        sk2.name = "Otvori"
        circles = sk2.sketchCurves.sketchCircles
        origin = adsk.core.Point3D.create(0, 0, 0)

        circles.addByCenterRadius(origin, BORE_R * MM)

        out_hole_r = OUT_PIN_R + ECCENTRICITY
        for i in range(OUT_HOLE_COUNT):
            a = 2 * math.pi * i / OUT_HOLE_COUNT
            c = adsk.core.Point3D.create(
                OUT_HOLE_CIRCLE_R * math.cos(a) * MM,
                OUT_HOLE_CIRCLE_R * math.sin(a) * MM,
                0,
            )
            circles.addByCenterRadius(c, out_hole_r * MM)

        cut_profiles = adsk.core.ObjectCollection.create()
        for prof in sk2.profiles:
            cut_profiles.add(prof)

        cut_in = extrudes.createInput(
            cut_profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        cut_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(THICKNESS * MM))
        extrudes.add(cut_in)

        ui.messageBox(
            f"Cikloidni disk generisan.\n\n"
            f"Prenosni odnos: {PIN_COUNT - 1}:1\n"
            f"Broj lobova: {PIN_COUNT - 1}\n"
            f"Ekscentricitet: {ECCENTRICITY} mm (granica R/N = {PIN_CIRCLE_R / PIN_COUNT:.3f} mm)\n"
            f"Korak pinova: {2 * math.pi * PIN_CIRCLE_R / PIN_COUNT:.2f} mm"
        )

    except ValueError as e:
        if ui:
            ui.messageBox(f"Neispravni parametri:\n\n{e}")
    except Exception:
        if ui:
            ui.messageBox(f"Greska:\n{traceback.format_exc()}")
