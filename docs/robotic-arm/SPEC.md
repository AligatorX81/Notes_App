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
| M5 | roll | rotacija grippera | ne | direktan ili mali remen |
| M6 | linearni/prstasti | gripper otvaranje/zatvaranje | ne | aktuator, nije zglob |

Rame i lakat nose gotovo sav moment u sistemu, pa oni dobijaju cikloidni. Sve
ostalo ostaje lagano — što je samo po sebi dobitak, jer svaki gram na kraju ruke
direktno povecava opterecenje M2 i M3.

### Napomena: M4 (zglob sake)
Ako je M4 **pitch** osa, ona i dalje radi protiv gravitacije — nosi gripper i
teret, samo na kratkom kraku. Bez cikloidnog joj treba ili samokocivi prenos
(puz/worm) ili dovoljan odnos da drzi pozu bez backdrivinga. Opcije po
prioritetu:

1. **Puzni prenos (worm)** — samokocivi, drzi bez struje, jeftin. Mana: trenje
   i nizak stepen korisnosti, ali na ovoj osi to nije bitno.
2. **Planetarni reduktor na NEMA17**, ~20–30:1 — kompaktan, dostupan gotov.
3. **Zupcasti remen** ~5:1 — najlaksi, ali sam po sebi verovatno nedovoljan da
   drzi teret bez drzanja struje na motoru.

Ako je M4 **roll** osa (rotacija podlaktice), gravitacija je nije briga i
dovoljan je remen. **Potvrditi tip ose M4.**

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
**TMC2226 to ne izdrzava.** Potrebna je dupla sina:

- **48 V** → M2, M3 (TMC5160T Pro)
- **24 V** → ostali (buck konverter sa 48V ili zasebno napajanje)

Ako sve ostane na 24V, TMC5160T Pro ne donosi znacajnu prednost nad TMC2240.

### Napomene
- Kontroler mora imati **i SPI i UART** — 2240/5160 su SPI, 2226 je UART.
- **TMC5169 ne postoji** kao proizvod (Trinamic/ADI ima 5130, 5160, 5161, 5240,
  5271). Pretpostavka je da se misli na TMC5160T Pro — potvrditi.
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

1. Potvrditi tip ose M4 (pitch ili roll) i oznaku velikog drajvera (TMC5160T Pro?)
2. Popuniti sekciju 6 na osnovu referentnog videa
3. Odabrati alat za modelovanje (parametarski kod: CadQuery/OpenSCAD, ili ručni CAD)
4. Proračun momenata po zglobu → konačni prenosni odnosi i izbor motora
5. Generisanje cikloidnog profila za M2 i M3
