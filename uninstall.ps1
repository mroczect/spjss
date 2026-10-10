#Requires -Version 5.1

$ErrorActionPreference = 'SilentlyContinue'

$ScriptUrl = 'https://raw.githubusercontent.com/mroczect/spjss/master/uninstall.ps1'

# ── self-elevate ────────────────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host 'requesting administrator privileges...'
    Start-Process powershell -Verb RunAs -ArgumentList @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-Command', "irm $ScriptUrl | iex"
    )
    exit
}

Write-Host ''
Write-Host '==== spjss uninstall ===='
Write-Host ''

# ── paths ───────────────────────────────────────────────────────────
$paths = @(
    "$env:LOCALAPPDATA\Programs\spjss",
    "$env:APPDATA\spjss",
    "$env:LOCALAPPDATA\spjss",
    "$env:ProgramData\spjss",
    "${env:ProgramFiles}\spjss",
    "${env:ProgramFiles(x86)}\spjss"
)

$shortcuts = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\spjss",
    "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\spjss",
    "$env:USERPROFILE\Desktop\spjss.lnk",
    "$env:PUBLIC\Desktop\spjss.lnk"
)

$regKeys = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}_is1',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}_is1',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{8F2C3A4D-1B5E-4F6A-9D8C-7E0A1B2C3D4E}_is1',
    'HKCU:\Software\spjss',
    'HKLM:\Software\spjss'
)

# ── 1. stop processes ───────────────────────────────────────────────
Write-Host '[1/6] stopping processes'
foreach ($name in 'spjss', 'spjss-setup', 'unins000') {
    Get-Process -Name $name -ErrorAction SilentlyContinue | Stop-Process -Force
}
Start-Sleep -Milliseconds 800

# ── 2. run official uninstaller ─────────────────────────────────────
Write-Host '[2/6] running official uninstaller'
$uninst = "$env:LOCALAPPDATA\Programs\spjss\unins000.exe"
if (Test-Path $uninst) {
    Start-Process $uninst -ArgumentList `
        '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' -Wait
} else {
    Write-Host '      not found, skipping'
}

# ── 3. remove folders ───────────────────────────────────────────────
Write-Host '[3/6] removing folders'
foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host "      $p"
        Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
        if (Test-Path $p) {
            # fallback for protected files
            takeown /f $p /r /d y *>$null
            icacls $p /grant "*S-1-5-32-544:F" /t /c *>$null
            Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# ── 4. remove shortcuts ─────────────────────────────────────────────
Write-Host '[4/6] removing shortcuts'
foreach ($s in $shortcuts) {
    if (Test-Path $s) { Remove-Item -LiteralPath $s -Recurse -Force }
}

# ── 5. remove registry + credentials ────────────────────────────────
Write-Host '[5/6] removing registry and credentials'
foreach ($k in $regKeys) {
    if (Test-Path $k) { Remove-Item -LiteralPath $k -Recurse -Force }
}

# run-key autostart entries
foreach ($hive in 'HKCU', 'HKLM') {
    $runKey = "${hive}:\Software\Microsoft\Windows\CurrentVersion\Run"
    if (Test-Path $runKey) {
        Remove-ItemProperty -Path $runKey -Name 'spjss' -Force
    }
}

# stored credentials — any target containing "spjss"
$creds = cmdkey /list 2>$null | Select-String 'Target:\s*(.+spjss.+)$'
foreach ($c in $creds) {
    $target = $c.Matches[0].Groups[1].Value.Trim()
    cmdkey /delete:$target *>$null
}

# ── 6. temp files ───────────────────────────────────────────────────
Write-Host '[6/6] removing temp files'
Get-ChildItem "$env:TEMP\spjss-setup-*.exe" -ErrorAction SilentlyContinue |
    Remove-Item -Force
Get-ChildItem "$env:TEMP\_MEI*" -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-Path "$($_.FullName)\spjss.exe" } |
    Remove-Item -Recurse -Force

# refresh shell icon cache
ie4uinit.exe -show *>$null

# ── verify ──────────────────────────────────────────────────────────
Write-Host ''
Write-Host '==== verification ===='

$left = 0
foreach ($p in $paths) {
    if (Test-Path $p) { Write-Host "  left: $p"; $left++ }
}
foreach ($k in $regKeys) {
    if (Test-Path $k) { Write-Host "  left: $k"; $left++ }
}
if (Get-Process spjss -ErrorAction SilentlyContinue) {
    Write-Host '  left: spjss.exe running'; $left++
}
if (cmdkey /list 2>$null | Select-String 'spjss') {
    Write-Host '  left: credential entry'; $left++
}

Write-Host ''
if ($left -eq 0) {
    Write-Host 'clean.'
} else {
    Write-Host "$left item(s) remain. Close Explorer or reboot and re-run."
}
Write-Host ''
Read-Host 'press enter to exit'
