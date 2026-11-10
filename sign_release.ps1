# sign_release.ps1 - Authenticode Code Signing for GameForge Studio
$ErrorActionPreference = "Stop"

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $workspace

Write-Host "==> Checking for GameForge Code Signing Certificate..." -ForegroundColor Cyan

$certName = "GameForge Studio (CharmCompanion)"
$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object { $_.Subject -match "CN=GameForge Studio" } | Select-Object -First 1

if (-not $cert) {
    Write-Host "--> Generating new 5-year Code Signing Certificate..." -ForegroundColor Yellow
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject "CN=$certName, O=CharmCompanion, C=US" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(5) `
        -KeyExportPolicy Exportable `
        -HashAlgorithm SHA256
    Write-Host "--> Certificate created with thumbprint: $($cert.Thumbprint)" -ForegroundColor Green
} else {
    Write-Host "--> Existing certificate found: $($cert.Thumbprint)" -ForegroundColor Green
}

# Export public certificate
$cerPath = Join-Path $workspace "CharmCompanion_GameForge.cer"
Export-Certificate -Cert $cert -FilePath $cerPath -Force | Out-Null
Write-Host "--> Public certificate exported: $cerPath" -ForegroundColor Green

# Locate signtool
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
if (-not (Test-Path $signtool)) {
    $signtool = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Filter "signtool.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}

if (-not (Test-Path $signtool)) {
    Write-Error "signtool.exe not found on system."
}

Write-Host "--> Using signtool: $signtool" -ForegroundColor Cyan

$targets = @(
    (Join-Path $workspace "Release\GameForgeStudio.exe")
)
$installerExes = Get-ChildItem -Path (Join-Path $workspace "Output") -Filter "GameForgeStudio-Setup*.exe" -ErrorAction SilentlyContinue
foreach ($inst in $installerExes) {
    $targets += $inst.FullName
}

foreach ($target in $targets) {
    if (Test-Path $target) {
        Write-Host "--> Signing $target..." -ForegroundColor Yellow
        & $signtool sign /sha1 $($cert.Thumbprint) /fd SHA256 /v $target
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    [OK] Signed: $(Split-Path -Leaf $target)" -ForegroundColor Green
        } else {
            Write-Warning "    Failed to sign $target (Exit Code: $LASTEXITCODE)"
        }
    }
}

# Generate 1-click trust installer
$trustCmd = @"
@echo off
echo ==========================================================
echo  GameForge Studio - CharmCompanion Certificate Installer
echo ==========================================================
echo Installing publisher certificate to Windows Trusted Root and Trusted Publisher stores...
certutil -addstore -f "Root" "%~dp0CharmCompanion_GameForge.cer"
certutil -addstore -f "TrustedPublisher" "%~dp0CharmCompanion_GameForge.cer"
echo.
echo Certificate installation complete. GameForge Studio is now trusted on this PC.
pause
"@

$trustCmdPath = Join-Path $workspace "Trust-Certificate.cmd"
[System.IO.File]::WriteAllText($trustCmdPath, $trustCmd)
Write-Host "--> Generated: $trustCmdPath" -ForegroundColor Green
Write-Host "==> Code signing complete." -ForegroundColor Green
