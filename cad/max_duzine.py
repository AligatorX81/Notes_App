"""Maksimalne duzine segmenata iz raspolozivog momenta NEMA17.

Racuna do koje duzine nadlaktica i podlaktica smeju ici a da rame i lakat
ostanu unutar onoga sto NEMA17 daje kroz svoje reduktore. Duzine su spregnute:
obe opterecuju rame, pa se ne mogu obe maksimizirati.

Rezerva od 30% je za ubrzanje — staticki proracun ne pokriva dinamiku.
"""

import math
G = 9.81
T_MOTOR = 0.59          # NEMA17 42x48
ETA = 0.75
I_RAME, I_LAKAT = 40, 20

T_RAME_MAX  = T_MOTOR * I_RAME  * ETA     # 17.70 Nm
T_LAKAT_MAX = T_MOTOR * I_LAKAT * ETA     #  8.85 Nm

# fiksne mase [kg]
M_LAKAT   = 0.58    # M3 + cikloidni 20:1 (sklop 180 g + motor 400 g)
M_ROLL    = 0.35    # M4 + remenica
M_ZGLOB   = 0.40    # M5 + puzni prenos
M_GRIPPER = 0.35    # gripper + M6
L_GRIPPER = 100.0   # zglob -> vrh grippera, fiksno

# linijska gustina konstrukcije [kg/mm]
RHO_NAD = 0.35/260
RHO_POD = 0.30/240

def t_lakat(L3, teret):
    return G * (
        M_ROLL*0.040
        + RHO_POD*L3 * (L3/2)/1000
        + M_ZGLOB * L3/1000
        + M_GRIPPER * (L3 + L_GRIPPER/2)/1000
        + teret * (L3 + L_GRIPPER)/1000
    )

def t_rame(L2, L3, teret):
    return G * (
        RHO_NAD*L2 * (L2/2)/1000
        + M_LAKAT * L2/1000
        + M_ROLL * (L2+40)/1000
        + RHO_POD*L3 * (L2 + L3/2)/1000
        + M_ZGLOB * (L2+L3)/1000
        + M_GRIPPER * (L2 + L3 + L_GRIPPER/2)/1000
        + teret * (L2 + L3 + L_GRIPPER)/1000
    )

def maks(f, limit, *a):
    lo, hi = 10.0, 3000.0
    for _ in range(80):
        mid = (lo+hi)/2
        if f(mid, *a) <= limit: lo = mid
        else: hi = mid
    return lo

for teret, oznaka in ((0.5, "teret 500 g"), (1.0, "teret 1 kg")):
    print(f"\n{'='*66}\n{oznaka.upper()}   (rame {T_RAME_MAX:.1f} Nm, lakat {T_LAKAT_MAX:.1f} Nm)\n{'='*66}")
    for rez, opis in ((0.0, "APSOLUTNI MAKSIMUM (0% rezerve)"),
                      (0.30, "PREPORUKA (30% rezerve za ubrzanje)")):
        tl = T_LAKAT_MAX*(1-rez)
        tr = T_RAME_MAX*(1-rez)
        L3max = maks(t_lakat, tl, teret)
        print(f"\n  {opis}")
        print(f"    lakat -> zglob (L3) max: {L3max:.0f} mm"
              f"   => lakat -> vrh grippera: {L3max+L_GRIPPER:.0f} mm")
        print(f"    {'L3 [mm]':>9} {'L2 max [mm]':>12} {'ukupan domet':>14}")
        for L3 in (200, 240, 280, min(320, L3max)):
            if L3 > L3max: continue
            L2 = maks(lambda x, a, b: t_rame(x, a, b), tr, L3, teret)
            print(f"    {L3:>9.0f} {L2:>12.0f} {L2+L3+L_GRIPPER:>13.0f} mm")
