"""Proracun statickih momenata po zglobovima.

Model: ruka ispruzena vodoravno — najgori slucaj za rame i lakat.
Momenti se racunaju kao suma m*g*d za svaku komponentu, gde je d rastojanje
od ose posmatranog zgloba.

Mase su procena zasnovana na izracunatoj masi cikloidnog stepena (~830 g sa
motorom) i tipicnim masama NEMA17. Zameniti stvarnim vrednostima cim delovi
budu izmereni.
"""

from __future__ import annotations

from dataclasses import dataclass

G = 9.81


@dataclass
class Komponenta:
    naziv: str
    masa: float        # kg
    polozaj: float     # mm od ose ramena, ruka ispruzena


# --- geometrija (mm), ukupan domet 600 ---
L_NADLAKTICA = 260.0
L_PODLAKTICA = 240.0
L_ZGLOB_GRIPPER = 100.0
DOMET = L_NADLAKTICA + L_PODLAKTICA + L_ZGLOB_GRIPPER

OSA_LAKTA = L_NADLAKTICA
OSA_ZGLOBA = L_NADLAKTICA + L_PODLAKTICA

KOMPONENTE = [
    Komponenta("nadlaktica (konstrukcija)", 0.35, L_NADLAKTICA / 2),
    Komponenta("M3 + cikloidni reduktor",   0.83, OSA_LAKTA),
    Komponenta("M4 roll + remenica",        0.35, OSA_LAKTA + 40),
    Komponenta("podlaktica (konstrukcija)", 0.30, OSA_LAKTA + L_PODLAKTICA / 2),
    Komponenta("M5 + puzni prenos",         0.40, OSA_ZGLOBA),
    Komponenta("gripper + M6",              0.35, OSA_ZGLOBA + L_ZGLOB_GRIPPER / 2),
]


def moment(osa_mm: float, teret_kg: float) -> float:
    """Staticki moment [Nm] oko ose na datom rastojanju od ramena."""
    uk = 0.0
    for k in KOMPONENTE:
        krak = k.polozaj - osa_mm
        if krak > 0:
            uk += k.masa * G * krak / 1000
    uk += teret_kg * G * (DOMET - osa_mm) / 1000
    return uk


def osovina(tau_zgloba: float, odnos: float, eta: float = 0.75) -> float:
    """Moment koji motor mora dati na svojoj osovini."""
    return tau_zgloba / odnos / eta


def main() -> None:
    masa_ruke = sum(k.masa for k in KOMPONENTE)
    print(f"Domet: {DOMET:.0f} mm   (nadlaktica {L_NADLAKTICA:.0f} + "
          f"podlaktica {L_PODLAKTICA:.0f} + zglob/gripper {L_ZGLOB_GRIPPER:.0f})")
    print(f"Masa pokretnog dela ruke: {masa_ruke:.2f} kg (bez tereta)\n")

    for teret in (0.5, 0.75, 1.0):
        print(f"--- teret {teret*1000:.0f} g na punom dometu ---")
        for naziv, osa, odnos in (
            ("M2 rame", 0.0, 35),
            ("M3 lakat", OSA_LAKTA, 28),
            ("M5 zglob", OSA_ZGLOBA, 30),
        ):
            t = moment(osa, teret)
            print(f"  {naziv:10s} {t:6.2f} Nm   ->  na osovini "
                  f"{osovina(t, odnos):5.2f} Nm  (odnos {odnos}:1)")
        print()


if __name__ == "__main__":
    main()
