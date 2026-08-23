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

## 5. Firmware — otvoreno pitanje

**Klipper nema kinematiku za petoosnu zglobnu ruku.** Podrzava cartesian,
corexy, delta, rotary_delta, polar, winch — ne i serijsku ruku.

Dve opcije:

1. **Sopstveni kinematicki modul u Klipperu** — C + Python, veci posao, ali daje
   pravu real-time kontrolu.
2. **Offline pretvaranje G-koda u uglove zglobova** — putanje su unapred poznate,
   pa se inverzna kinematika moze uraditi pre stampe i ruci poslati vec
   izracunati uglovi. Izvodljivije.

Odluka nije hitna, ali utice na to da li su enkoderi u zatvorenoj petlji ili
samo za kalibraciju.

---

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
