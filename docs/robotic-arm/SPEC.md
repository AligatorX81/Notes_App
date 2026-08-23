# Robotska ruka — specifikacija (radna verzija)

> **Status: konfiguracija potvrdjena.** Raspored osa, pogoni i segmentacija su
> zakljuceni. Otvoreno ostaje samo *domet i nosivost*, bez kojih su dimenzije
> u sekciji 3 procena.
>
> Referentni video (YouTube Shorts `b2AzL5bor0w`) nije bio dostupan asistentu —
> vizuelni opis ruke treba dopuniti rucno u sekciji "Referentni dizajn".

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

Konfiguracija: **6 motora, 5 stepeni slobode, 2 cikloidna reduktora** (rame i lakat).

> **6 motora ≠ 6 DOF.** M6 pokrece prste hvataljke i ne menja ni polozaj ni
> orijentaciju alata, pa ne ulazi u kinematicki lanac. Po standardnoj
> konvenciji broje se samo zglobovi koji nose alat — dakle M1 do M5.
> **5 osa + hvataljka = 6 motora.**

| Motor | Tip ose | Funkcija | Cikloidni? | Prenos ako nema cikloidnog |
|-------|---------|----------|-----------|----------------------------|
| M1 | yaw (vertikalna) | rotacija baze | ne | remen ili planetarni, ~4:1 |
| M2 | pitch | **rame / elevacija** (opseg nesto ispod 180°) | **da** | — |
| M3 | pitch | **lakat / elevacija** | **da** | — |
| M4 | roll | uvrtanje **podlaktice** (iza lakta) | ne | zupcasti remen |
| M5 | **pitch** | savijanje grippera, ugao prilaza | ne | **puzni prenos** (samokociv) |
| M6 | linearni/prstasti | gripper otvaranje/zatvaranje | ne | aktuator, nije zglob |

Rame i lakat nose gotovo sav moment u sistemu, pa oni dobijaju cikloidni. Sve
ostalo ostaje lagano — što je samo po sebi dobitak, jer svaki gram na kraju ruke
direktno povecava opterecenje M2 i M3.

### Napomena: M4 i M5

- **M4 = roll** (uvrtanje podlaktice). Gravitacija ga ne opterecuje — dovoljan
  je zupcasti remen.
- **M5 = pitch** (savijanje grippera). Elevacioni je, ali nosi samo gripper na
  kratkom kraku, pa ide bez cikloidnog. Pogon: **puzni prenos**, prvenstveno
  zato sto je samokociv i drzi pozu bez struje. Alternative ako puz ne odgovara:
  planetarni ~20–30:1, ili remen ~5:1 (ovaj poslednji verovatno nedovoljan da
  drzi teret bez stalnog drzanja struje).

Vidi sekciju 2a za obrazlozenje zasto M5 nije roll.

## 2a. Segmentacija projekta

Ruka se razvija kao pet zasebnih modula. Svaki je zaseban CAD sklop i moze se
projektovati i stampati nezavisno.

| # | Modul | Sadrzaj | Motori |
|---|-------|---------|--------|
| 1 | **Baza / podnozje** | kuciste, BTT Octopus Pro, napajanje, motor rotacije. Osovina motora viri iznad baze i nosi celu ruku. | M1 |
| 2 | **Koren ruke** | motor elevacije, montiran uz osovinu iz baze; elevira celu ruku | M2 |
| 3 | **Nadlaktica + podlaktica** | od M2 do lakta; na laktu **M3 sa cikloidnim** (elevira podlakticu), a **odmah iza njega, na podlaktici, M4 roll** (uvrce podlakticu) | M3, M4 |
| 4 | **Zglob pred gripperom** | savijanje grippera (pitch, puzni prenos) | M5 |
| 5 | **Gripper** | pogon hvatanja | M6 |

### Kinematicki lanac

```
BAZA
 └─[M1 yaw]──────── rotacija cele ruke
     └─[M2 pitch]── CIKLOIDNI ~35:1   elevacija cele ruke (<180°)
         │
      NADLAKTICA
         └─[M3 pitch]── CIKLOIDNI ~28:1   elevacija podlaktice   (lakat)
             └─[M4 roll]── remen              uvrtanje podlaktice
                 │
              PODLAKTICA
                 └─[M5 pitch]── PUZNI (samokociv)   ugao prilaza
                     │
                  GRIPPER
                     └─[M6]── pogon prstiju
```

**Redosled na laktu je bitan: cikloidni pitch (M3) pa tek onda roll (M4).**
Vidi "ODLUCENO: roll ide iza lakta" nize.

### ODLUCENO: M5 je pitch, ne roll

Prvobitni opis je M4 (uvrtanje podlaktice) i M5 (rotacija grippera) stavljao
oko **iste uzduzne ose** — jedan stepen slobode izveden dvaput. Efektivno bi to
bila ruka sa 4 stepena slobode, kod koje se moze doci do tacke, ali se ne moze
birati ugao pod kojim gripper prilazi.

**M5 je zato pitch: savija gripper gore-dole umesto da ga uvrce.**

Time M4 ostaje roll i prestaje da bude suvisan, a ruka ima punih **5 stepeni
slobode**:

| | Osa | Doprinos |
|---|-----|----------|
| M1 | yaw | zakret cele ruke |
| M2 | pitch | polozaj u vertikalnoj ravni |
| M3 | pitch | polozaj u vertikalnoj ravni |
| M4 | roll | ravan u kojoj M5 savija |
| M5 | pitch | ugao prilaza grippera |

Sto daje: **pun polozaj (3) + pravac prilaza (2)**.

Sto ne daje: nezavisan zaokret alata oko sopstvene ose kada je prilaz vec
fiksiran — to trazi sesti zglob.

### ODLUCENO: roll ide IZA lakta, ne ispred

Prvobitni opis je stavljao roll **iznad** lakta — izmedju ramena i lakta. Odbaceno.

Roll osa tada ide uzduz nadlaktice, a teziste svega iza nje (laktni motor,
cikloidni reduktor M3, podlaktica, zglob, gripper) **nije na toj osi**. Kad je
nadlaktica vodoravna a lakat savijen, gravitacija pravi moment koji roll motor
mora da drzi:

| Varijanta | Sta roll nosi | Moment |
|-----------|---------------|--------|
| roll **iznad** lakta | lakat + cikloidni M3 + podlaktica + gripper | ~2.1 Nm |
| roll **iza** lakta (usvojeno) | zglob M5 + gripper | ~0.2 Nm |

Deset puta razlika. Laktni sklop sam — cikloidni reduktor plus motor — tezi oko
**830 g**, uglavnom celik (36 pinova, lezajevi, ekscentar). Roll iznad lakta bi
morao da nosi i vrti tu masu na kraku, cime bi postao treci po opterecenju u
ruci i trazio jak prenos — upravo ona slozenost koju osnovno pravilo (sekcija 1)
izbegava.

Sa rollom iza lakta, on nosi samo gripper i remen mu je zaista dovoljan.

Ovo je uz to i redosled koji koriste industrijski sestoosni roboti:
yaw, pitch, pitch, **roll**, pitch.

### ODLUCENO: ostaje 5 osa

Pun 6-DOF trazio bi **sedmi motor** — roll iza M5, na samom gripperu. Odbaceno:
masa na samom kraju ruke direktno opterecuje M2 i M3, dakle i oba cikloidna
reduktora koja projektujemo, a za hvatanje i premestanje se sesta osa retko
oseti.

Ako se kasnije pokaze da je potrebna, modul 4 je zaseban segment i moze se
zameniti bez diranja ostatka ruke.

**Pogon M5:** puzni prenos. Nosi samo gripper na kratkom kraku, pa cikloidni
nije potreban — a puz je samokociv, sto znaci da gripper ne pada kad se
iskljuci struja.

### Napomena o masi na zglobu (modul 3)
Dva motora na istom zglobu su koncentrisana masa na sredini ruke i direktno
opterecuju M2. Ako se pokaze kao problem, motor za roll se moze pomeriti blize
korenu i pogon preneti remenom.

## 3. Orijentacione vrednosti prenosa (cikloidni)

| Zglob | Predlog odnosa | Razlog |
|-------|----------------|--------|
| M2 (rame) | ~35–40:1 | nosi celu ruku + teret na punom kraku |
| M3 (lakat) | ~25–30:1 | nosi podlakticu, saku, gripper + teret |

Konacne vrednosti se fiksiraju tek posle proracuna momenata (korak 3 u sekciji 7),
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

1. Popuniti sekciju 6 na osnovu referentnog videa
2. ~~Odabrati alat za modelovanje~~ — odluceno: CadQuery + FreeCAD 1.0 (vidi `cad/README.md`)
3. Proračun momenata po zglobu → konačni prenosni odnosi i izbor motora
4. Generisanje cikloidnog profila za M2 i M3
