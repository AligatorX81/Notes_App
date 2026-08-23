"""Kotirani crtez ruke u bocnom pogledu (PNG).

Iste mere kao cad/arm_massing.py — citljiv prikaz za proveru proporcija,
ne tehnicki crtez za izradu.
"""

import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

BAZA_X, BAZA_Z = 220.0, 130.0
OSA_RAMENA_Z = 210.0
L_NAD, L_POD, L_GRIP = 260.0, 240.0, 100.0
D_RAME, D_LAKAT, D_ZGLOB = 137.0, 89.0, 55.0
NEMA = 42.3

LINIJA, CEV, KOTA, MOTOR = "#2b3a4a", "#4a6fa5", "#c0392b", "#8fa0ad"


def t(x, z, d, a):
    r = math.radians(a)
    return x + d*math.cos(r), z + d*math.sin(r)


def kota(ax, p1, p2, tekst, odmak=55, fs=11):
    dx, dz = p2[0]-p1[0], p2[1]-p1[1]
    L = math.hypot(dx, dz)
    n = (-dz/L*odmak, dx/L*odmak)
    a1, a2 = (p1[0]+n[0], p1[1]+n[1]), (p2[0]+n[0], p2[1]+n[1])
    ax.add_patch(FancyArrowPatch(a1, a2, arrowstyle="<|-|>", mutation_scale=11,
                                 color=KOTA, lw=1.4, zorder=8))
    for p, a in ((p1, a1), (p2, a2)):
        ax.plot([p[0], a[0]], [p[1], a[1]], color=KOTA, lw=0.7, ls=":", zorder=8)
    ax.text((a1[0]+a2[0])/2, (a1[1]+a2[1])/2, tekst, ha="center", va="center",
            fontsize=fs, color=KOTA, fontweight="bold", zorder=9,
            bbox=dict(fc="white", ec="none", pad=2))


def nacrtaj(ax, ugao_nad, ugao_pod, ugao_grip, naslov, ploca=True):
    rame = (0.0, OSA_RAMENA_Z)
    lakat = t(*rame, L_NAD, ugao_nad)
    zglob = t(*lakat, L_POD, ugao_pod)
    vrh = t(*zglob, L_GRIP, ugao_grip)

    ax.add_patch(Rectangle((-BAZA_X/2, 0), BAZA_X, BAZA_Z, fc="#e8edf2",
                           ec=LINIJA, lw=1.8, zorder=1))
    ax.add_patch(Rectangle((-45, BAZA_Z), 90, OSA_RAMENA_Z-BAZA_Z, fc="#e8edf2",
                           ec=LINIJA, lw=1.8, zorder=1))
    ax.text(0, BAZA_Z/2, "BAZA\nOctopus + M1", ha="center", va="center",
            fontsize=8.5, color=LINIJA, zorder=2)

    if ploca:
        ax.add_patch(Rectangle((185, BAZA_Z-8), 220, 8, fc="#d5dbe1",
                               ec=LINIJA, lw=1.4, zorder=1))
        ax.text(295, BAZA_Z-26, "ploča za štampu", ha="center", fontsize=8,
                color="#6b7b8c")

    # motori (iza svega)
    for c, a in ((rame, ugao_nad), (lakat, ugao_pod), (zglob, ugao_grip)):
        ax.add_patch(Rectangle((c[0]-NEMA/2, c[1]-NEMA/2), NEMA, NEMA, fc=MOTOR,
                               ec="none", alpha=0.5, zorder=2))

    # karbonske cevi u paru
    for od, do in ((rame, lakat), (lakat, zglob)):
        dx, dz = do[0]-od[0], do[1]-od[1]
        L = math.hypot(dx, dz); n = (-dz/L*12, dx/L*12)
        for s in (-1, 1):
            ax.plot([od[0]+n[0]*s, do[0]+n[0]*s], [od[1]+n[1]*s, do[1]+n[1]*s],
                    color=CEV, lw=5, solid_capstyle="round", zorder=3)

    # gripper
    ax.plot([zglob[0], vrh[0]], [zglob[1], vrh[1]], color=CEV, lw=7,
            solid_capstyle="round", zorder=3)
    ang = math.radians(ugao_grip)
    nx, nz = -math.sin(ang), math.cos(ang)
    for s in (-1, 1):
        bx, bz = vrh[0]+nx*s*11, vrh[1]+nz*s*11
        ax.plot([bx-math.cos(ang)*14, bx+math.cos(ang)*16],
                [bz-math.sin(ang)*14, bz+math.sin(ang)*16],
                color=LINIJA, lw=4, solid_capstyle="round", zorder=4)

    for c, d in ((rame, D_RAME), (lakat, D_LAKAT), (zglob, D_ZGLOB)):
        ax.add_patch(Circle(c, d/2, fc="white", ec=LINIJA, lw=2.2, zorder=5, alpha=0.95))
        ax.add_patch(Circle(c, 5.5, fc=LINIJA, zorder=6))

    ax.text(rame[0], rame[1]-D_RAME/2-22, "M2   50:1   Ø137", ha="center",
            va="center", fontsize=8.5, color=LINIJA, zorder=9,
            bbox=dict(fc="white", ec="none", pad=1.5))
    ax.text(lakat[0], lakat[1]-D_LAKAT/2-20, "M3   25:1   Ø89", ha="center",
            va="center", fontsize=8.5, color=LINIJA, zorder=9,
            bbox=dict(fc="white", ec="none", pad=1.5))
    ax.annotate("M5  puž", zglob, xytext=(zglob[0]+58, zglob[1]+58),
                fontsize=8, color=LINIJA, zorder=7,
                arrowprops=dict(arrowstyle="-", color=LINIJA, lw=0.8))

    ax.set_title(naslov, fontsize=11.5, color=LINIJA, pad=14)
    return rame, lakat, zglob, vrh


def main():
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # --- levo: radna poza ---
    r, l, z, v = nacrtaj(axes[0], 62, -34, -90, "Radna poza — iznad ploče za štampu")
    kota(axes[0], r, l, "260")
    kota(axes[0], l, z, "240", odmak=-52)
    kota(axes[0], z, v, "100", odmak=-46, fs=9.5)

    # --- desno: ispruzena vodoravno, pun domet ---
    r, l, z, v = nacrtaj(axes[1], 0, 0, 0, "Ispružena vodoravno — puni domet",
                         ploca=False)
    kota(axes[1], r, l, "260", odmak=48)
    kota(axes[1], l, z, "240", odmak=48)
    kota(axes[1], z, v, "100", odmak=48, fs=9.5)

    ax = axes[1]
    ax.add_patch(FancyArrowPatch((r[0], -30), (v[0], -30), arrowstyle="<|-|>",
                                 mutation_scale=12, color=KOTA, lw=1.6, zorder=8))
    for x in (r[0], v[0]):
        ax.plot([x, x], [OSA_RAMENA_Z-70, -30], color=KOTA, lw=0.7, ls=":", zorder=8)
    ax.text((r[0]+v[0])/2, -55, "domet 600 mm od ose ramena", ha="center",
            fontsize=11, color=KOTA, fontweight="bold", zorder=9,
            bbox=dict(fc="white", ec="none", pad=2))
    ax.text((r[0]+v[0])/2, -105,
            "najgori slučaj za moment  ·  rame 63%, lakat 52% pri 1 kg",
            ha="center", fontsize=8.5, color="#6b7b8c")

    for ax, xl in zip(axes, ((-280, 610), (-190, 700))):
        ax.set_aspect("equal")
        ax.set_xlim(*xl)
        ax.set_ylim(-135, 560)
        ax.axhline(0, color="#95a5a6", lw=1.2, zorder=0)
        ax.axis("off")

    fig.suptitle("Robotska ruka — bočni pogled, mere u mm", fontsize=14,
                 color=LINIJA, y=0.97)
    fig.text(0.5, 0.02,
             "NEMA17 42×48  ·  nosivost 1 kg  ·  ASA  ·  24 V  ·  "
             "karbonske cevi Ø25 u paru  ·  osa ramena 210 mm iznad poda",
             ha="center", fontsize=9, color="#6b7b8c")

    os.makedirs("cad/out", exist_ok=True)
    fig.savefig("cad/out/ruka_mere.png", dpi=165, bbox_inches="tight",
                facecolor="white")
    print("cad/out/ruka_mere.png")


if __name__ == "__main__":
    main()
