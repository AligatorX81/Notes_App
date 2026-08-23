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
