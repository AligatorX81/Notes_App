"""Parametarski generator cikloidnog diska.

Profil se racuna iz hipocikloidnih jednacina i izvozi kao pravi B-rep solid
(STEP), pa se otvara u Fusionu ili SolidWorksu kao telo, ne kao mesh.

Prenosni odnos jednostepenog cikloidnog reduktora sa fiksnim prstenom pinova
i izlazom preko izlaznih cepova je  i = N - 1,  gde je N broj pinova prstena.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import cadquery as cq


@dataclass
class CycloidalParams:
    pin_circle_r: float      # R  - poluprecnik kruga na kojem leze pinovi prstena
    pin_r: float             # Rr - poluprecnik jednog pina
    eccentricity: float      # E  - ekscentricitet
    pin_count: int           # N  - broj pinova prstena (odnos = N - 1)
    disc_thickness: float
    bore_r: float            # otvor za lezaj na ekscentru
    output_hole_count: int
    output_hole_circle_r: float
    output_pin_r: float
    clearance: float = 0.0   # zazor profila, oduzima se od pin_r
    shrinkage: float = 0.0   # skupljanje materijala; model se uvecava da posle
                             # hladjenja padne na nominalnu meru

    @property
    def ratio(self) -> int:
        return self.pin_count - 1

    def validate(self) -> None:
        """Provera uslova koji sprecavaju podsecanje profila i sudar pinova."""
        max_e = self.pin_circle_r / self.pin_count
        if self.eccentricity >= max_e:
            raise ValueError(
                f"Ekscentricitet {self.eccentricity:.3f} mm je prevelik: "
                f"mora biti manji od R/N = {max_e:.3f} mm, inace profil ima podsecanje."
            )
        pitch = 2 * math.pi * self.pin_circle_r / self.pin_count
        gap = pitch - 2 * self.pin_r
        if gap <= 0:
            raise ValueError(
                f"Pinovi se preklapaju: korak {pitch:.2f} mm, precnik pina "
                f"{2 * self.pin_r:.2f} mm."
            )
        hole_r = self.output_pin_r + self.eccentricity
        if self.output_hole_circle_r + hole_r >= self.pin_circle_r - self.pin_r:
            raise ValueError("Izlazni otvori seku cikloidni profil - smanji krug izlaznih cepova.")
        if self.bore_r + self.eccentricity >= self.output_hole_circle_r - hole_r:
            raise ValueError("Centralni otvor se preklapa sa izlaznim otvorima.")


def profile_points(p: CycloidalParams, steps: int = 720) -> list[tuple[float, float]]:
    """Tacke cikloidnog profila (hipocikloida sa ekvidistantom za poluprecnik pina).

    Vraca otvorenu listu - prva tacka se ne ponavlja na kraju, jer periodicni
    splajn sam zatvara krivu.
    """
    R, E, N = p.pin_circle_r, p.eccentricity, p.pin_count
    Rr = p.pin_r - p.clearance

    pts: list[tuple[float, float]] = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        psi = math.atan2(math.sin((1 - N) * t), (R / (E * N)) - math.cos((1 - N) * t))
        x = R * math.cos(t) - Rr * math.cos(t + psi) - E * math.cos(N * t)
        y = -R * math.sin(t) + Rr * math.sin(t + psi) + E * math.sin(N * t)
        pts.append((x, y))
    return pts


def build_disc(p: CycloidalParams) -> cq.Workplane:
    p.validate()

    # Splajn umesto polilinije: jedna glatka ivica umesto stotina segmenata,
    # pa je STEP mali i skica u Fusionu ostaje upotrebljiva.
    pts = profile_points(p)
    disc = (
        cq.Workplane("XY")
        .spline(pts, periodic=True)
        .close()
        .extrude(p.disc_thickness)
    )

    # Centralni otvor za lezaj na ekscentricnoj osovini
    disc = disc.faces(">Z").workplane().hole(2 * p.bore_r)

    # Izlazni otvori: precnik = precnik cepa + 2 * ekscentricitet
    hole_r = p.output_pin_r + p.eccentricity
    disc = (
        disc.faces(">Z")
        .workplane()
        .polarArray(radius=p.output_hole_circle_r, startAngle=0, angle=360,
                    count=p.output_hole_count)
        .hole(2 * hole_r)
    )
    if p.shrinkage:
        # Uvecanje za 1/(1-s): posle skupljanja deo pada na nominalnu meru.
        # Skalira se cela geometrija, pa i zazori — sto je ispravno, jer su
        # zazori projektovani na nominalnoj meri.
        k = 1.0 / (1.0 - p.shrinkage)
        disc = disc.newObject([disc.val().scale(k)])
    return disc


# --- Napomena o izboru odnosa ---
# Granica ekscentriciteta je  E_max = R/N = korak_pina / (2*pi).
# Ako se R skalira sa brojem pinova tako da korak ostane isti, granica je
# KONSTANTNA bez obzira na prenosni odnos. Visi odnos kosta precnik i masu,
# ne preciznost. Ovde je korak drzan na 9 mm uz pinove O4 (celicni zatik).

# ASA se skuplja 0.4-0.7%. Vrednost OBAVEZNO kalibrisati probnim komadom —
# zavisi od stampaca, temperature komore i geometrije dela.
ASA_SKUPLJANJE = 0.005

# M2 rame - 50:1. Odnos podignut sa 40:1 zbog tereta od 1 kg: na 40:1 rame je
# trosilo 78% momenta, sto je iznad granice na kojoj koracni motor gubi korake.
# Korak pinova stisnut na 7.5 mm da disk ne naraste — na 9 mm bi bio Ø161 mm.
SHOULDER = CycloidalParams(
    pin_circle_r=60.9,
    pin_r=2.0,
    eccentricity=1.0,
    pin_count=51,
    disc_thickness=8.0,
    bore_r=11.0,
    output_hole_count=6,
    output_hole_circle_r=33.0,
    output_pin_r=4.0,
    clearance=0.08,
    shrinkage=ASA_SKUPLJANJE,
)

# M3 lakat - 25:1. Namerno nizi odnos nego rame: moment u laktu je svega
# 5.8 Nm, pa visak odnosa placa masom na sredini ruke bez koristi.
ELBOW = CycloidalParams(
    pin_circle_r=37.2,
    pin_r=2.0,
    eccentricity=1.2,
    pin_count=26,
    disc_thickness=7.0,
    bore_r=8.0,
    output_hole_count=6,
    output_hole_circle_r=21.0,
    output_pin_r=3.0,
    clearance=0.08,
    shrinkage=ASA_SKUPLJANJE,
)

PRESETS = {"shoulder": SHOULDER, "elbow": ELBOW}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("joint", nargs="?", default="shoulder", choices=list(PRESETS),
                    help="koji zglob generisati")
    ap.add_argument("--out", default=None)
    ap.add_argument("--pins", type=int, default=None,
                    help="broj pinova prstena; prenosni odnos = pins - 1")
    args = ap.parse_args()

    p = PRESETS[args.joint]
    if args.pins:
        p.pin_count = args.pins
    args.out = args.out or f"cad/out/cycloidal_disc_{args.joint}"

    disc = build_disc(p)

    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cq.exporters.export(disc, f"{args.out}.step")
    cq.exporters.export(disc, f"{args.out}.stl")

    vol = disc.val().Volume()
    print(f"Zglob               : {args.joint}")
    print(f"Prenosni odnos      : {p.ratio}:1")
    print(f"Precnik diska       : ~{2*p.pin_circle_r + 15:.0f} mm")
    print(f"Broj rezni profila  : {p.pin_count - 1} (lobova)")
    print(f"Ekscentricitet      : {p.eccentricity} mm (granica R/N = {p.pin_circle_r / p.pin_count:.3f} mm)")
    print(f"Korak pinova        : {2 * math.pi * p.pin_circle_r / p.pin_count:.2f} mm")
    if p.shrinkage:
        print(f"Kompenzacija ASA    : +{p.shrinkage*100:.1f}% "
              f"(model uvecan, posle hladjenja pada na nominalu)")
    print(f"Zapremina diska     : {vol / 1000:.1f} cm3")
    print(f"Izvezeno            : {args.out}.step / .stl")


if __name__ == "__main__":
    main()
