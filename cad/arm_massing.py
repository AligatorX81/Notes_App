"""Maketa cele ruke u pravim merama.

Gruba zapreminska predstava — ne delovi za izradu, nego provera proporcija,
dohvata i medjusobnog odnosa sklopova. Sve mere su one potvrdjene u
docs/robotic-arm/SPEC.md.
"""

from __future__ import annotations

import math
import os

import cadquery as cq

# --- potvrdjene mere (mm) ---
BAZA_X, BAZA_Y, BAZA_Z = 220.0, 180.0, 130.0
OSA_RAMENA_Z = 210.0

L_NADLAKTICA = 260.0        # rame -> lakat
L_PODLAKTICA = 240.0        # lakat -> zglob
L_GRIPPER = 100.0           # zglob -> vrh

D_CIKL_RAME = 137.0         # 50:1
D_CIKL_LAKAT = 89.0         # 25:1
W_CIKL_RAME, W_CIKL_LAKAT = 55.0, 45.0

NEMA = (42.3, 42.3, 48.0)   # potvrdjeno: 42x48
D_CEV, RAZMAK_CEVI = 25.0, 30.0

# --- poza (stepeni od horizontale) ---
UGAO_RAME = 62.0
UGAO_PODLAKTICA = -34.0


def tacka(x0, z0, duz, ugao):
    a = math.radians(ugao)
    return x0 + duz*math.cos(a), z0 + duz*math.sin(a)


RAME = (0.0, OSA_RAMENA_Z)
LAKAT = tacka(*RAME, L_NADLAKTICA, UGAO_RAME)
ZGLOB = tacka(*LAKAT, L_PODLAKTICA, UGAO_PODLAKTICA)
VRH = (ZGLOB[0], ZGLOB[1] - L_GRIPPER)


def cev(od, do, precnik):
    """Cilindar izmedju dve tacke u XZ ravni."""
    dx, dz = do[0]-od[0], do[1]-od[1]
    duz = math.hypot(dx, dz)
    ugao = math.degrees(math.atan2(dz, dx))
    return (
        cq.Workplane("XZ").circle(precnik/2).extrude(duz)
        .rotate((0, 0, 0), (0, 1, 0), 90 - ugao)
        .translate((od[0], 0, od[1]))
    )


def disk(centar, precnik, sirina):
    return (
        cq.Workplane("XZ").circle(precnik/2).extrude(sirina)
        .translate((centar[0], sirina/2, centar[1]))
    )


def motor(centar, ugao, odmak):
    x, z = tacka(centar[0], centar[1], odmak, ugao)
    return (
        cq.Workplane("XZ")
        .box(NEMA[0], NEMA[1], NEMA[2], centered=(True, True, False))
        .rotate((0, 0, 0), (0, 1, 0), -ugao)
        .translate((x, -NEMA[2]/2 - 30, z))
    )


def build():
    d = cq.Workplane("XY").box(BAZA_X, BAZA_Y, BAZA_Z, centered=(True, True, False))

    # nosac ramena iznad baze
    d = d.union(
        cq.Workplane("XY").box(90, 150, OSA_RAMENA_Z - BAZA_Z,
                               centered=(True, True, False))
        .translate((0, 0, BAZA_Z))
    )

    d = d.union(disk(RAME, D_CIKL_RAME, W_CIKL_RAME))
    d = d.union(motor(RAME, UGAO_RAME, 0))

    for y in (-RAZMAK_CEVI/2, RAZMAK_CEVI/2):
        d = d.union(cev(RAME, LAKAT, D_CEV).translate((0, y, 0)))
        d = d.union(cev(LAKAT, ZGLOB, D_CEV).translate((0, y, 0)))

    d = d.union(disk(LAKAT, D_CIKL_LAKAT, W_CIKL_LAKAT))
    d = d.union(motor(LAKAT, UGAO_RAME, -55))
    d = d.union(motor(LAKAT, UGAO_PODLAKTICA, 70))          # M4 roll

    d = d.union(disk(ZGLOB, 55, 40))                         # M5 + puzni
    d = d.union(motor(ZGLOB, UGAO_PODLAKTICA, -45))

    # gripper: nosac + dva prsta
    d = d.union(cev(ZGLOB, (VRH[0], VRH[1]+35), 34))
    for y in (-18, 18):
        d = d.union(
            cq.Workplane("XY").box(14, 8, 40, centered=(True, True, False))
            .translate((VRH[0], y, VRH[1]))
        )

    # ploca za stampu, pored baze, u nivou gornje povrsine
    d = d.union(
        cq.Workplane("XY").box(220, 220, 8, centered=(True, True, False))
        .translate((295, 0, BAZA_Z - 8))
    )
    return d


def main():
    d = build()
    os.makedirs("cad/out", exist_ok=True)
    cq.exporters.export(d, "cad/out/ruka_maketa.step")

    for naziv, smer in (("bok", (0, -1, 0)), ("izo", (0.75, -0.85, 0.45))):
        cq.exporters.export(d, f"cad/out/ruka_{naziv}.svg", opt={
            "projectionDir": smer, "showAxes": False, "strokeWidth": 0.5,
            "width": 1100, "height": 850, "marginLeft": 40, "marginTop": 40,
        })

    print(f"rame   x={RAME[0]:7.1f}  z={RAME[1]:7.1f}")
    print(f"lakat  x={LAKAT[0]:7.1f}  z={LAKAT[1]:7.1f}")
    print(f"zglob  x={ZGLOB[0]:7.1f}  z={ZGLOB[1]:7.1f}")
    print(f"vrh    x={VRH[0]:7.1f}  z={VRH[1]:7.1f}")
    print(f"\nhorizontalni dohvat od ose baze : {VRH[0]:.0f} mm")
    print(f"visina vrha iznad ploce         : {VRH[1] - BAZA_Z:.0f} mm")
    print(f"ukupna visina ruke              : {LAKAT[1]:.0f} mm")


if __name__ == "__main__":
    main()
