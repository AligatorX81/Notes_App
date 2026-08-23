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

Konacne vrednosti se fiksiraju tek posle proracuna momenata (korak 3 u sekciji 6),
kada budu poznati domet i nosivost.

## 4. Konstruktivne odluke za cikloidne stepene

Vazi za oba stepena (M2 i M3):

- **Dupli disk pomeren 180°** — obavezno, zbog balansiranja ekscentra i vibracija
- **Čelični pinovi + igličasti/kuglični ležajevi** na pinovima prstena i na
  izlaznim čepovima — bez toga se štampani profil brzo troši
- **Kaljena ekscentrična osovina** na dva ležaja
- Zazor (offset cikloidnog profila) — parametar koji se štimuje po toleranciji
  proizvodnje, tipično 0.05–0.15 mm za štampu

## 5. Referentni dizajn

*(popuniti — broj osa, domet, nosivost, tip motora, materijal, izvor inspiracije)*

- Broj osa:
- Domet:
- Nosivost:
- Motori:
- Materijal kućišta:
- Poznat open-source projekat kao osnova (AR4 / Thor / Moveo / Annin / drugo):

## 6. Sledeći koraci

1. Popuniti sekciju 5 na osnovu referentnog videa
2. Odabrati alat za modelovanje (parametarski kod: CadQuery/OpenSCAD, ili ručni CAD)
3. Proračun momenata po zglobu → konačni prenosni odnosi i izbor motora
4. Generisanje cikloidnog profila za J2, J3, J5
