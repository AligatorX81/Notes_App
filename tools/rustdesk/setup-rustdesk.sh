#!/usr/bin/env bash
#
# Instalira RustDesk i priprema ga za unattended (nenadzirani) pristup.
#
#   sudo ./setup-rustdesk.sh
#
# Na kraju ispisuje RustDesk ID i trajnu lozinku s kojima se spajate
# s drugog uredaja.
#
# Podrzano: Debian/Ubuntu (.deb), Fedora/RHEL/openSUSE (.rpm), macOS (Homebrew).
#
# Varijable okruzenja (sve opcionalne):
#   RUSTDESK_PASSWORD   trajna lozinka; ako je prazno, generira se nasumicna
#   RUSTDESK_VERSION    tag verzije, npr. 1.4.2; ako je prazno, uzima najnoviju
#   RUSTDESK_SHA256     ocekivani sha256 preuzetog paketa (preporuceno)
#   RUSTDESK_SERVER     host vlastitog rendezvous servera (self-hosted)
#   RUSTDESK_RELAY      host vlastitog relay servera; default = RUSTDESK_SERVER
#   RUSTDESK_API        URL vlastitog API servera
#   RUSTDESK_KEY        javni kljuc vlastitog servera
#
set -euo pipefail

RUSTDESK_PASSWORD="${RUSTDESK_PASSWORD:-}"
RUSTDESK_VERSION="${RUSTDESK_VERSION:-}"
RUSTDESK_SHA256="${RUSTDESK_SHA256:-}"
RUSTDESK_SERVER="${RUSTDESK_SERVER:-}"
RUSTDESK_RELAY="${RUSTDESK_RELAY:-${RUSTDESK_SERVER}}"
RUSTDESK_API="${RUSTDESK_API:-}"
RUSTDESK_KEY="${RUSTDESK_KEY:-}"

GH_API="https://api.github.com/repos/rustdesk/rustdesk/releases"

log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m /!\\\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m!!!\033[0m %s\n' "$*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || die "nedostaje alat: $1"; }

# ---------------------------------------------------------------- lozinka ---
# Bez ambigviteta: bez 0/O, 1/l/I. 20 znakova iz 58-znakovne abecede ~ 117 bita.
gen_password() {
  local alphabet='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'
  local out=''
  # Napomena: neograniceni izvor (< /dev/urandom) uz `head -c` salje SIGPIPE
  # tr-u, sto uz `set -o pipefail` rusi skriptu s exit 141. Zato ulaz omedimo.
  if command -v openssl >/dev/null 2>&1; then
    out="$(LC_ALL=C tr -dc "$alphabet" < <(openssl rand 512) | head -c 20)"
  elif [[ -r /dev/urandom ]]; then
    out="$(LC_ALL=C tr -dc "$alphabet" < <(head -c 4096 /dev/urandom) | head -c 20)"
  else
    die "nema ni openssl ni /dev/urandom - ne mogu generirati lozinku"
  fi
  [[ ${#out} -eq 20 ]] || die "generiranje lozinke nije uspjelo"
  printf '%s' "$out"
}

# ------------------------------------------------------------- detekcija ----
detect_platform() {
  OS="$(uname -s)"
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64|amd64)   ARCH=x86_64 ;;
    aarch64|arm64)  ARCH=aarch64 ;;
    *) die "nepodrzana arhitektura: $ARCH" ;;
  esac

  if [[ "$OS" == "Darwin" ]]; then
    PKG=macos
    return
  fi
  [[ "$OS" == "Linux" ]] || die "nepodrzan OS: $OS"

  if command -v apt-get >/dev/null 2>&1; then
    PKG=deb
  elif command -v dnf >/dev/null 2>&1 || command -v zypper >/dev/null 2>&1; then
    PKG=rpm
  else
    die "ne prepoznajem package manager (ocekujem apt-get, dnf ili zypper)"
  fi
}

require_root() {
  [[ "$PKG" == "macos" ]] && return 0
  [[ "$(id -u)" -eq 0 ]] || die "pokrenite kao root: sudo $0"
}

# ---------------------------------------------------------------- preuzmi ---
# Ime asseta se kroz verzije mijenjalo, pa ga ne hardkodiramo nego biramo
# regexom iz GitHub release API-ja.
resolve_asset() {
  local url json
  if [[ -n "$RUSTDESK_VERSION" ]]; then
    url="$GH_API/tags/${RUSTDESK_VERSION}"
  else
    url="$GH_API/latest"
  fi

  log "Trazim izdanje: $url"
  json="$(curl -fsSL -H 'Accept: application/vnd.github+json' "$url")" \
    || die "ne mogu dohvatiti podatke o izdanju s GitHuba"

  TAG="$(printf '%s' "$json" | grep -o '"tag_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | cut -d'"' -f4)"
  [[ -n "$TAG" ]] || die "ne mogu procitati tag izdanja"

  local pattern
  case "$PKG" in
    deb) pattern="${ARCH}\\.deb$" ;;
    rpm) pattern="${ARCH}\\.rpm$" ;;
  esac

  ASSET_URL="$(printf '%s' "$json" \
    | grep -o '"browser_download_url"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | cut -d'"' -f4 \
    | grep -Ei "$pattern" \
    | head -1)"

  [[ -n "$ASSET_URL" ]] \
    || die "u izdanju $TAG nema paketa koji odgovara /$pattern/ (arhitektura $ARCH)"
  log "Izdanje $TAG -> $(basename "$ASSET_URL")"
}

download() {
  TMPDIR_RD="$(mktemp -d)"
  # shellcheck disable=SC2064
  trap "rm -rf '$TMPDIR_RD'" EXIT
  PKG_FILE="$TMPDIR_RD/$(basename "$ASSET_URL")"

  log "Preuzimam paket"
  curl -fSL --retry 3 --retry-delay 2 -o "$PKG_FILE" "$ASSET_URL" \
    || die "preuzimanje nije uspjelo"

  [[ -s "$PKG_FILE" ]] || die "preuzeta datoteka je prazna"

  local actual
  actual="$(sha256sum "$PKG_FILE" 2>/dev/null | cut -d' ' -f1)" \
    || actual="$(shasum -a 256 "$PKG_FILE" | cut -d' ' -f1)"

  if [[ -n "$RUSTDESK_SHA256" ]]; then
    [[ "$actual" == "$RUSTDESK_SHA256" ]] \
      || die "sha256 se ne poklapa: ocekivano $RUSTDESK_SHA256, dobiveno $actual"
    log "sha256 provjeren"
  else
    warn "RUSTDESK_SHA256 nije zadan, preskacem provjeru integriteta."
    warn "sha256 preuzetog paketa: $actual"
  fi
}

install_pkg() {
  log "Instaliram RustDesk"
  case "$PKG" in
    deb)
      apt-get update -qq || true
      # apt rjesava ovisnosti .deb-a bolje nego goli dpkg -i
      DEBIAN_FRONTEND=noninteractive apt-get install -y "$PKG_FILE"
      ;;
    rpm)
      if command -v dnf >/dev/null 2>&1; then
        dnf install -y "$PKG_FILE"
      else
        zypper --non-interactive install --allow-unsigned-rpm "$PKG_FILE"
      fi
      ;;
  esac
  command -v rustdesk >/dev/null 2>&1 || die "rustdesk nije u PATH-u nakon instalacije"
}

install_macos() {
  need brew
  log "Instaliram RustDesk preko Homebrewa"
  brew install --cask rustdesk
}

# ------------------------------------------------------------ self-hosted ---
# Zapisuje se u config servisa. Servis na Linuxu radi kao root, pa je to
# /root/.config/rustdesk/RustDesk2.toml.
configure_server() {
  [[ -n "$RUSTDESK_SERVER" ]] || return 0

  local cfg_dir="/root/.config/rustdesk"
  local cfg="$cfg_dir/RustDesk2.toml"
  mkdir -p "$cfg_dir"

  log "Postavljam vlastiti server: $RUSTDESK_SERVER"

  # Uklanjamo eventualne postojece kljuceve da ne dupliramo unose.
  if [[ -f "$cfg" ]]; then
    cp "$cfg" "$cfg.bak.$(date +%s)"
    sed -i -E '/^[[:space:]]*(custom-rendezvous-server|relay-server|api-server|key)[[:space:]]*=/d' "$cfg"
  else
    printf '[options]\n' > "$cfg"
  fi
  grep -q '^\[options\]' "$cfg" || printf '\n[options]\n' >> "$cfg"

  {
    printf "custom-rendezvous-server = '%s'\n" "$RUSTDESK_SERVER"
    printf "relay-server = '%s'\n"             "${RUSTDESK_RELAY:-$RUSTDESK_SERVER}"
    [[ -n "$RUSTDESK_API" ]] && printf "api-server = '%s'\n" "$RUSTDESK_API"
    [[ -n "$RUSTDESK_KEY" ]] && printf "key = '%s'\n"        "$RUSTDESK_KEY"
  } >> "$cfg"

  chmod 600 "$cfg"
}

# ---------------------------------------------------------------- servis ----
start_service() {
  [[ "$PKG" == "macos" ]] && return 0
  command -v systemctl >/dev/null 2>&1 || { warn "nema systemd, preskacem servis"; return 0; }

  log "Ukljucujem rustdesk servis (unattended pristup)"
  systemctl enable --now rustdesk 2>/dev/null || systemctl restart rustdesk || \
    warn "servis se nije pokrenuo preko systemd-a; provjerite: systemctl status rustdesk"
}

wait_for_id() {
  local i id=''
  log "Cekam da servis registrira ID"
  for ((i = 0; i < 30; i++)); do
    id="$(rustdesk --get-id 2>/dev/null | tr -d '[:space:]' || true)"
    [[ -n "$id" && "$id" =~ ^[0-9]+$ ]] && { RD_ID="$id"; return 0; }
    sleep 2
  done
  RD_ID=''
  return 1
}

set_password() {
  log "Postavljam trajnu lozinku"
  rustdesk --password "$RUSTDESK_PASSWORD" >/dev/null 2>&1 \
    || die "postavljanje lozinke nije uspjelo (je li servis pokrenut?)"
  # Servis mora ponovno procitati config.
  if command -v systemctl >/dev/null 2>&1; then
    systemctl restart rustdesk 2>/dev/null || true
  fi
}

# -------------------------------------------------------------- provjere ----
check_display_server() {
  [[ "$PKG" == "macos" ]] && return 0

  local stype="${XDG_SESSION_TYPE:-}"

  # Pod sudo se XDG_SESSION_TYPE gubi, pa tip graficke sesije pitamo logind
  # za korisnika koji je pokrenuo sudo.
  if [[ -z "$stype" ]] && command -v loginctl >/dev/null 2>&1; then
    local sid
    sid="$(loginctl list-sessions --no-legend 2>/dev/null \
           | awk -v u="${SUDO_USER:-}" '(u == "" || $3 == u) { print $1; exit }')" || sid=''
    if [[ -n "$sid" ]]; then
      stype="$(loginctl show-session "$sid" -p Type --value 2>/dev/null)" || stype=''
    fi
  fi

  if [[ "$stype" == "wayland" ]]; then
    warn "Graficka sesija je Wayland. RustDesk na Waylandu ima ogranicenu"
    warn "podrsku za unattended pristup - dijeljenje ekrana i simulacija unosa"
    warn "znaju zakazati kad nitko nije prijavljen."
    warn "Na Pop!_OS-u: odjavite se, pa na ekranu za prijavu kliknite zupcanik"
    warn "i odaberite sesiju 'GNOME on Xorg' prije nego se prijavite."
  elif [[ -n "$stype" ]]; then
    log "Graficka sesija: $stype"
  fi
}

check_sleep() {
  [[ "$PKG" == "macos" ]] && return 0
  warn "Laptop mora biti budan da bi bio dostupan. Provjerite postavke"
  warn "stednje energije (suspend/hibernate na zatvaranje poklopca)."
}

# ------------------------------------------------------------------ main ----
main() {
  need curl
  detect_platform
  require_root

  if [[ -z "$RUSTDESK_PASSWORD" ]]; then
    RUSTDESK_PASSWORD="$(gen_password)"
    GENERATED=1
  else
    GENERATED=0
    [[ ${#RUSTDESK_PASSWORD} -ge 8 ]] || die "lozinka je prekratka (min 8 znakova)"
  fi

  if [[ "$PKG" == "macos" ]]; then
    install_macos
    cat <<'MAC'

RustDesk je instaliran, ali macOS ne dopusta da se ostatak odradi skriptom.
Otvorite RustDesk i rucno:
  1. System Settings -> Privacy & Security -> Screen Recording  -> ukljucite RustDesk
  2. System Settings -> Privacy & Security -> Accessibility     -> ukljucite RustDesk
  3. U RustDesku: Settings -> Security -> Permanent Password -> postavite lozinku
  4. U RustDesku: Settings -> General -> ukljucite "Start on boot"
Nakon toga ID vidite u glavnom prozoru aplikacije.
MAC
    exit 0
  fi

  resolve_asset
  download
  install_pkg
  configure_server
  start_service

  if ! wait_for_id; then
    warn "Servis jos nije prijavio ID. To obicno znaci da ne moze doci do"
    warn "rendezvous servera. Provjerite: systemctl status rustdesk"
    warn "i journalctl -u rustdesk -n 50"
  fi

  set_password
  check_display_server
  check_sleep

  {
    printf '\n'
    printf -- '------------------------------------------------------------------\n'
    printf '  RustDesk je spreman za povezivanje\n'
    printf -- '------------------------------------------------------------------\n'
    printf '  ID:       %s\n' "${RD_ID:-<nije jos dodijeljen, vidi upozorenja gore>}"
    printf '  Lozinka:  %s\n' "$RUSTDESK_PASSWORD"
    printf '  Verzija:  %s\n' "$TAG"
    [[ -n "$RUSTDESK_SERVER" ]] && printf '  Server:   %s\n' "$RUSTDESK_SERVER"
    printf -- '------------------------------------------------------------------\n'
    printf '\n'
  }

  if [[ "$GENERATED" -eq 1 ]]; then
    warn "Lozinka je generirana i NIGDJE nije spremljena osim u RustDesk config."
    warn "Zapisite je sada u password manager - ovaj ispis se ne ponavlja."
  fi
  warn "Ne saljite ID i lozinku zajedno preko istog kanala."
}

main "$@"
