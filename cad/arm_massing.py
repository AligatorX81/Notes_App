"""Maketa cele ruke — cilindricni aktuatori.

Arhitektura: motor i cikloidni reduktor su koaksijalni, u jednom cilindricnom
kucistu. Motor ulazi sa jedne strane, izlazna prirubnica izlazi sa druge.
Nema delova koji strce — segmenti se spajaju direktno na prirubnice.

Gruba zapreminska predstava za proveru proporcija, ne delovi za izradu.
Mere iz docs/robotic-arm/SPEC.md.
"""

from __future__ import annotations

import math
import os

import cadquery as cq

# --- baza ---
BAZA_X, BAZA_Y, BAZA_Z = 200.0, 170.0, 125.0
OSA_RAMENA_Z = 205.0

# --- duzine segmenata ---
L_NADLAKTICA, L_PODLAKTICA, L_GRIPPER = 260.0, 240.0, 100.0

# --- cilindricni aktuatori: (precnik, duzina) ---
AKT_RAME = (116.0, 92.0)      # 50:1, disk Ø105
AKT_LAKAT = (72.0, 92.0)      # 25:1, disk Ø61
AKT_ROLL = (52.0, 78.0)       # M4, remen
AKT_ZGLOB = (58.0, 74.0)      # M5, puzni

D_CEV, RAZMAK_CEVI = 25.0, 34.0

UGAO_RAME, UGAO_PODLAKTICA = 62.0, -34.0


def t(x, z, d, a):
    r = math.radians(a)
    return x + d*math.cos(r), z + d*math.sin(r)


RAME = (0.0, OSA_RAMENA_Z)
LAKAT = t(*RAME, L_NADLAKTICA, UGAO_RAME)
ZGLOB = t(*LAKAT, L_PODLAKTICA, UGAO_PODLAKTICA)
VRH = (ZGLOB[0], ZGLOB[1] - L_GRIPPER)


def cilindar(pocetak, pravac, precnik, duzina):
    """Cilindar zadat pocetnom tackom i pravcem ose — bez dvosmislenosti oko
    toga u kom smeru radi extrude na kojoj ravni."""
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        precnik/2, duzina,
        pnt=cq.Vector(*pocetak), dir=cq.Vector(*pravac)))


def aktuator(centar, precnik, duzina, y=0.0):
    """Cilindricni aktuator: osa zgloba je vodoravna (duz Y), motor i reduktor
    su unutra. Uzi prstenovi na krajevima su izlazne prirubnice."""
    d, L = precnik, duzina
    os_y = (0, 1, 0)
    telo = cilindar((centar[0], y - L/2, centar[1]), os_y, d, L)
    for kraj in (y - L/2 - 9, y + L/2):
        telo = telo.union(
            cilindar((centar[0], kraj, centar[1]), os_y, d - 14, 9))
    return telo


def cev(od, do, precnik, y=0.0):
    """Cev izmedju dve tacke u ravni ruke (XZ)."""
    dx, dz = do[0]-od[0], do[1]-od[1]
    L = math.hypot(dx, dz)
    return cilindar((od[0], y, od[1]), (dx/L, 0, dz/L), precnik, L)


def build():
    # baza sa zaobljenim ivicama
    d = (
        cq.Workplane("XY")
        .box(BAZA_X, BAZA_Y, BAZA_Z, centered=(True, True, False))
        .edges("|Z").fillet(14)
    )
    # vrat baze — nosi rame, ujedno prolaz kablova kroz osu M1
    d = d.union(
        cq.Workplane("XY").circle(46).extrude(OSA_RAMENA_Z - BAZA_Z - 20)
        .translate((0, 0, BAZA_Z))
    )

    d = d.union(aktuator(RAME, *AKT_RAME))

    for y in (-RAZMAK_CEVI/2, RAZMAK_CEVI/2):
        d = d.union(cev(RAME, LAKAT, D_CEV, y))
        d = d.union(cev(LAKAT, ZGLOB, D_CEV, y))

    d = d.union(aktuator(LAKAT, *AKT_LAKAT))

    # M4 roll — koaksijalan sa podlakticom, odmah iza lakta
    a = math.radians(UGAO_PODLAKTICA)
    pocetak = t(*LAKAT, 46, UGAO_PODLAKTICA)
    d = d.union(cilindar((pocetak[0], 0, pocetak[1]),
                         (math.cos(a), 0, math.sin(a)),
                         AKT_ROLL[0], AKT_ROLL[1]))

    d = d.union(aktuator(ZGLOB, *AKT_ZGLOB))

    # gripper
    d = d.union(cev(ZGLOB, (VRH[0], VRH[1]+38), 36))

    for y in (-19, 19):
        d = d.union(
            cq.Workplane("XY").box(15, 9, 42, centered=(True, True, False))
            .translate((VRH[0], y, VRH[1]))
        )

    # ploca za stampu
    d = d.union(
        cq.Workplane("XY").box(220, 220, 8, centered=(True, True, False))
        .translate((290, 0, BAZA_Z - 8))
    )
    return d


def main():
    d = build()
    os.makedirs("cad/out", exist_ok=True)
    cq.exporters.export(d, "cad/out/ruka_maketa.step")
    for naziv, smer in (("bok", (0, -1, 0)), ("izo", (0.8, -0.9, 0.45))):
        cq.exporters.export(d, f"cad/out/ruka_{naziv}.svg", opt={
            "projectionDir": smer, "showAxes": False, "strokeWidth": 0.5,
            "width": 1100, "height": 850, "marginLeft": 40, "marginTop": 40,
        })
    print(f"aktuator rame   Ø{AKT_RAME[0]:.0f} x {AKT_RAME[1]:.0f} mm")
    print(f"aktuator lakat  Ø{AKT_LAKAT[0]:.0f} x {AKT_LAKAT[1]:.0f} mm")
    print(f"dohvat u ovoj pozi: {VRH[0]:.0f} mm,  visina lakta: {LAKAT[1]:.0f} mm")


if __name__ == "__main__":
    main()
