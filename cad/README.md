# CAD — parametarski modeli

## Zasto CadQuery

CadQuery je Python biblioteka nad OpenCascade kernelom. Bitna razlika u odnosu
na Blender: pravi **B-rep solide**, ne mesh. Izlaz je STEP, koji se u Fusionu i
SolidWorksu otvara kao pravo telo sa ravnim povrsinama i tacnim precnicima —
ne kao trougaona mreza.

Sve se pokrece bez GUI-ja, pa se model moze generisati i proveriti automatski.

## Pokretanje

```bash
pip install cadquery
python3 cad/cycloidal_disc.py                 # podrazumevano M2 (rame), 35:1
python3 cad/cycloidal_disc.py --pins 29       # 28:1 za M3 (lakat)
```

Izlaz ide u `cad/out/` kao `.step` (za CAD) i `.stl` (za stampu).

## Sta sa Fusionom i SolidWorksom

STEP se uvozi u oba kao solid telo. Ogranicenje koje treba znati: **telo dolazi
bez istorije feature-a** — nema timeline-a koji se moze premotati. Parametri
zive u Python skripti umesto u CAD-u: promeni broj pinova, pokreni ponovo,
uvezi novi STEP.

Alternativa je da se napise nativna skripta za Fusion (Python, `Utilities →
Add-Ins → Scripts`) ili VBA makro za SolidWorks. Tada se dobija pravi
parametarski feature tree, ali se skripta mora pokretati na Windows/macOS
masini sa instaliranim programom.

## Cikloidni profil

Profil je hipocikloida sa ekvidistantom za poluprecnik pina:

```
psi(t) = atan2( sin((1-N)t),  R/(E*N) - cos((1-N)t) )
x(t)   =  R*cos(t) - Rr*cos(t + psi) - E*cos(N*t)
y(t)   = -R*sin(t) + Rr*sin(t + psi) + E*sin(N*t)
```

| Simbol | Znacenje |
|--------|----------|
| `R`  | poluprecnik kruga pinova prstena |
| `Rr` | poluprecnik pina (umanjen za zazor) |
| `E`  | ekscentricitet |
| `N`  | broj pinova prstena |

Prenosni odnos jednostepenog reduktora sa fiksnim prstenom i izlazom preko
cepova: **i = N − 1**.

### Dva uslova koja skripta proverava

1. **`E < R/N`** — inace profil ima podsecanje i disk je neupotrebljiv.
   Posledica: visok odnos znaci mali ekscentricitet, a mali ekscentricitet
   znaci uze tolerancije. Kod 35:1 i R=50 mm granica je 1.39 mm.
2. **Korak pinova > precnik pina** — inace se pinovi preklapaju.

Izlazni otvori imaju precnik `2*(Rout + E)`, jer disk tokom obrtaja opisuje
kruznicu poluprecnika `E` oko svakog izlaznog cepa.

## Trenutne vrednosti (privremene)

Vrednosti u `SHOULDER` su pocetna procena dok se ne uradi proracun momenata.
Nakon proracuna (korak 4 u `docs/robotic-arm/SPEC.md`) treba ih zameniti.

---

# Fusion — dva nacina

## Nacin A: uvoz STEP-a (preporuceno za pocetak)

CadQuery skripta se **ne pokrece u Fusionu** — koristi drugi kernel. Ona pravi
STEP, a Fusion ga uvozi.

1. `python3 cad/cycloidal_disc.py` → nastaje `cad/out/cycloidal_disc_M2.step`
2. U Fusionu: **File → Open** (ili Upload) → izaberi `.step`
3. Telo se pojavi kao pravi solid, sa tacnim precnicima i ravnim povrsinama

Prednost: brzo, radi odmah, isti fajl otvara i SolidWorks.
Mana: telo dolazi **bez timeline istorije** — moze se menjati direktnim
editovanjem, ali nema feature tree-a za premotavanje.

## Nacin B: nativna Fusion skripta

`cad/fusion/CycloidalDisc/` je prava Fusion skripta — gradi skicu, splajn i
extrude kroz Fusion API, pa nastaje telo **sa feature tree-om u timeline-u**.

### Instalacija

Kopiraj ceo folder `CycloidalDisc/` u Fusion-ov direktorijum za skripte:

| OS | Putanja |
|----|---------|
| Windows | `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\` |
| macOS | `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts/` |

Folder i `.py` fajl moraju imati **isto ime** — Fusion tako pronalazi skriptu.

### Pokretanje

1. U Fusionu otvori prazan **Design**
2. Kartica **Utilities → ADD-INS → Scripts and Add-Ins** (precica `Shift+S`)
3. Kartica **Scripts** → `CycloidalDisc` u listi **My Scripts** → **Run**

Ako se ne pojavi u listi, klikni **+** pored "My Scripts" i pokazi na folder.

### Menjanje parametara

Parametri su konstante na vrhu `CycloidalDisc.py`:

```python
PIN_COUNT = 36      # prenosni odnos = PIN_COUNT - 1, dakle 35:1
PIN_CIRCLE_R = 50.0
ECCENTRICITY = 1.0
```

Za lakat (M3, 28:1) postavi `PIN_COUNT = 29`. Skripta pre gradnje proverava
iste uslove kao CadQuery verzija i prekida sa porukom ako su prekrseni.

## Ogranicenje koje vazi za oba nacina

Cikloidni profil je **izracunata kriva**, provucena kroz stotine tacaka. Ne moze
se vezati za Fusion-ove User Parameters — promena prenosnog odnosa znaci ponovno
pokretanje skripte, ne prevlacenje broja u tabeli parametara. Timeline iz nacina
B je koristan za ono sto dolazi *posle* diska (zaobljenja, dodatni otvori,
sklop), ne za sam profil.

## Napomena o testiranju

CadQuery skripta je pokrenuta i provera je prosla. **Fusion skripta nije
testirana** — Fusion API radi samo unutar pokrenutog Fusiona na Windows/macOS,
pa je ovde nije bilo moguce izvrsiti. Proverena je samo sintaksa. Ako pukne pri
pokretanju, posalji tekst greske iz message box-a.

## Fusion na Linuxu (Pop!_OS)

Autodesk nema nativnu Linux verziju Fusiona. Opcije:

1. **cryinkfly instaler** (Wine) — podrzava Pop!_OS 20.04 / 22.04 / 24.04:
   https://codeberg.org/cryinkfly/Autodesk-Fusion-360-on-Linux
   Trazi wine 6.23+, winetricks, yad.
2. **Windows VM** — stabilnije, ali bez GPU passthrough-a je spor.
3. **Dual boot** — najpouzdanije.

### Posledica za ovaj projekat

Na Pop!_OS-u je **nacin A (STEP) pouzdaniji od nacina B**, suprotno od onoga
sto vazi na Windowsu. CadQuery je nativan na Linuxu i moze se pokrenuti i
proveriti automatski; Fusion pod Wine-om je sloj vise u kojem nista nije
provereno, a nativna Fusion skripta je ionako netestirana.

**Alternativa vredna razmatranja:** FreeCAD je nativan na Linuxu, otvara STEP
sa punim parametarskim editovanjem i ima CadQuery integraciju (Workbench).
Ako Fusion nije obavezan, otpada cela Wine prica.

---

# Izbor alata — odluka

**CadQuery (profili i delovi) + FreeCAD 1.0 (sklop i crtezi).**
Oba nativna na Linuxu, oba na istom OpenCascade kernelu, pa STEP putuje izmedju
njih bez gubitka. Bez Wine-a.

## Zasto ne Blender

Blender je mesh modeler — krug u njemu ne postoji, postoji poligon koji ga
aproksimira. Greska za otvor lezaja R = 11 mm:

| Segmenata | Poluprecnik | Greska | vs zazor 0.08 mm |
|-----------|-------------|--------|------------------|
| 16 | 10.789 mm | 0.211 mm | 2.6x |
| 32 | 10.947 mm | 0.053 mm | 0.7x |
| 64 | 10.987 mm | 0.013 mm | 0.2x |
| 256 | 10.999 mm | 0.0008 mm | zanemarljivo |

Na podrazumevanih 32 segmenta greska je 66% zazora koji projektujemo.

Vise segmenata to numericki popravlja, ali ne resava sustinu: u Blenderu je
preciznost nesto sto se **rucno odrzava**, a ne sto alat garantuje. Nema pojma
tolerancije, nema STEP izvoza (dakle nema predaje masinbravaru ni ozbiljnog
FEM-a), boolean operacije na gustim mrezama su krhke, zaobljenja su
aproksimacije. CAD kernel umesto toga cuva analiticku definiciju — cilindar je
osa i poluprecnik, tacnost ~1e-7 mm kroz svaku operaciju.

**Blender ostaje u projektu za render i animaciju gotovog sklopa** (uvoz STL-a).
To mu je prava uloga.

## Zasto FreeCAD 1.0, a ne ranije verzije

Verzija 1.0 je donela dve stvari koje su je ucinile upotrebljivom za ovo:

- resen **topological naming problem** — ranije bi izmena rane skice razbila
  kasnije feature-e
- ugradjen **Assembly Workbench**

Instalacija na Pop!_OS: AppImage sa freecad.org ili flatpak. `apt` cesto nosi
stariju verziju.

## Odbacene opcije

| Alat | Zasto ne |
|------|----------|
| Fusion 360 | nema nativni Linux; samo Wine ili VM |
| SolidWorks | Windows only |
| Blender | mesh, ne solid — vidi gore |

## Razmotreno, ostaje kao rezerva

**OnShape** — pun parametarski CAD u pregledacu, radi nativno na Linuxu bez
instalacije, kvalitet na nivou Fusiona. Kvaka: besplatan plan cini sve dokumente
javnim.
