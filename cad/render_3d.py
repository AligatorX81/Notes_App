"""Render makete u vise pogleda kao jedan PNG.

CadQuery izvozi poglede sa uklonjenim skrivenim linijama u SVG, pa se SVG
konvertuje u PNG i poglede spajamo u jednu sliku.
"""

import io
import os

import cairosvg
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

import arm_massing

POGLEDI = (
    ((0.80, 1.0, 0.55), "Izometrija"),
    ((0.0, 1.0, 0.0), "Bočni pogled"),
    ((0.30, 0.55, 1.0), "Odozgo-napred"),
)


def svg_u_png(model, smer, sirina=1000, visina=800):
    """CadQuery izvozi SVG sa uklonjenim skrivenim linijama; konvertujemo u PNG."""
    tmp = "cad/out/_pogled.svg"
    cq.exporters.export(model, tmp, opt={
        "projectionDir": smer, "showAxes": False, "strokeWidth": 0.55,
        "width": sirina, "height": visina, "marginLeft": 30, "marginTop": 30,
    })
    png = cairosvg.svg2png(url=tmp, output_width=sirina*2,
                           output_height=visina*2, background_color="white")
    os.remove(tmp)
    slika = mpimg.imread(io.BytesIO(png), format="png")
    # CadQuery-jev SVG izvoz ne postuje "gore": u izlazu je +X nagore a +Z udesno.
    # Rotacija za 90° i preslikavanje vracaju uobicajenu orijentaciju (X desno, Z gore).
    return np.rot90(slika, k=1)[:, ::-1]


def main():
    os.makedirs("cad/out", exist_ok=True)
    model = arm_massing.build()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.4))
    for ax, (smer, naslov) in zip(axes, POGLEDI):
        ax.imshow(svg_u_png(model, smer))
        ax.set_title(naslov, fontsize=12, color="#2b3a4a", pad=8)
        ax.axis("off")

    fig.suptitle("Robotska ruka — cilindrični aktuatori (NEMA17 + cikloidni koaksijalno)",
                 fontsize=14, color="#2b3a4a", y=0.99)
    fig.text(0.5, 0.02,
             f"rame Ø{arm_massing.AKT_RAME[0]:.0f}×{arm_massing.AKT_RAME[1]:.0f}  ·  "
             f"lakat Ø{arm_massing.AKT_LAKAT[0]:.0f}×{arm_massing.AKT_LAKAT[1]:.0f}  ·  "
             "domet 600 mm  ·  nosivost 1 kg  ·  ASA",
             ha="center", fontsize=10, color="#6b7b8c")
    fig.savefig("cad/out/ruka_3d.png", dpi=125, bbox_inches="tight", facecolor="white")
    print("cad/out/ruka_3d.png")


if __name__ == "__main__":
    main()
