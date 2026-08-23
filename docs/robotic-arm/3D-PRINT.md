# 3D stampa i sklapanje — zahtevi za modelovanje

## Osnovno pravilo

**Odstampan deo mora biti spreman za sklapanje bez naknadne obrade.** Posle
stampe se samo:

1. usrafe motori
2. montira ploca (BTT Octopus Pro)
3. sprovedu kablovi

Bez busenja, bez turpijanja, bez lepljenja nosaca. Sve rupe, kanali, lezista i
prolazi za kablove moraju postojati u modelu.

Posledica za modelovanje: svaki modul se projektuje **oko konkretnih komponenti**,
sa njihovim stvarnim merama, a ne kao ljuska u koju ce se nesto kasnije ugurati.

---

## Sta svaki modul mora da sadrzi

### Modul 1 — Baza
- leziste za **BTT Octopus Pro** sa distancerima i rupama za zavrtnje
- izrezi za konektore: USB, napajanje, CAN, izlazi za motore
- prolaz za kablove ka gore, **kroz osu rotacije M1**
- ventilacija iznad TMC5160T Pro modula (imaju ventilatore)
- leziste za napajanje ili prolaz za spoljasnje
- montaza motora M1 sa osovinom nagore
- glavni lezaj rotacije ruke

### Modul 2 — Koren ruke
- prihvat na osovinu M1
- montaza motora M2 uz osovinu iz baze
- kuciste cikloidnog reduktora M2: leziste prstena pinova, otvori za pinove,
  leziste ekscentricne osovine, izlazni cepovi
- prolaz kablova ka nadlaktici

### Modul 3 — Nadlaktica + podlaktica
- prihvat na izlaz cikloidnog reduktora M2
- na laktu: montaza **M3** i kuciste njegovog cikloidnog reduktora
- **odmah iza lakta, na podlaktici: montaza M4 (roll)** sa remenicom
- kanal za kablove duz oba segmenta
- prolaz kroz osu M4 (roll) — vidi "Kablovi kroz rotacione zglobove"

Redosled je bitan: cikloidni pitch (M3) pa tek onda roll (M4). Obrnuto bi
opteretilo roll motor ~10x jace — vidi `SPEC.md`, sekcija 2a.

### Modul 4 — Zglob pred gripperom
- montaza M5 kao **pitch** ose i njegovog **puznog prenosa**
- leziste puznog para (puz + puzno kolo), sa lezajevima na oba kraja puza
- prihvat grippera

### Modul 5 — Gripper
- montaza M6
- mehanizam prstiju

---

## Reference za montazu motora

Mere koje treba ugraditi u model (**potvrditi na konkretnim motorima pre
stampe** — postoje varijante):

| | NEMA 17 | NEMA 23 |
|---|---|---|
| Prirubnica | 42.3 mm | 56.4 mm |
| Raspored zavrtnjeva | 31.04 mm kvadrat | 47.14 mm kvadrat |
| Zavrtnji | 4 × M3 | 4 × M5 |
| Centrirni prsten | Ø22 mm | Ø38.1 mm |
| Osovina | Ø5 mm | Ø6.35 mm |

**Centrirni prsten se ne sme preskociti** — on nosi centriranje, ne zavrtnji.
Rupa za njega ide sa zazorom od 0.1–0.2 mm.

Za BTT Octopus Pro: dimenzije i pozicije rupa uzeti iz mehanickog crteza u
zvanicnom repozitorijumu, ne procenom.

---

## Zavrtnji i navoji u plastici

**Ne modelirati navoj direktno u plastici** za bilo sta sto se rasklapa.

Umesto toga **mesingani heat-set umeci**:

| Zavrtanj | Umetak (tipicno) | Rupa u modelu |
|----------|------------------|---------------|
| M3 | OD ~4.6 mm | Ø4.0 mm |
| M4 | OD ~5.6 mm | Ø5.0 mm |
| M5 | OD ~6.4 mm | Ø5.8 mm |

Tacne mere zavise od proizvodjaca umetaka — proveriti pre modelovanja.
Dubina rupe: duzina umetka + 1 mm rezerve za visak materijala.

---

## Tolerancije za FDM stampu

Rupe na FDM stampi izlaze **manje** od nominalne mere.

| Namena | Dodatak na precnik |
|--------|--------------------|
| Prolazna rupa za zavrtanj | +0.4 mm |
| Leziste (press fit) | +0.0 do +0.1 mm |
| Klizno naleganje | +0.3 mm |
| Vertikalni otvor Ø > 20 mm | +0.2 mm, uz proveru probnim komadom |

**Obavezno odstampati probni komad** sa nekoliko otvora razlicitih mera pre
nego sto se stampa ceo modul. Vrednosti zavise od stampaca, materijala i
mlaznice.

Cikloidni disk: zazor profila je vec parametar u skripti (`clearance`,
trenutno 0.08 mm) i stima se posle probne stampe.

---

## Kablovi kroz rotacione zglobove

Ovo je najcesci propust kod ovakvih ruku i tesko se popravlja naknadno.

Kabl koji prolazi kroz **rotacioni** zglob se uvrce pri svakoj rotaciji.
Resenja, po redosledu jednostavnosti:

1. **Prolaz kroz osu rotacije** — kabl ide kroz suplju osovinu ili kroz otvor
   u centru lezaja. Uvrtanje ostaje, ali je ravnomerno i podnosljivo ako se
   ogranici opseg (npr. ±180°).
2. **Ogranicenje opsega** — softverski i mehanicki granicnik, da kabl nikad ne
   predje dozvoljeni broj obrtaja.
3. **Klizni prsten (slip ring)** — neograniceno okretanje, ali dodatna cena i
   ugradnja.

Zglobovi kojih se ovo tice: **M1** (nosi kablove cele ruke) i **M4** (roll).

Za M1 je prolaz kroz osu prakticno obavezan — kroz njega ide sve od Octopusa
ka ostatku ruke.

Kanali za kablove: minimum 10 × 6 mm za snop stepper kablova po segmentu,
sa zaobljenim ulazima (bez ostrih ivica koje seku izolaciju) i mestom za
vezice kao rasterecenje.

---

## Orijentacija stampe

Slojevi su najslabija ravan dela. Orijentisati tako da opterecenje **ne**
razdvaja slojeve:

- **Segmenti ruke** — opterecenje na savijanje. Stampati po duzini, da slojevi
  ne budu upravni na pravac savijanja.
- **Cikloidni disk** — opterecenje je radijalno, u ravni diska. Stampati
  polozeno (ravno na plocu), sto je ujedno i najtacnije za profil.
- **Nosaci motora** — zavrtnji cupaju slojeve; ojacati zid oko rupa i
  izbegavati da sila deluje upravno na slojeve.

Za nosive delove: 4+ perimetra i 40%+ ispune. Delovi cikloidnog reduktora
zasluzuju vise.

---

## Sta jos treba proveriti

- [ ] Mehanicki crtez BTT Octopus Pro — tacne pozicije rupa
- [ ] Visina TMC5160T Pro modula sa ventilatorom (odredjuje visinu baze)
- [ ] Konkretni motori — potvrditi prirubnicu i osovinu
- [ ] Precnik i tip glavnog lezaja rotacije baze
- [ ] Probni komad za tolerancije na konkretnom stampacu
