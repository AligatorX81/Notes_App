# Rezim 3D stampe — mlaznica kao alat

Ruka treba da drzi hotend i izvrsava zadatke 3D stampe. Ploca za stampu stoji
**pored ruke, u nivou gornje povrsine baze**.

Ovo je zaseban rezim rada sa bitno strozim zahtevom za tacnost od hvatanja i
premestanja, i menja sta je u konstrukciji kriticno.

---

## 1. Zasto 5 osa odgovara

Mlaznica je rotaciono simetricna — svejedno je pod kojim je uglom zaokrenuta oko
sopstvene ose. Za stampu treba **polozaj (3) + pravac mlaznice (2) = 5**.

Sesta osa bi za stampu bila beskorisna. Odluka o 5 osa (SPEC.md, sekcija 2a) je
za ovaj zadatak optimalna, ne kompromis.

---

## 2. Budzet greske

Cilj za FDM: vrh mlaznice tacan na **~0.1 mm**.

| Domet | Potrebna ugaona tacnost |
|-------|-------------------------|
| 600 mm | 0.0095° (0.57 lucnih minuta) |
| 400 mm | 0.0143° |
| 300 mm | 0.0191° |
| 200 mm | 0.0286° |

### Rezolucija — nije problem

NEMA17 (1.8°), 1/16 mikrokoraka, cikloidni 35:1:

```
1.8 / 16 / 35 = 0.0032° po mikrokoraku  =  0.034 mm na 600 mm
```

Trostruka rezerva u odnosu na cilj.

### Zazor — ovde je granica

| Zazor u zglobu | Greska @600 mm | @300 mm |
|----------------|----------------|---------|
| 0.20° (tipican stampani cikloidni) | 2.09 mm | 1.05 mm |
| 0.10° (pazljiva izrada) | 1.05 mm | 0.52 mm |
| 0.05° (celicni pinovi, lezajevi, predopterecenje) | 0.52 mm | 0.26 mm |
| **0.0095° (potrebno)** | **0.10 mm** | — |

Stampani cikloidni sklop je i u najboljem slucaju **5–10x grublji** od onoga sto
FDM trazi na punom dometu.

---

## 3. Tri izmene koje iz ovoga slede

### 3.1 Dve radne zone

| Zona | Domet | Namena |
|------|-------|--------|
| **Hvatanje / premestanje** | do 600 mm | pun domet, tacnost nebitna |
| **Stampa** | **200–350 mm** | ploca se postavlja ovde |

Ista ugaona greska na upola manjem kraku daje upola manju linearnu gresku.
Ploca se ne postavlja na kraju dometa.

**Napomena o singularnosti:** ploca je u nivou gornje povrsine baze, dakle ruka
radi savijena blizu sopstvene baze. To je i podrucje najlosije uslovljenosti
kinematike — treba proveriti da radna zona ne ulazi u polozaje gde mali pomeraj
alata trazi veliki pomeraj zgloba.

### 3.2 Enkoderi na IZLAZU zgloba

Zazor se moze kompenzovati samo ako se meri **posle** reduktora.

- Magnetni enkoder (npr. AS5048A, 14-bit = 0.022°) na **osi zgloba**, ne na
  osovini motora
- Enkoder na motoru ne vidi zazor reduktora i ne pomaze
- Prioritet: **M2 i M3**

### 3.3 Prioritet preciznosti na M2 i M3

Greska svakog zgloba mnozi se rastojanjem do mlaznice:

| Zglob | Rastojanje do mlaznice | Doprinos gresci |
|-------|------------------------|-----------------|
| M2 rame | ~600 mm | **najveci** |
| M3 lakat | ~340 mm | veliki |
| M4 roll | ~100 mm | mali |
| M5 zglob | ~50 mm | zanemarljiv |

Sav trud u tolerancije, celicne pinove, lezajeve i predopterecenje ide u **M2 i
M3**. Na M4 i M5 se ne isplati.

---

## 3.4 Sta redukcija radi za preciznost — i sta ne radi

Cikloidni odnos 40:1 **jeste** uracunat u sve momente (0.59 Nm x 40 x 0.75 =
17.7 Nm u zglobu). Bez njega ruka ne bi drzala ni samu sebe.

Za **preciznost** vazi drugacije. Redukcija deli sa 40 samo greske nastale
**pre** reduktora:

| Izvor | U zglobu | Na 600 mm |
|-------|----------|-----------|
| mikrokorak 1/16 | 0.0028° | 0.029 mm |
| greska koraka motora | 0.0023° | 0.024 mm |

Te greske su prakticno obrisane. Ali ono sto nastaje **u reduktoru i posle
njega** ne deli se ni sa cim:

| Izvor | Na 600 mm |
|-------|-----------|
| zazor cikloidnog 0.05° (vrlo dobra izrada) | 0.52 mm |
| zazor cikloidnog 0.10° (realno) | 1.05 mm |
| **ugib konstrukcije** (PETG 40x40, zid 3 mm) | **4.48 mm** |

Reduktor je i sam izvor zazora — ne uklanja ga, nego ga uvodi.

### KRITICNO: ugib konstrukcije je dominantan izvor greske

Veci je od zazora reduktora. Prioritet preciznosti nije samo u reduktoru, nego
**prvenstveno u krutosti konstrukcije**.

| Presek | Ugib @600 mm | Masa segmenta |
|--------|--------------|---------------|
| PETG 40x40, zid 3 mm | 4.48 mm | ~290 g |
| PETG 60x60, zid 4 mm | 0.97 mm | ~680 g |
| PETG 80x80, zid 5 mm | 0.32 mm | ~1140 g |
| **2x karbonska cev Ø25x1 mm, razmak 30 mm** | **0.29 mm** | **~145 g** |

**Preporuka: karbonske cevi kao nosiva kicma.** Stampani delovi postaju kucista
zglobova i spojnice; nosivi raspon preuzimaju cevi ulepljene u njih. Karbon je
~15x kruci od PETG-a i pritom 4x laksi od preseka koji bi dao slican ugib — a
manja masa dodatno smanjuje moment na ramenu.

### Ugib je kompenzabilan, zazor nije

- **Ugib** je deterministicka funkcija poze i tereta. Firmware je nas, pa se
  moze **racunati i kompenzovati u softveru** — bez ijedne dodatne komponente.
  Najisplativija mera u projektu.
- **Zazor** menja znak sa smerom kretanja. Softver ga ne moze predvideti —
  trazi enkoder na izlazu zgloba (3.2).

---

## 4. Konstruktivne posledice

### Masa i kablovi hotenda
- **Bowden ekstruder** — motor ekstrudera na bazi ili nadlaktici, ne na vrhu.
  Direktni pogon bi dodao ~400 g tamo gde masa najvise boli.
- Kroz ruku do vrha treba sprovesti: grejac (24 V, ~40 W ≈ 1.7 A), termistor,
  ventilator hlađenja, ventilator hotenda. To je znatan dodatak na kablovske
  kanale iz `3D-PRINT.md`.

### Toplota
- Hotend radi na 200–250 °C. **PLA delovi ruke u blizini vrha nisu prihvatljivi.**
- Materijal konstrukcije: PETG, ASA ili ABS, posebno za modul 4 i 5.
- Toplotna izolacija izmedju hotenda i nosaca.

### Krutost
- Kod hvatanja je bitna nosivost; kod stampe je bitna **krutost**. Savijanje
  segmenta pod sopstvenom tezinom direktno pomera mlaznicu.
- Preseci segmenata se dimenzionisu prema ugibu, ne prema cvrstoci.

---

## 5. Firmware

**Na plocu je vec napisan i flesovan sopstveni bare metal firmware i radi.**
Kinematika je time nasa odluka, ne ogranicenje gotovog alata.

(Ranija napomena da Klipper ne podrzava petoosnu zglobnu ruku ovde ne vazi —
Klipper se i ne koristi.)

Ostaje da se odluci gde se racuna inverzna kinematika:

1. **U firmware-u, u realnom vremenu** — potpuna kontrola, veci posao na MCU-u
2. **Offline, pre stampe** — putanje su unapred poznate, pa se G-kod moze
   pretvoriti u uglove zglobova i firmware-u slati vec izracunato

Izbor utice na to da li su enkoderi (3.2) u zatvorenoj petlji ili sluze samo za
kalibraciju i proveru.

## 6. Realno ocekivanje

Ova ruka ce stampati na **~0.3–0.5 mm tacnosti**, ne 0.1 mm. To znaci
funkcionalne komade, ne fini detalj. Kvalitet kartezijanskog stampaca se ovako
ne dobija.

**Ono sto ruka moze a kartezijanski ne:**
- stampa po zakrivljenim povrsinama
- neplanarni slojevi
- stampa bez potpornih struktura
- stampa na vec postojeci predmet

Tu je njena stvarna vrednost, i tu 5 osa zaista dolazi do izrazaja.
