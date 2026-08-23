# Robotska ruka — ulazna tacka

Ovo je **drugi deo projekta**. Prvi deo (bare metal firmware za BTT Octopus Pro)
je gotov i radi. Ovde se projektuje mehanika koju ce ti motori pokretati.

## Procitaj ovim redom

| # | Fajl | Sadrzaj |
|---|------|---------|
| 1 | `SPEC.md` | osovine, pogoni, prenosni odnosi, elektronika, segmentacija |
| 2 | `3D-STAMPA-REZIM.md` | rezim gde ruka drzi hotend i stampa — najstroziji zahtev |
| 3 | `3D-PRINT.md` | zahtevi za stampu delova i sklapanje |
| 4 | `../../cad/README.md` | izbor alata, kako se generisu modeli |

## Stanje u jednoj tabeli

| Motor | Osa | Pogon | Drajver |
|-------|-----|-------|---------|
| M1 | yaw — baza | remen ~4:1 | TMC2240 |
| M2 | pitch — rame | **cikloidni 50:1**, aktuator Ø116x92 | TMC2240 |
| M3 | pitch — lakat | **cikloidni 25:1**, aktuator Ø72x92 | TMC2240 |
| M4 | roll — podlaktica | remen | TMC2240 |
| M5 | pitch — zglob | puzni (samokociv) | TMC2226 |
| M6 | gripper | — | TMC2226 |

- **5 stepeni slobode + hvataljka = 6 motora**
- Motori: **NEMA17 42x48 (0.59 Nm)**
- Napajanje: **24 V**
- Domet **600 mm** od ose ramena, nosivost **1 kg**
- Duzine: **nadlaktica 260**, **podlaktica 240**, **zglob+gripper 100**
- Osa ramena **210 mm** iznad poda, baza **220 x 180 x 130**
- Materijal: **ASA** (zbog hotenda)
- **Cilindricni aktuatori:** motor + cikloidni koaksijalno u jednom kucistu
- Dva rezima: hvatanje/premestanje (pun domet) i **stampa (200–350 mm zona)**

## Generisanje modela

```bash
pip install cadquery
python3 cad/cycloidal_disc.py shoulder   # 50:1, Ø137 mm
python3 cad/cycloidal_disc.py elbow      # 25:1, Ø89 mm
python3 cad/torque_calc.py               # momenti po zglobovima
python3 cad/max_duzine.py                # granice duzina segmenata
python3 cad/arm_massing.py               # maketa cele ruke (STEP + SVG)
python3 cad/crtez_mere.py                # kotirani crtez (PNG)
PYTHONPATH=cad python3 cad/render_3d.py  # 3D pogledi (PNG)
```

Izlaz u `cad/out/` kao STEP (za FreeCAD) i STL (za stampu).

## Otvoreno

1. **Kalibracija skupljanja ASA** — izmeriti na probnom komadu i uneti u
   `ASA_SKUPLJANJE`. Bez toga disk ramena promasi meru za ~0.7 mm.
2. **Gde se racuna inverzna kinematika** — u firmware-u ili offline pre stampe
3. **Tacan polozaj ploce za stampu** u odnosu na osu baze

## Veza sa drugim sesijama

- **OCTOARM bare-metal firmware** — gotov firmware, lokalna masina
- **cycloidal drive** (grana `claude/claude-code-testing-zjf2fd`) — ranija verzija
  cikloidnog reduktora 20:1. Ta sesija je stala cekajuci duzinu segmenta i
  opterecenje na kraju; oba su sada poznata (600 mm, 500 g).

Kontekst razgovora se ne prenosi izmedju sesija — **ova dokumentacija je
prenosnik.** Sve odluke su ovde, sa obrazlozenjem.
