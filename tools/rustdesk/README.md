# RustDesk — priprema za nenadzirani pristup

Skripte koje na **vašem laptopu** instaliraju RustDesk i podese ga za
unattended (nenadzirani) pristup: instalacija, servis koji se diže s
sustavom, trajna lozinka i ispis ID-a s kojim se spajate s drugog uređaja.

> Ove skripte nisu dio Notes App aplikacije — stoje u `tools/` kao pomoćni
> alat i ništa u buildu ih ne dira.

## Upotreba

### Linux (Pop!_OS, Debian/Ubuntu, Fedora/RHEL, openSUSE)

```bash
sudo ./setup-rustdesk.sh
```

### Windows

```powershell
# PowerShell kao administrator
powershell -ExecutionPolicy Bypass -File .\setup-rustdesk.ps1
```

### macOS

```bash
./setup-rustdesk.sh
```

Na macOS-u skripta instalira RustDesk preko Homebrewa i tu staje — dodjelu
dozvola za *Screen Recording* i *Accessibility* Apple ne dopušta skriptirati,
pa ta četiri koraka odradite ručno (skripta ih ispiše).

## Što skripta radi

1. Prepozna OS, distribuciju i arhitekturu.
2. Dohvati **najnovije** izdanje s GitHub API-ja i iz njega izabere
   odgovarajući paket uzorkom imena (ne hardkodira verziju, pa ne puca kad
   RustDesk promijeni shemu imenovanja).
3. Preuzme paket, provjeri da nije prazan i ispiše mu SHA256.
4. Instalira ga kroz nativni package manager.
5. Uključi i pokrene RustDesk servis (`systemctl enable --now rustdesk`,
   odnosno `--install-service` na Windowsu).
6. Pričeka da servis registrira ID (do 60 s).
7. Postavi trajnu lozinku i restarta servis da je pročita.
8. Ispiše **ID + lozinku + verziju**.

## Opcije

Na Linuxu preko varijabli okruženja, na Windowsu preko parametara:

| Linux (env)         | Windows (param) | Značenje                                        |
|---------------------|-----------------|-------------------------------------------------|
| `RUSTDESK_PASSWORD` | `-Password`     | Trajna lozinka; prazno ⇒ generira se nasumična   |
| `RUSTDESK_VERSION`  | `-Version`      | Tag verzije (npr. `1.4.2`); prazno ⇒ najnovija   |
| `RUSTDESK_SHA256`   | `-Sha256`       | Očekivani SHA256 paketa — **preporučeno**        |
| `RUSTDESK_SERVER`   | `-Server`       | Vlastiti (self-hosted) rendezvous server         |
| `RUSTDESK_RELAY`    | —               | Vlastiti relay; default = `RUSTDESK_SERVER`      |
| `RUSTDESK_API`      | —               | URL vlastitog API servera                        |
| `RUSTDESK_KEY`      | `-Key`          | Javni ključ vlastitog servera                    |

Primjer sa self-hosted serverom:

```bash
sudo RUSTDESK_SERVER=rd.mojadomena.hr \
     RUSTDESK_KEY=abc123...= \
     ./setup-rustdesk.sh
```

### O provjeri integriteta

Bez `RUSTDESK_SHA256` skripta ne provjerava integritet — samo ispiše hash
preuzetog paketa. Preuzimanje ide preko HTTPS-a s GitHuba, što pokriva
većinu slučajeva, ali za pouzdano zaključavanje verzije uzmite hash iz
službenog izdanja i proslijedite ga skripti.

## Provjera nakon instalacije

```bash
systemctl status rustdesk      # servis mora biti active (running)
rustdesk --get-id              # ispisuje vaš ID
journalctl -u rustdesk -n 50   # log ako nešto ne radi
```

Na Windowsu:

```powershell
Get-Service RustDesk
& "$env:ProgramFiles\RustDesk\rustdesk.exe" --get-id
```

## Mrežni preduvjeti

RustDesk klijent mora prema van doći do rendezvous i relay servera:

| Protokol | Port          | Čemu služi                          |
|----------|---------------|-------------------------------------|
| TCP      | 21115         | NAT type test                       |
| TCP+UDP  | 21116         | **registracija ID-a (UDP)**, NAT punching (TCP) |
| TCP      | 21117         | relay (hbbr)                        |
| TCP      | 21118 / 21119 | WebSocket varijante                 |

Ako laptop nikad ne dobije ID, gotovo uvijek je uzrok blokiran **UDP 21116** —
bez njega se klijent ne može registrirati i nitko se ne može spojiti, koliko
god ostalo bilo ispravno podešeno.

## Pop!_OS

Pop!_OS je Ubuntu baza, pa ide `.deb` grana skripte — instalacija prolazi
kroz `apt` bez dodatnih koraka.

Bitno je koji je display server:

- **Pop!_OS 22.04 (GNOME)** — prema zadanome X11, što je za nenadzirani
  pristup ispravno i ništa ne treba mijenjati.
- **Pop!_OS 24.04 / COSMIC** — Wayland, gdje unattended pristup zna zakazati
  (vidi niže). Za pouzdan rad prijavite se u Xorg sesiju.

Provjera trenutne sesije:

```bash
echo $XDG_SESSION_TYPE       # ocekivano: x11
```

Skripta i sama detektira Wayland — i kad se pokrene pod `sudo`, gdje se
`XDG_SESSION_TYPE` gubi, pa tip sesije čita iz `loginctl`.

## Wayland

Na Waylandu (GNOME na Ubuntu 22.04+ / Fedora) RustDesk ima ograničenu podršku
za nenadzirani pristup — dijeljenje ekrana i simulacija unosa znaju zakazati
kad nitko nije prijavljen. Za pouzdan unattended pristup na ekranu za prijavu
odaberite **Xorg / X11** sesiju. Skripta upozori ako detektira Wayland.

## Sigurnost

- Generirana lozinka ima ~117 bita entropije (20 znakova, abeceda od 58 bez
  ambigviteta tipa `0`/`O`, `1`/`l`). **Nigdje se ne sprema** osim u RustDesk
  config — zapišite je u password manager odmah, ispis se ne ponavlja.
- **ID i lozinku ne šaljite istim kanalom.**
- Trajna lozinka znači da se bilo tko s ID-om i lozinkom može spojiti bez
  potvrde na laptopu. Ako vam to nije potrebno, izbrišite trajnu lozinku u
  *Settings → Security* i koristite jednokratnu lozinku koju očitate s ekrana.
- Za punu kontrolu nad prometom razmislite o vlastitom serveru
  (`RUSTDESK_SERVER`) umjesto javne RustDesk infrastrukture.
- Laptop mora biti budan da bi bio dostupan — provjerite postavke štednje
  energije i ponašanje na zatvaranje poklopca.
