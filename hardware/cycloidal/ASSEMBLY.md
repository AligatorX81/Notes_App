# Cikloidni reduktor 20:1 za NEMA17

Parametarski generator za Blender. Motor **nije** modeliran — koristi se samo
njegov montažni interfejs (31 mm M3 raspored, Ø22 pilot, Ø5 osovina).

## Pokretanje

```bash
blender -b -P cycloidal_drive.py        # headless, izveze STL u ~/cyclo_out
```
ili u Blenderu: **Scripting → Open → Run Script**. Za pregled sklopa stavi
`EXPORT = False` i `EXPLODE = 6.0`.

## Zašto 20:1

| | |
|---|---|
| Prenosni odnos | **20:1** (21 trn / 20 režnjeva) |
| Izlazni moment | ~6.7 Nm (0.45 Nm × 20 × 0.75 η) |
| Rezolucija | 0.09°/full step, 0.0056° pri 1/16 mikrokoraka |
| Gabarit | Ø70 × 38.7 mm iznad prirubnice motora |

Za zglob robotske ruke to je dobra sredina: dovoljno momenta da drži segment
bez struje držanja na granici, a režnjevi su još uvijek 1.8 mm visoki pa se
čisto štampaju s 0.4 mm dizne. Veća redukcija (npr. 30:1) smanjila bi zub
ispod granice pouzdane štampe pri ovom promjeru.

## Geometrija — provjereno

Profil je *roller-offset epitrohoida*, tačna envelopa prstena trnova:

```
psi = atan2( sin((1-N)t),  R/(E·N) - cos((1-N)t) )
x   =  R·cos(t) - Rr·cos(t+psi) - E·cos(N·t)
y   = -R·sin(t) + Rr·sin(t+psi) + E·sin(N·t)
```

Numerički potvrđeno prije modeliranja:

- polarni kut **strogo monoton** → nema undercuta (najuži korak 0.027°)
- zazor prema svakom od 21 trna u nominalnoj geometriji **točno 0.0000 mm**
  (tangentnost — dokaz da je envelopa tačna); s `CLR` postaje ravnomjernih 0.15 mm
- mreža diska: Euler V−E+F = 2, nula non-manifold ivica → zatvoreno tijelo

### Dva pravila koja se ne smiju prekršiti pri mijenjanju parametara

1. **`2·ECC ≤ R_PIN`** — inače vrh režnja prelazi kružnicu trnova, ležište trna
   obuhvata manje od pola prečnika i trnovi ispadaju u otvor. Ovdje: 1.8 ≤ 2.5.
2. **`OUT_HOLE_D = OUT_PIN_D + 2·ECC`** — geometrijski uslov spojnice, ne zazor.
   Skript to računa sam; ne diraj ručno.

Pomoćni uslov: `ECC·N_PINS/R_PC < 1` (ovdje 0.727).

## Diskovi A i B nisu isti dio

Disk B sjedi na suprotnom ekscentru, pa mu profil kasni za pola koraka režnja
(180°/20 = 9°) dok rupe za izlazne trnove ostaju na mjestu. Skript generiše dva
zasebna STL-a — **nemoj štampati isti dva puta.**

*(Napomena: period profila je 18°, pa su +9° i −9° isti dio — smjer rotacije
ne može biti pogrešan.)*

## Štampani dijelovi

PETG ili ABS, 4 perimetra, 40–60% infill, **bez podrške**, 0.2 mm sloj.

| Fajl | Kom | Orijentacija |
|---|---|---|
| `01_housing.stl` | 1 | bazom nadolje |
| `03_disc_A.stl` | 1 | plosnato |
| `04_disc_B.stl` | 1 | plosnato |
| `05_eccentric_cam.stl` | 1 | plosnato, 6 perimetara |
| `06_output_flange.stl` | 1 | pločom nadolje |
| `07_front_cover.stl` | 1 | plosnato |

PLA radi za probu, ali puzi pod stalnim opterećenjem u zglobu — za stvarnu ruku
uzmi PETG ili ABS.

## Kupovni dijelovi

| Kom | Dio |
|---|---|
| 21 | cilindrični trn Ø5 × 16 mm (prsten) |
| 6 | cilindrični trn Ø5 × 22 mm (izlaz) |
| 2 | ležaj 6802ZZ 15×24×5 (diskovi, na ekscentru) |
| 1 | ležaj 6808-2RS 40×52×7 (izlaz) |
| 6 | M3×16 samorezni (poklopac) |
| 4 | M3×8 (na motor, kroz otvor) |
| 1 | M3 crvić (ekscentar na osovinu) |

## Redoslijed sklapanja

1. M3×8 kroz otvor kućišta pričvrsti bazu na motor (glave ulaze u upuštenja).
2. Ekscentar na osovinu, crvić na ravninu osovine. Provjeri da su režnjevi
   na 180° — donji ka +X, gornji ka −X.
3. Utisni 6802 u disk A i disk B (sjedaju na 1 mm ramena).
4. Disk A na donji ekscentar, pa disk B na gornji.
5. Ubaci 21 trn Ø5×16 u ležišta prstena odozgo.
6. Utisni 6 trnova Ø5×22 u prirubnicu (slijepe rupe, 7 mm), spusti kroz oba diska.
7. 6808 na glavčinu Ø40, oslonjen na pločicu prirubnice.
8. Poklopac preko ležaja, 6 × M3×16.
9. Segment ruke na 4 × M4 na čelu glavčine (r = 13 mm), Ø16 pilot udubljenje.

Okreni rukom prije napajanja — mora se vrtjeti glatko uz mali otpor. Ako je
prestegnuto, povećaj `CLR` na 0.20 i preštampaj diskove; ako ima zazora u
prenosu, smanji na 0.10.

## Izmjena redukcije

Promijeni samo `N_PINS`; `N_LOBES` prati automatski i odnos je `N_PINS−1 : 1`.
Nakon izmjene provjeri da `2·ECC ≤ R_PIN` i dalje vrijedi i da visina zuba
(2·ECC = 1.8 mm) ostaje iznad ~1.2 mm, inače zubi postaju presitni za štampu.

## Status

Matematika profila, radijalni budžet, aksijalni sklop i topologija mreže su
numerički provjereni. **Same boolean operacije nisu izvršene** — u ovom
kontejneru nema Blendera. Pokreni skript lokalno; ako neki boolean padne,
javi mi poruku i sredim to.
