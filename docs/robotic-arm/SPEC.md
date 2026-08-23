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

Pravilo "svaki drugi motor" važi približno, ali kod klasične 6-osne kinematike
postoje **dva pitch zgloba zaredom** (rame i lakat):

| Zglob | Tip ose | Funkcija | Cikloidni? | Napomena |
|-------|---------|----------|-----------|----------|
| J1 | yaw (vertikalna) | rotacija baze | ne | nosi inerciju cele ruke, ali ne gravitaciju |
| J2 | pitch | rame / elevacija | **da** | najveći moment u sistemu |
| J3 | pitch | lakat / elevacija | **da** | drugi po momentu |
| J4 | roll | rotacija podlaktice | ne | remen ili planetarni |
| J5 | pitch | zglob šake / elevacija | **da** | najmanji od tri cikloidna |
| J6 | roll | rotacija alata | ne | direktan ili mali remen |

→ 3 cikloidna reduktora, 3 jednostavna prenosa.

**Otvoreno pitanje:** ako referentna ruka ima drugačiju kinematiku (npr. J2 i J3
razdvojeni rotacionom osom), raspored se menja i tada "svaki drugi motor"
važi doslovno. Potvrditi prema videu.

## 3. Orijentacione vrednosti prenosa

Moment opada kako se ide ka alatu, pa ne moraju svi cikloidni biti isti:

| Zglob | Predlog odnosa | Razlog |
|-------|----------------|--------|
| J2 | ~35–40:1 | nosi celu ruku + teret na punom kraku |
| J3 | ~25–30:1 | nosi podlakticu + teret |
| J5 | ~20:1 | nosi samo alat/teret |

Odnos cikloidnog: `i = Zp / (Zp - Zd)`, gde je `Zp` broj pinova prstena, a `Zd`
broj zuba diska (obično `Zd = Zp - 1`, pa je `i = Zp - 1`... zavisno od toga da
li je izlaz disk ili prsten). Fiksira se pri proračunu profila.

## 4. Konstruktivne odluke za cikloidne stepene

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
