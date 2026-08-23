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
| M2 | pitch — rame | **cikloidni 40:1**, Ø132 mm | TMC2240 |
| M3 | pitch — lakat | **cikloidni 20:1**, Ø75 mm | TMC2240 |
| M4 | roll — podlaktica | remen | TMC2240 |
| M5 | pitch — zglob | puzni (samokociv) | TMC2226 |
| M6 | gripper | — | TMC2226 |

- **5 stepeni slobode + hvataljka = 6 motora**
- Motori: **iskljucivo NEMA17**
- Napajanje: **24 V**
- Domet **600 mm**, teret **500 g** (potvrditi)
- Dva rezima: hvatanje/premestanje (pun domet) i **stampa (200–350 mm zona)**

## Generisanje modela

```bash
pip install cadquery
python3 cad/cycloidal_disc.py shoulder   # 40:1, Ø132 mm
python3 cad/cycloidal_disc.py elbow      # 20:1, Ø75 mm
python3 cad/torque_calc.py               # momenti po zglobovima
```

Izlaz u `cad/out/` kao STEP (za FreeCAD) i STL (za stampu).

## Otvoreno

1. **Tacna oznaka NEMA17** — 42x40 (0.45 Nm), 42x48 (0.59 Nm) ili 42x60 (0.72 Nm).
   Racunato je sa 0.59 Nm; razlika pomera sve rezerve. **Blokira potvrdu odnosa.**
2. **Nosivost** — 500 g, 750 g ili 1 kg
3. **Materijal** — PETG ili ASA (PLA otpada zbog hotenda)
4. **Gde se racuna inverzna kinematika** — u firmware-u ili offline pre stampe

## Veza sa drugim sesijama

- **OCTOARM bare-metal firmware** — gotov firmware, lokalna masina
- **cycloidal drive** (grana `claude/claude-code-testing-zjf2fd`) — ranija verzija
  cikloidnog reduktora 20:1. Ta sesija je stala cekajuci duzinu segmenta i
  opterecenje na kraju; oba su sada poznata (600 mm, 500 g).

Kontekst razgovora se ne prenosi izmedju sesija — **ova dokumentacija je
prenosnik.** Sve odluke su ovde, sa obrazlozenjem.
