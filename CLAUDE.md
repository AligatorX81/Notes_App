# Notes App — upute za Claude Code

## Radno okruženje (važno)

**Radi se isključivo lokalno, na Pop!_OS-u, kroz Claude Code u terminalu.**

Kontejnerske / web sesije (claude.ai/code) za ovaj projekt su neupotrebljive i
ne treba ih predlagati:

- kontejner je efemeran — nestaje nakon neaktivnosti, ništa u njemu ne
  preživi osim onoga što je pushano;
- nema grafičke sesije (`DISPLAY` je prazan), pa se aplikacija ne može
  stvarno vidjeti ni testirati na uređaju;
- izlazna mreža ide kroz proxy s allowlistom domena, a UDP je potpuno
  blokiran — sve izvan HTTPS-a prema dopuštenim domenama otpada;
- nema pristupa lokalnom Android uređaju za Capacitor build i testiranje.

Kad zadatak traži pokretanje aplikacije, rad s uređajem, mrežne alate ili
bilo što izvan uređivanja koda — pretpostavi lokalni Pop!_OS, ne kontejner.

## Pokretanje

```bash
npm install
npm run dev        # Vite dev server
npm run build      # tsc + vite build
npm run lint       # eslint, --max-warnings 0
```

## Android (Capacitor)

Pogledaj `README.android.md`. Build zahtijeva lokalni Android SDK i uređaj
ili emulator — dakle isključivo lokalno.

## Struktura

- `src/` — React + TypeScript izvorni kod
- `index.html`, `app.js` — ulazna točka
- `android/` — Capacitor Android projekt
- `tools/rustdesk/` — pomoćne skripte za RustDesk (nisu dio aplikacije,
  build ih ne dira)
