# Robotska ruka — specifikacija (radna verzija)

> Status: rana faza. Referentni video (YouTube Shorts `b2AzL5bor0w`) nije bio dostupan
> asistentu — vizuelni opis ruke treba dopuniti ručno u sekciji "Referentni dizajn".

## 1. Osnovni princip pogona

**Cikloidni reduktor se ugrađuje isključivo na zglobove elevacije.**

- Zglob koji podiže masu protiv gravitacije (pitch / elevacija) → **cikloidni reduktor**
- Zglob koji samo rotira oko sopstvene uzdužne ose (roll / yaw) → **bez cikloidnog**
  (dovoljan je remen, planetarni ili direktan pogon)

Obrazloženje: cikloidni daje visok prenosni odnos, visok moment i nizak backlash u
kompaktnom koaksijalnom pakovanju, uz nisku backdrivability — što je tačno ono što
treba zglobu koji mora da *drži* pozu pod opterećenjem. Rotacione ose ne nose
statički moment gravitacije, pa je tu cikloidni nepotrebna masa, cena i trenje.

### Posledica koju treba imati u vidu
Rotacione ose i dalje traže *neki* prenos. Direktan pogon koračnog motora na roll
osi je slab i lako se okreće spolja. Za njih: zupčasti remen (npr. 3:1–5:1) ili
mali planetarni.

## 2. Raspored zglobova

Konfiguracija: **6 motora, 2 cikloidna reduktora** (rame i lakat).

| Motor | Tip ose | Funkcija | Cikloidni? | Prenos ako nema cikloidnog |
|-------|---------|----------|-----------|----------------------------|
| M1 | yaw (vertikalna) | rotacija baze | ne | remen ili planetarni, ~4:1 |
| M2 | pitch | **rame / elevacija** | **da** | — |
| M3 | pitch | **lakat / elevacija** | **da** | — |
| M4 | — | zglob šake | ne | vidi napomenu ispod |
| M5 | roll (predlog: pitch) | orijentacija grippera | ne | puzni prenos ako postane pitch |
| M6 | linearni/prstasti | gripper otvaranje/zatvaranje | ne | aktuator, nije zglob |

Rame i lakat nose gotovo sav moment u sistemu, pa oni dobijaju cikloidni. Sve
ostalo ostaje lagano — što je samo po sebi dobitak, jer svaki gram na kraju ruke
direktno povecava opterecenje M2 i M3.

### Napomena: M4 i M5

M4 je **roll** (uvrtanje podlaktice) — gravitacija ga ne opterecuje, dovoljan je
remen. Vidi sekciju 2a: kako je opisano, M4 i M5 dele istu osu, sto je otvoreno
pitanje.

Ako M5 postane pitch (predlog u 2a), nosi samo gripper na kratkom kraku. Bez
cikloidnog, ali mu treba prenos koji drzi pozu:

1. **Puzni prenos (worm)** — samokociv, drzi bez struje, jeftin. Prvi izbor.
2. **Planetarni reduktor na NEMA17**, ~20–30:1 — gotov, kompaktan.
3. **Zupcasti remen** ~5:1 — najlaksi, ali verovatno nedovoljan da drzi teret
   bez stalnog drzanja struje na motoru.

## 2a. Segmentacija projekta

Ruka se razvija kao pet zasebnih modula. Svaki je zaseban CAD sklop i moze se
projektovati i stampati nezavisno.

| # | Modul | Sadrzaj | Motori |
|---|-------|---------|--------|
| 1 | **Baza / podnozje** | kuciste, BTT Octopus Pro, napajanje, motor rotacije. Osovina motora viri iznad baze i nosi celu ruku. | M1 |
| 2 | **Koren ruke** | motor elevacije, montiran uz osovinu iz baze; elevira celu ruku | M2 |
| 3 | **Nadlaktica** | od elevacionog motora do zgloba; na zglobu **dva motora** — elevacija i rotacija sledeceg segmenta | M3, M4 |
| 4 | **Zglob pred gripperom** | orijentacija grippera | M5 |
| 5 | **Gripper** | pogon hvatanja | M6 |

### Kinematicki lanac

```
BAZA -[M1 yaw]- RAME -[M2 pitch]- NADLAKTICA -[M3 pitch]-+-[M4 roll]- PODLAKTICA -[M5]- GRIPPER -[M6]
                                                          |
                                                     isti zglob
```

### OTVORENO: M4 i M5 su, kako je opisano, ista osa

Ako je podlaktica prava, M4 (uvrtanje podlaktice) i M5 (rotacija grippera)
rotiraju oko **iste uzduzne ose**. To je jedan stepen slobode izveden dvaput —
jedan motor ne doprinosi nista novo.

Efektivno: **4 stepena slobode**, ne 5.

Posledica: u vertikalnoj ravni postoje samo dva zgloba (M2, M3). Dva zgloba daju
dva stepena slobode — dovoljno da se **dodje do tacke** (domet + visina), ali ne
i da se bira **ugao pod kojim gripper prilazi**. Nagib grippera je posledica
pozicije, a ne izbor.

**Predlog: M5 postaje pitch umesto roll.** Neka savija gripper gore-dole umesto
da ga uvrce. Tri pitch zgloba u vertikalnoj ravni daju polozaj **i** ugao
prilaza. M4 tada ostaje roll i prestaje da bude suvisan.

M5 kao pitch jeste elevacioni zglob, ali nosi samo gripper na kratkom kraku —
**i dalje bez cikloidnog**. Puzni prenos je dovoljan i uz to samokociv, pa
gripper ne pada kad se iskljuci struja.

**Alternativa:** zadrzati raspored i izbaciti M4 ili M5, posto rade isti posao.
Ustedi se motor, drajver i masa na kraju ruke.

### Napomena o masi na zglobu (modul 3)
Dva motora na istom zglobu su koncentrisana masa na sredini ruke i direktno
opterecuju M2. Ako se pokaze kao problem, motor za roll se moze pomeriti blize
korenu i pogon preneti remenom.

## 3. Orijentacione vrednosti prenosa (cikloidni)

| Zglob | Predlog odnosa | Razlog |
|-------|----------------|--------|
| M2 (rame) | ~35–40:1 | nosi celu ruku + teret na punom kraku |
| M3 (lakat) | ~25–30:1 | nosi podlakticu, saku, gripper + teret |

Konacne vrednosti se fiksiraju tek posle proracuna momenata (korak 4 u sekciji 7),
kada budu poznati domet i nosivost.

## 4. Elektronika — drajveri koracnih motora

### Raspodela (predlog)

| Motor | Osa | Drajver | Bus | Obrazlozenje |
|-------|-----|---------|-----|--------------|
| M1 | baza, yaw | TMC2240 | SPI | ubrzava inerciju cele ruke pri malom odnosu |
| M2 | **rame (cikloidni)** | **TMC5160T Pro** | SPI | najveci motor, treba naponska rezerva |
| M3 | **lakat (cikloidni)** | **TMC5160T Pro** | SPI | drugi po velicini |
| M4 | zglob sake | TMC2240 | SPI | mali prenosni odnos → trazi moment |
| M5 | rotacija grippera | TMC2226 | UART | roll osa, bez gravitacionog opterecenja |
| M6 | gripper | TMC2226 | UART | aktuator, mala snaga |

### Zasto veliki drajveri idu na cikloidne ose

Nije zbog statickog momenta — cikloidni reduktor od 25–40:1 sam rasterecuje motor.
Razlog je **brzina**: pri visokom odnosu motor mora da se vrti brzo da bi zglob
imao upotrebljivu brzinu, a moment koracnog motora naglo opada sa obrtajima.
Jedini lek je visi napon, i tu TMC5160 (60V) ima znacajnu prednost nad
TMC2240 (36V).

### Naponske sine — kriticno

Maksimalni naponi napajanja:

| Drajver | Max V | Struja (orijentaciono) |
|---------|-------|------------------------|
| TMC2226 | 29 V | ~2.0 A RMS |
| TMC2240 | 36 V | ~2.1 A RMS |
| TMC5160T Pro | 60 V | vise A, eksterni MOSFET-i |

Ako se ide na 48V za M2/M3 (a to je jedini razlog da se uopste uzme 5160),
**TMC2226 to ne izdrzava** — 29V mu je granica. Potrebne su dve sine:

- **48 V** → M2, M3 (TMC5160T Pro)
- **24 V** → ostali

### Resenje preko BTT Octopus Pro v1.1

Octopus Pro resava ovo bez zasebnog napajanja i bez buck konvertera:

- `MOTOR_POWER` port prima do **60 V**, `Main Power` do 28 V
- **svaki od 8 slotova bira napon nezavisno, preko jumpera**

Raspored jumpera:

| Slot | Drajver | Sina |
|------|---------|------|
| M2 rame | TMC5160T Pro | `MOTOR_POWER` 48 V |
| M3 lakat | TMC5160T Pro | `MOTOR_POWER` 48 V |
| M1, M4 | TMC2240 | `Main Power` 24 V |
| M5, M6 | TMC2226 | `Main Power` 24 V |

Osam slotova pokriva svih sest motora, uz dva u rezervi.

**Proveriti fizicki:** TMC5160T Pro je krupan modul sa hladnjakom i ventilatorom —
potvrditi da dva takva ne blokiraju susedne slotove.

**Kamera:** Octopus Pro nema CSI/MIPI konektor niti bilo kakav interfejs za
kameru. To je iskljucivo motion-control ploca. Kamera ide na host SBC
(Raspberry Pi), preko USB-a ili CSI-ja na samom Pi-ju.

### Napomene
- Kontroler mora imati **i SPI i UART** — 2240/5160 su SPI, 2226 je UART.
- StallGuard (dostupan na 2240 i 5160) omogucava homing bez krajnjih prekidaca
  na cikloidnim osama.
- Otvoreno: da li ici na zatvorenu petlju sa enkoderima na izlazu zgloba.
  Pri visokom cikloidnom odnosu izgubljen korak motora je mali u prostoru
  zgloba, pa je otvorena petlja podnosljiva za pocetak.

## 5. Konstruktivne odluke za cikloidne stepene

Vazi za oba stepena (M2 i M3):

- **Dupli disk pomeren 180°** — obavezno, zbog balansiranja ekscentra i vibracija
- **Čelični pinovi + igličasti/kuglični ležajevi** na pinovima prstena i na
  izlaznim čepovima — bez toga se štampani profil brzo troši
- **Kaljena ekscentrična osovina** na dva ležaja
- Zazor (offset cikloidnog profila) — parametar koji se štimuje po toleranciji
  proizvodnje, tipično 0.05–0.15 mm za štampu

## 6. Referentni dizajn

*(popuniti — domet, nosivost, tip i velicina motora, materijal, izvor inspiracije)*

- Broj osa:
- Domet:
- Nosivost:
- Motori:
- Materijal kućišta:
- Poznat open-source projekat kao osnova (AR4 / Thor / Moveo / Annin / drugo):

## 7. Sledeći koraci

1. Odluciti o M4/M5 redundanciji (vidi 2a) — M5 kao pitch ili izbaciti jedan motor
2. Popuniti sekciju 6 na osnovu referentnog videa
3. ~~Odabrati alat za modelovanje~~ — odluceno: CadQuery + FreeCAD 1.0 (vidi `cad/README.md`)
4. Proračun momenata po zglobu → konačni prenosni odnosi i izbor motora
5. Generisanje cikloidnog profila za M2 i M3
