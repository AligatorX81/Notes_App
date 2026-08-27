# OctoArm — cikloidni reduktori za zglobove ruke (rukovanje konzervama)

**Verzija:** 1.0 · **Datum:** 2026-08-27
**Predmet:** analiza tri referentna cikloidna prenosnika, izbor parametara i prilagođenje zglobovima OctoArm manipulatora za pick-and-place konzervi.

> **Napomena o izvorima.** Stranice `printables.com` i `thingiverse.com` su blokirane kroz mrežni proxy ove sesije, pa modeli nisu preuzeti niti mereni direktno. Sve navedene specifikacije referentnih dizajna su prikupljene iz javno indeksiranih opisa i komentara i **označene su kao „prijavljeno"**. Sve što je izvedeno računom označeno je kao **„računato"**. Pre proizvodnje treba preuzeti STL/STEP fajlove i verifikovati kritične kote (E, R, Rr) merenjem.

---

## 1. Referentni dizajni — šta smo naučili

### 1.1 Lev Hovhera — 30:1 za NEMA 17 (Printables 1582476)

| Stavka | Vrednost | Izvor |
|---|---|---|
| Prenosni odnos | 30:1 | prijavljeno |
| Broj diskova | 2, pomereni 180° | prijavljeno |
| Ležajevi | samo 2× **608** (8×22×7) | prijavljeno |
| Spojni elementi | isključivo M3 vijci | prijavljeno |
| Izmeren moment | **9.5 Nm trajno, 10.5 Nm pik** | prijavljeno |
| Materijal / motor | PETG / NEMA 17, 59 Ncm (0.59 Nm) | prijavljeno |
| Implicirani stepen korisnosti | η ≈ 9.5 / (0.59 × 30) = **0.54** | računato |

**Vrednost za nas:** dokazana referenca „koliko momenta realno daje štampani cikloid na NEMA 17". Dva diska 180° van faze poništavaju radijalnu inercijalnu silu i prepolovljuju talasanje momenta — to je **obavezno** za zglob robota, jer inače vibracija ulazi u kinematički lanac. BOM je minimalan (2 ležaja), što je odlično za cenu, ali znači da izlaz nema sopstveni ležaj velikog prečnika — moment savijanja mora da preuzme nešto drugo.

### 1.2 gouldpa — „Rework Simple 25:1 Cycloidal Actuator" (Thingiverse 4781349)

| Stavka | Vrednost | Izvor |
|---|---|---|
| Prenosni odnos | 25:1 | prijavljeno |
| Parametri profila | **N = 25, E = 1 mm, Rr = 2 mm, R = 31.5 mm** | prijavljeno |
| Čivijci prstena | Ø3 mm srebrni čelik (silver steel), dužina 32 mm | prijavljeno |
| Ležajevi | **6810** (50×65×7), 6704 (27×20×4), 6701 (18×12×4), 6700 (15×10×4), MR85 (8×5×2.5) | prijavljeno |
| Faktor zahvata K₁ = E·N/R | 1 × 25 / 31.5 = **0.79** (agresivno, gornja granica) | računato |
| Arhitektura | „pancake" — nizak, veliki tanki izlazni ležaj | prijavljeno |

**Vrednost za nas:** ovo je jedini od tri dizajna koji je **stvarno aktuator, a ne samo reduktor**. Tanki ležaj 6810 (50 mm unutrašnji, 65 mm spoljašnji, 7 mm širine) preuzima moment savijanja direktno u zglobu — tačno ono što treba ramenu i bazi ruke, gde zglob nosi konzolu. Kaljeni Ø3 čelični čivijci umesto štampanih su jedina ispravna odluka; štampani čivijci se izližu za nekoliko stotina ciklusa.

### 1.3 Edukativni model cikloidnog prenosnika (Printables 1453110)

Presečeni/otvoreni demonstracioni model. Nije nosiva konstrukcija i **ne ulazi u OctoArm kao komponenta**.

**Vrednost za nas — dvostruka, i nije zanemarljiva:**
1. **Verifikacija profila.** Pre nego što potrošimo dan na štampu nosivog zgloba, štampamo edukativni model sa *našim* parametrima (naš N, E, R, Rr) i rukom proverimo da li se disk kotrlja bez zapinjanja i bez zazora. Kvar u jednačini profila se ovde vidi za 20 minuta umesto posle sklapanja celog zgloba.
2. **Kalibracija zazora.** Otvoren sklop dozvoljava da se izmeri stvarni backlash i podesi korekcija `Rr + δ` (vidi §5.3) pre nego što se pređe na zatvoreno kućište.

---

## 2. Geometrija cikloidnog profila — jednačine koje koristimo

Uz oznake: `R` = poluprečnik kružnice čivijaka prstena, `Rr` = poluprečnik čivijka, `E` = ekscentricitet, `N` = broj čivijaka prstena, `n = N − 1` = broj režnjeva diska.

```
ψ(t) = atan2( sin((1−N)·t) ,  R/(E·N) − cos((1−N)·t) )

x(t) =  R·cos(t) − Rr·cos(t + ψ(t)) − E·cos(N·t)
y(t) = −R·sin(t) + Rr·sin(t + ψ(t)) + E·sin(N·t)
```

za `t ∈ [0, 2π)`, uzorkovano sa najmanje **2000 tačaka po punom krugu** (ispod ~1000 se na režnjevima vidi fasetiranje koje pravi mikro-zapinjanje).

**Prenosni odnos** (prsten fiksiran, ulaz = ekscentar, izlaz = disk preko čivijaka/rupa):

```
i = n / (N − n) = n / 1 = N − 1
```

**Faktor zahvata** (ključan projektni parametar):

```
K₁ = E·N / R
```

| K₁ | Ponašanje |
|---|---|
| < 0.4 | plitki režnjevi, mali moment, disk „preskače" pod opterećenjem |
| **0.55 – 0.75** | **preporučeni radni opseg** |
| > 0.8 | rizik od podsecanja (undercut), visok kontaktni napon, težak hod |

gouldpa je na 0.79 — radi, ali je na ivici. Za OctoArm ciljamo **K₁ ≈ 0.70**.

**Izlazna spojnica (čivijak-u-rupi):** prečnik rupe = prečnik izlaznog čivijka + `2E`. Broj izlaznih čivijaka: 6 ili 8, na kružnici poluprečnika ≈ `0.5·R`.

---

## 3. Kritično ograničenje: ekscentricitet vs. tačnost štampe

Iz `E = K₁·R / N` sledi da za **visok odnos u malom kućištu ekscentricitet postaje sitan**, a sitan ekscentricitet je neupotrebljiv na FDM štampi.

Primer — 30:1 (N=31) u kućištu sa R = 30 mm, K₁ = 0.70:

```
E = 0.70 × 30 / 31 = 0.68 mm
```

Pri tipičnoj FDM tačnosti od ±0.1 mm, to je **greška od 15 % na najosetljivijoj koti u celom sklopu**. Rezultat je nejednak zazor po obodu: disk negde zapinje, negde ima luft.

**Pravilo koje usvajamo za OctoArm:**

> **E ≥ 1.0 mm.** Ako parametri daju manje, ili se poveća `R` (veće kućište), ili se smanji odnos `i` i razlika nadoknadi remenskim pred-stepenom.

Ovo je razlog zašto **ne kopiramo 30:1 direktno**, nego idemo na 25:1 / 20:1 uz remen tamo gde treba više.

---

## 4. Prilagođenje OctoArm-u

### 4.1 Radne pretpostavke

Pošto geometrija OctoArm-a nije bila dostupna u ovom repozitorijumu, proračun je urađen na sledećem modelu — **zameniti stvarnim vrednostima i preračunati** (tabele u §4.3 su linearne po masi i po kraku, pa je preračun trivijalan):

| Stavka | Pretpostavka |
|---|---|
| Konzerva (nosivost) | 0.40 kg (standardna limenka ~400 g) |
| Hvataljka | 0.35 kg |
| Nadlaktica L1 | 250 mm, 0.70 kg |
| Podlaktica L2 | 250 mm, 0.50 kg |
| Sklop lakta (motor + reduktor) | 0.60 kg |
| Ukupan domet | 500 mm |
| Ciklus | pick-and-place, pokret ~0.5 s, α ≈ 10 rad/s² |
| Stepen korisnosti štampanog cikloida | **η = 0.60** (konzervativno, iz §1.1) |

### 4.2 Izbor arhitekture po zglobu

Tri referentna dizajna daju tri različita načina uglobljavanja i svaki ima svoje mesto:

| Arhitektura | Poreklo | Gde ide na OctoArm | Zašto |
|---|---|---|---|
| **Pancake, veliki tanki ležaj** | gouldpa 25:1 | **J1 baza, J2 rame** | izlazni ležaj 6810 preuzima moment savijanja konzole direktno u zglobu; nizak profil ne produžava krak |
| **Koaksijalni (motor iza reduktora)** | Hovhera 30:1 | **J3 lakat** | motor leži duž podlaktice, gde ionako ima mesta; minimalan BOM |
| **Odmaknut motor + remen** | (dopuna) | **J2 rame, pred-stepen 2:1** | masa motora ide bliže bazi → drastično smanjuje moment inercije ramena i statički moment |
| Nema cikloida | — | **J6 rotacija hvataljke** | moment je zanemarljiv; cikloid je nepotrebna masa. Planetarni ili direktan pogon. |

### 4.3 Predloženi parametri

Svi setovi drže **K₁ ≈ 0.70** i **E ≥ 1.0 mm**:

| Zglob | i | N (čivijaka) | n (režnjeva) | R [mm] | Rr [mm] | E [mm] | K₁ | Ø čivijka | Ø kućišta ≈ | Motor |
|---|---|---|---|---|---|---|---|---|---|---|
| **J1 baza** | 25:1 | 26 | 25 | 40 | 2.5 | 1.10 | 0.715 | 5 mm | 97 mm | NEMA 17 |
| **J2 rame** | 25:1 (+2:1 remen = 50:1) | 26 | 25 | 40 | 2.5 | 1.10 | 0.715 | 5 mm | 97 mm | NEMA 17 |
| **J3 lakat** | 20:1 | 21 | 20 | 32 | 2.0 | 1.05 | 0.689 | 4 mm | 78 mm | NEMA 17 |
| **J4 zglob (pitch)** | 16:1 | 17 | 16 | 24 | 1.5 | 1.00 | 0.708 | 3 mm | 60 mm | NEMA 14 |
| **J5 zglob (roll)** | 16:1 | 17 | 16 | 24 | 1.5 | 1.00 | 0.708 | 3 mm | 60 mm | NEMA 14 |
| **J6 hvataljka** | — | — | — | — | — | — | — | — | — | NEMA 8 / servo |

Izvedene kote: spoljni poluprečnik diska ≈ `R − Rr + E`; izlazne rupe na `≈ 0.5·R`, prečnik = Ø čivijka + `2E`.
Svi cikloidni zglobovi imaju **2 diska pomerena 180°** (preuzeto od Hovhere) — bez izuzetka.

### 4.4 Provera momenta

**Raspoloživo** (`T = T_motor × i × η`, η = 0.60):

| Zglob | T_motor | i | T_raspoloživo |
|---|---|---|---|
| J1 | 0.59 Nm | 25 | **8.85 Nm** |
| J2 | 0.59 Nm | 50 (25 × remen 2:1) | **17.7 Nm** |
| J3 | 0.59 Nm | 20 | **7.08 Nm** |
| J4 / J5 | 0.22 Nm (NEMA 14) | 16 | **2.11 Nm** |

**Zahtevano** — najgori slučaj, ruka horizontalno ispružena, konzerva u hvataljci:

| Zglob | Statički moment [Nm] | Dinamički [Nm] | Ukupno [Nm] | Rezerva (SF) |
|---|---|---|---|---|
| J4 zglob | 9.81 × (0.75 × 0.060) = **0.44** | ~0.05 | 0.49 | **4.3** ✔ |
| J3 lakat | 9.81 × (0.50×0.125 + 0.75×0.250) = **2.45** | ~0.35 | 2.80 | **2.5** ✔ |
| J2 rame | 9.81 × 0.800 = **7.85** | J≈0.31 kg·m² × 10 = **3.06** | 10.9 | **1.6** ✔ |
| J2 rame *bez remena* | 7.85 | 3.06 | 10.9 | **0.81** ✘ |

**Zaključak:** rame **ne prolazi** sa golim 25:1 na NEMA 17 (SF = 0.81, tj. ne može ni da podigne sopstvenu ruku ispruženu). Remenski pred-stepen 2:1 (ili prelazak na NEMA 23) je **obavezan**. Svi ostali zglobovi prolaze sa zdravom rezervom.

Brzine na izlazu pri 300 o/min na motoru: J1 12 o/min (72 °/s), J2 6 o/min (36 °/s), J3 15 o/min (90 °/s). Za pick-and-place konzervi je to sasvim dovoljno; rame se ionako najmanje okreće.

---

## 5. Specifičnosti rada sa konzervama

Ovo je deo koji nijedan od tri referentna dizajna ne pokriva — svi su opšti reduktori.

### 5.1 Udarno opterećenje
Konzerva je gusta, kruta i teška za svoju veličinu. Pri hvatanju i odlaganju ide udar u kinematički lanac. **Ovo je glavni argument za cikloid umesto planetarnog**: opterećenje se deli na ~N/2 čivijaka u kotrljajućem kontaktu, pa nema pojedinačnog zuba koji prima udar. Zadržati kaljene čelične čivijke (gouldpa) — štampani čivijci ovde otpadaju odmah.

### 5.2 Zaptivanje i higijena
Prehrambeno okruženje znači vlagu, ulje i pranje. Referentni dizajni imaju otvorene prstenove čivijaka — **to menjamo**:
- Zatvoreno kućište, **radijalni zaptivač na izlazu** (za J1/J2 sa ležajem 6810: 50×65×8 gumeni zaptivač).
- O-prsten na spoju polovina kućišta.
- **Mast: PFPE ili silikonska, klase H1** (prehrambeno bezbedna). Litijumske i mineralne masti napadaju PETG i PA — ne koristiti.
- Bez rastvarača pri čišćenju štampanih delova.

### 5.3 Zazor (backlash)
Cilj: **0.2 – 0.4°** na izlazu. Zazor se ne podešava naknadno — ugrađuje se u profil, tako što se u jednačinama iz §2 koristi `Rr + δ` umesto `Rr`:

| δ | Efekat |
|---|---|
| 0.00 mm | disk zapinje, nemoguće sklopiti |
| **0.05 – 0.10 mm** | **radni opseg za dobro kalibrisanu štampu** |
| > 0.15 mm | osetan luft, gubi se glavna prednost cikloida |

Kalibrisati na edukativnom modelu (§1.3) pre štampe nosivih delova.

### 5.4 Puzanje materijala (creep) — bezbednosno pitanje
PETG puzi pod trajnim opterećenjem, naročito iznad 40 °C. Ruka koja satima drži konzervu ispruženo **polako propada**.
- Diskovi i kućište: **PETG-CF ili PA6-CF** (najlon sa ugljenikom), ne običan PETG.
- Za J2 rame: **kočnica pri nestanku napajanja ili protivteg/opružna kompenzacija.**
- Pri 25:1 i η_povratno ≈ 0.3–0.4 prenosnik **otežava** povratni pogon ali **nije samokočiv**. Ne oslanjati se na trenje kao na bezbednosnu funkciju kada je konzerva iznad radne zone.

---

## 6. BOM po zglobu (J1 / J2, tip „pancake")

| Poz. | Komponenta | Specifikacija | Kom. |
|---|---|---|---|
| 1 | Izlazni ležaj | 6810 (50×65×7), tanki presek | 1 |
| 2 | Ležaj ekscentra | 6802 (15×24×5) | 2 |
| 3 | Ulazni ležaj | 608 (8×22×7) | 1 |
| 4 | Čivijci prstena | Ø5 h6 kaljeni čelik, L = 2×debljina diska + 4 mm | 26 |
| 5 | Izlazni čivijci | Ø8 kaljeni + čaura/ležaj MR128 | 6 |
| 6 | Cikloidni diskovi | PA6-CF / PETG-CF, štampani | 2 |
| 7 | Kućište (2 dela) | PA6-CF / PETG-CF | 1 set |
| 8 | Zaptivač izlaza | 50×65×8 radijalni | 1 |
| 9 | O-prsten kućišta | prema Ø kućišta | 1 |
| 10 | Vijci | M4×16 / M3×12 inox | ~16 |
| 11 | Mast | PFPE ili silikonska, H1 | — |

Za J3 (koaksijalni, po Hovheri) BOM je znatno kraći: 2× 608, Ø4 čivijci ×21, 2 diska, kućište, M3.

---

## 7. Parametri štampe

| Parametar | Diskovi | Kućište |
|---|---|---|
| Materijal | PA6-CF / PETG-CF | PA6-CF / PETG-CF |
| Visina sloja | **0.15 mm** | 0.20 mm |
| Ispuna | **100 %** | 40 % gyroid |
| Obodi (perimeters) | **6** | 4 |
| Orijentacija | **ravno položen** (opterećenje u ravni slojeva) | podeljeno po ravni spoja |
| Horizontalna kompenzacija | kalibrisati na test-cilindru, tipično **−0.10 do −0.15 mm** | isto |

Rupe za čivijke prstena razvrtati (reamer) na konačnu meru — štampana rupa nikad nije dovoljno tačna za Ø5 h6.

---

## 8. Redosled realizacije

1. **Verifikacija profila** — generisati profil po §2 sa parametrima za J3 (najmanji rizik), odštampati edukativni model preseka (§1.3), potvrditi hod bez zapinjanja.
2. **Kalibracija δ** — na istom modelu odrediti `δ` koje daje 0.2–0.4° zazora.
3. **Prototip J3 (lakat, 20:1)** — najjednostavnija arhitektura, najveća rezerva momenta. Izmeriti stvarni η i maksimalni moment na kočnici.
4. **Preračun** — vratiti izmereno η u tabelu §4.4. Ako je η < 0.5, rame ide na NEMA 23, ne na remen 2:1.
5. **Prototip J1/J2 (pancake, 25:1)** — tek posle koraka 4.
6. **Test trajnosti** — 10 000 pick-and-place ciklusa sa konzervom, merenje porasta zazora. Ovo je test koji odlučuje da li PETG-CF prolazi ili se mora na PA6-CF/POM.

---

## 9. Otvorena pitanja za potvrdu

- Stvarne dužine segmenata i mase OctoArm-a (pretpostavke iz §4.1 treba zameniti).
- Broj stepeni slobode i da li J5/J6 čine diferencijalni zglob (menja proračun za J4/J5).
- Maksimalna nosivost — jedna konzerva ili pakovanje? Kod 2 kg umesto 0.4 kg rame traži ~24 Nm i NEMA 23 postaje obavezan.
- Da li postoji zahtev za ponovljivost pozicije (npr. ±0.5 mm na dometu od 500 mm)? To postavlja gornju granicu zazora strožu od §5.3.

---

### Izvori

- [30:1 reduction cycloidal drive for NEMA 17 stepper — Lev Hovhera, Printables 1582476](https://www.printables.com/model/1582476-301-reduction-cycloidal-drive-for-nema-17-stepper)
- [Rework Simple 25:1 Cycloidal Actuator — gouldpa, Thingiverse 4781349](https://www.thingiverse.com/thing:4781349)
- [Educational model of cycloidal drive — Printables 1453110](https://www.printables.com/model/1453110-educational-model-of-cycloidal-drive)
- [Faze4 Robotic Arm — referenca za cikloidne zglobove + remenske pred-stepene](https://hackaday.io/project/167247-faze4-robotic-arm)
- [What is a Cycloidal Drive? — HowToMechatronics (jednačine profila)](https://howtomechatronics.com/how-it-works/what-is-cycloidal-driver-designing-3d-printing-and-testing/)
