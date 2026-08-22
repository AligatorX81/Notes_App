# Podešavanje lokalnog Claude Code CLI-ja

Sve niže se izvodi **na laptopu**, u terminalu. Traje oko minutu.

## 1. Postavi memoriju projekta

Napravi folder projekta i stavi `CLAUDE.md` u njega:

```bash
mkdir -p ~/projects/cycloidal && cd ~/projects/cycloidal
# kopiraj CLAUDE.md i cycloidal_drive.py u ovaj folder
claude
```

Claude Code automatski čita `CLAUDE.md` iz foldera u kojem je pokrenut. Od tada
zna parametre, pravila i obaveznu provjeru — ne moraš ništa objašnjavati.

Za pravila koja vrijede u SVIM projektima, isti sadržaj ide u `~/.claude/CLAUDE.md`.

## 2. Direktna kontrola Blendera (blender-mcp)

Dva dijela, oba na laptopu:

**a) MCP server** — registriraj ga u Claude Code:
```bash
claude mcp add blender -- uvx blender-mcp
claude mcp list          # provjera da se pojavio
```

**b) Addon u Blenderu:** preuzmi `addon.py` iz repozitorija projekta blender-mcp,
pa u Blenderu: `Edit → Preferences → Add-ons → Install…`, izaberi `addon.py`,
uključi kvačicu. Zatim u 3D pogledu `N` → kartica **BlenderMCP** → *Connect*.

> Provjeri točan naziv paketa i korake u aktualnom README-u projekta blender-mcp —
> pišem ih po sjećanju i mogli su se promijeniti.

Kad oboje radi, u `claude` sesiji možeš tražiti izmjene scene i vidiš ih uživo.

## 3. Provjera da je sve na mjestu

```bash
claude --version
which blender
claude mcp list
```

## 4. Test

```bash
blender -P ~/projects/cycloidal/cycloidal_drive.py
```
Blender se otvori s izgrađenim sklopom i izveze STL-ove u `~/cyclo_out`.

## Zašto web-sesija ovo ne može

Claude Code na webu (claude.ai/code) izvršava se u kontejneru u oblaku — druga
mašina, bez rute do tvog diska. CLI u terminalu izvršava se na tvom laptopu i
ima pun pristup. Isti asistent, različito mjesto izvršavanja. Za sve što dira
tvoje fajlove i programe, koristi CLI.
