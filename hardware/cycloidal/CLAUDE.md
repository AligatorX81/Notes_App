# Projekt: cikloidni reduktori za 3D štampu

## Kontekst
Reduktori za zglobove robotske ruke, pogonjeni NEMA17 motorima, štampani na FDM
pisaču. Motor se NIKAD ne modelira — koristi se samo njegov montažni interfejs
(31 mm M3 raspored, Ø22 pilot, Ø5 osovina).

## Alat
Blender + Python (`bpy`). Generator je parametarski skript, ne ručno modeliranje.
Headless pokretanje: `blender -b -P <skript>.py`, ili `blender -P <skript>.py` za
otvaranje s izgrađenim modelom.

## Provjereni dizajn 20:1
Fajl: `cycloidal_drive.py`

| parametar | vrijednost |
|---|---|
| N_PINS / režnjevi | 21 / 20 → 20:1 |
| R_PC (kružnica trnova) | 26.0 mm |
| R_PIN | 2.5 mm (Ø5 trn) |
| ECC | 0.9 mm |
| CLR (zazor bokova) | 0.15 mm |
| debljina diska | 7.0 mm |
| izlazni trnovi | 6 × Ø5 na r=17.3 |
| ležajevi | 2× 6802ZZ + 1× 6808-2RS |
| gabarit | Ø70 × 38.7 mm |
| izlazni moment | ~6.8 Nm, 0.09°/pun korak |

## Pravila koja se ne smiju prekršiti

1. **`2*ECC <= R_PIN`** — inače vrh režnja prelazi kružnicu trnova, ležište
   obuhvata manje od pola prečnika i trnovi ispadaju u otvor.
2. **`OUT_HOLE_D = OUT_PIN_D + 2*ECC`** — geometrijski uslov spojnice, nije zazor.
3. **`ECC * N_PINS / R_PC < 1`** — trohoidni odnos (ovdje 0.727).
4. **Diskovi A i B nisu isti dio.** Profil disku B kasni 180°/režnjevi (ovdje 9°)
   jer sjedi na suprotnom bregu. Uvijek generiraj dva zasebna STL-a.

## Obavezna provjera prije modeliranja
Prije nego se išta gradi u Blenderu, numerički provjeri profil:

- polarni kut mora biti **strogo monoton** → nema undercuta
- zazor prema svakom trnu u nominalnoj geometriji mora biti **0.0000 mm**
  (tangentnost — dokaz da je envelopa tačna)
- radijalni budžet diska: rebro između centralnog otvora i rupa za trnove, te
  između rupa i korijena zuba, ne smije pasti ispod ~1.5 mm
- mreža: Euler V−E+F = 2, nula non-manifold ivica

Ako bilo što od toga padne, ispravi parametre prije modeliranja — ne poslije.

## Štampa
PETG ili ABS, 4 perimetra, 40–60% infill, 0.2 mm sloj, bez podrške.
PLA samo za probu — puzi pod stalnim opterećenjem u zglobu.
Prestegnuto → `CLR` 0.20 i preštampaj diskove. Zazor u prenosu → `CLR` 0.10.
