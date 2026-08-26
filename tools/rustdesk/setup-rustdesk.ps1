<#
.SYNOPSIS
    Instalira RustDesk na Windows i priprema ga za unattended pristup.

.DESCRIPTION
    Pokrenuti iz PowerShella s administratorskim ovlastima:

        powershell -ExecutionPolicy Bypass -File .\setup-rustdesk.ps1

    Na kraju ispisuje RustDesk ID i trajnu lozinku.

.PARAMETER Password
    Trajna lozinka. Ako se izostavi, generira se nasumicna.

.PARAMETER Version
    Tag verzije (npr. 1.4.2). Ako se izostavi, uzima se najnovije izdanje.

.PARAMETER Sha256
    Ocekivani SHA256 preuzetog instalacijskog paketa. Preporuceno.

.PARAMETER Server
    Host vlastitog (self-hosted) rendezvous servera.

.PARAMETER Key
    Javni kljuc vlastitog servera.
#>
[CmdletBinding()]
param(
    [string]$Password,
    [string]$Version,
    [string]$Sha256,
    [string]$Server,
    [string]$Key
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Step { param($m) Write-Host "==> $m" -ForegroundColor Cyan }
function Write-Warn { param($m) Write-Host " /!\ $m" -ForegroundColor Yellow }
function Die       { param($m) Write-Host "!!! $m" -ForegroundColor Red; exit 1 }

function Assert-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $pr = New-Object Security.Principal.WindowsPrincipal($id)
    if (-not $pr.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Die "Pokrenite PowerShell kao administrator."
    }
}

function New-StrongPassword {
    # 20 znakova iz 58-znakovne abecede bez ambigviteta (~117 bita entropije).
    $alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'
    $bytes = [byte[]]::new(20)
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        # Odbacivanje pristranih vrijednosti: 256 nije djeljiv s 58, pa bi
        # obicni modulo blago favorizirao pocetak abecede.
        $limit = [int](256 - (256 % $alphabet.Length))
        $out = New-Object System.Text.StringBuilder
        while ($out.Length -lt 20) {
            $rng.GetBytes($bytes)
            foreach ($b in $bytes) {
                if ($out.Length -ge 20) { break }
                if ($b -lt $limit) {
                    [void]$out.Append($alphabet[$b % $alphabet.Length])
                }
            }
        }
        return $out.ToString()
    } finally { $rng.Dispose() }
}

function Get-ReleaseAsset {
    $uri = if ($Version) {
        "https://api.github.com/repos/rustdesk/rustdesk/releases/tags/$Version"
    } else {
        "https://api.github.com/repos/rustdesk/rustdesk/releases/latest"
    }

    Write-Step "Trazim izdanje: $uri"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    try {
        $rel = Invoke-RestMethod -Uri $uri -Headers @{
            'Accept'     = 'application/vnd.github+json'
            'User-Agent' = 'rustdesk-setup-script'
        }
    } catch {
        Die "Ne mogu dohvatiti podatke o izdanju s GitHuba: $($_.Exception.Message)"
    }

    $arch = if ([Environment]::Is64BitOperatingSystem) { 'x86_64' } else { 'i686' }

    # Ime asseta se kroz verzije mijenjalo, pa biramo uzorkom umjesto
    # hardkodiranog imena. .exe je fallback ako .msi ne postoji u izdanju.
    $asset = $rel.assets | Where-Object { $_.name -match "$arch.*\.msi$" } | Select-Object -First 1
    if (-not $asset) {
        $asset = $rel.assets | Where-Object { $_.name -match "$arch.*\.exe$" } | Select-Object -First 1
    }
    if (-not $asset) { Die "U izdanju $($rel.tag_name) nema .msi ni .exe za $arch." }

    Write-Step "Izdanje $($rel.tag_name) -> $($asset.name)"
    return [pscustomobject]@{
        Tag  = $rel.tag_name
        Name = $asset.name
        Url  = $asset.browser_download_url
    }
}

function Get-Installer {
    param($Asset)
    $dest = Join-Path $env:TEMP $Asset.Name
    Write-Step "Preuzimam paket"
    $progressPreferenceOld = $ProgressPreference
    $ProgressPreference = 'SilentlyContinue'   # bez ovoga je Invoke-WebRequest jako spor
    try {
        Invoke-WebRequest -Uri $Asset.Url -OutFile $dest -UseBasicParsing
    } catch {
        Die "Preuzimanje nije uspjelo: $($_.Exception.Message)"
    } finally { $ProgressPreference = $progressPreferenceOld }

    if (-not (Test-Path $dest) -or (Get-Item $dest).Length -eq 0) {
        Die "Preuzeta datoteka je prazna."
    }

    $actual = (Get-FileHash -Path $dest -Algorithm SHA256).Hash.ToLower()
    if ($Sha256) {
        if ($actual -ne $Sha256.ToLower()) {
            Die "SHA256 se ne poklapa: ocekivano $($Sha256.ToLower()), dobiveno $actual"
        }
        Write-Step "SHA256 provjeren"
    } else {
        Write-Warn "Parametar -Sha256 nije zadan, preskacem provjeru integriteta."
        Write-Warn "SHA256 preuzetog paketa: $actual"
    }
    return $dest
}

function Install-RustDesk {
    param([string]$Installer)
    Write-Step "Instaliram RustDesk (tiha instalacija)"
    if ($Installer -like '*.msi') {
        $p = Start-Process msiexec.exe -ArgumentList @('/i', "`"$Installer`"", '/qn', '/norestart') -Wait -PassThru
    } else {
        $p = Start-Process $Installer -ArgumentList '--silent-install' -Wait -PassThru
    }
    if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) {
        Die "Instalacija je zavrsila s kodom $($p.ExitCode)."
    }
}

function Find-RustDeskExe {
    $candidates = @(
        (Join-Path $env:ProgramFiles        'RustDesk\rustdesk.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'RustDesk\rustdesk.exe')
    ) | Where-Object { $_ -and (Test-Path $_) }

    if (-not $candidates) { Die "Ne nalazim rustdesk.exe nakon instalacije." }
    return $candidates[0]
}

function Set-CustomServer {
    param([string]$Exe)
    if (-not $Server) { return }
    Write-Step "Postavljam vlastiti server: $Server"
    # Servis cita config iz ProfilaService accounta; --config primjenjuje globalno.
    $cfg = "rustdesk://config/host=$Server"
    if ($Key) { $cfg += ",key=$Key" }
    & $Exe --config $cfg | Out-Null
}

function Install-RustDeskService {
    param([string]$Exe)
    Write-Step "Ukljucujem RustDesk servis (unattended pristup)"
    & $Exe --install-service | Out-Null
    Start-Sleep -Seconds 5
    $svc = Get-Service -Name 'RustDesk' -ErrorAction SilentlyContinue
    if ($svc) {
        Set-Service -Name 'RustDesk' -StartupType Automatic
        if ($svc.Status -ne 'Running') { Start-Service -Name 'RustDesk' }
    } else {
        Write-Warn "Servis 'RustDesk' nije pronaden; unattended pristup mozda nece raditi."
    }
}

function Wait-ForId {
    param([string]$Exe)
    Write-Step "Cekam da servis registrira ID"
    for ($i = 0; $i -lt 30; $i++) {
        $id = (& $Exe --get-id 2>$null | Out-String).Trim()
        if ($id -match '^\d+$') { return $id }
        Start-Sleep -Seconds 2
    }
    return $null
}

# ------------------------------------------------------------------ main ----
Assert-Admin

$generated = $false
if (-not $Password) {
    $Password = New-StrongPassword
    $generated = $true
} elseif ($Password.Length -lt 8) {
    Die "Lozinka je prekratka (min 8 znakova)."
}

$asset     = Get-ReleaseAsset
$installer = Get-Installer -Asset $asset
Install-RustDesk -Installer $installer
$exe = Find-RustDeskExe
Set-CustomServer -Exe $exe
Install-RustDeskService -Exe $exe

$id = Wait-ForId -Exe $exe
if (-not $id) {
    Write-Warn "Servis jos nije prijavio ID - obicno znaci da ne moze doci do"
    Write-Warn "rendezvous servera. Provjerite vatrozid i mreznu vezu."
}

Write-Step "Postavljam trajnu lozinku"
& $exe --password $Password | Out-Null
Restart-Service -Name 'RustDesk' -ErrorAction SilentlyContinue

Remove-Item $installer -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "------------------------------------------------------------------"
Write-Host "  RustDesk je spreman za povezivanje"
Write-Host "------------------------------------------------------------------"
Write-Host "  ID:       $(if ($id) { $id } else { '<nije jos dodijeljen, vidi upozorenja gore>' })"
Write-Host "  Lozinka:  $Password"
Write-Host "  Verzija:  $($asset.Tag)"
if ($Server) { Write-Host "  Server:   $Server" }
Write-Host "------------------------------------------------------------------"
Write-Host ""

if ($generated) {
    Write-Warn "Lozinka je generirana i nigdje nije spremljena osim u RustDesk config."
    Write-Warn "Zapisite je sada u password manager - ovaj ispis se ne ponavlja."
}
Write-Warn "Laptop mora biti budan da bi bio dostupan (provjerite Sleep postavke)."
Write-Warn "Ne saljite ID i lozinku zajedno preko istog kanala."
