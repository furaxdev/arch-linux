# =============================================================================
#  Signe ArchInstallerFritax.exe avec un certificat auto-signé "FuraxDev".
#
#  ⚠️ Un certificat auto-signé n'est reconnu par AUCUNE autorité de confiance.
#  Windows affichera toujours "Éditeur inconnu" et cela ne supprime PAS les
#  alertes SmartScreen/Defender. Ça sert uniquement à identifier visuellement
#  le publisher dans les propriétés du fichier (onglet "Signatures numériques").
#
#  Usage : powershell -ExecutionPolicy Bypass -File sign_exe.ps1 -ExePath dist\ArchInstallerFritax.exe
# =============================================================================
param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,
    [string]$Publisher = "FuraxDev"
)

$ErrorActionPreference = "Stop"

Write-Host "Génération du certificat auto-signé pour '$Publisher'..."
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=$Publisher" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeyUsage DigitalSignature `
    -FriendlyName "$Publisher - Fritax Arch Setup" `
    -NotAfter (Get-Date).AddYears(3)

$pfxPath = Join-Path $env:TEMP "fritax-signing.pfx"
$pfxPassword = ConvertTo-SecureString -String ([guid]::NewGuid().ToString()) -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pfxPassword | Out-Null

$signtool = Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match "x64" } | Select-Object -First 1 -ExpandProperty FullName

if (-not $signtool) {
    throw "signtool.exe introuvable. Installe le Windows SDK (Signing Tools) ou utilise le Windows ADK."
}

Write-Host "Signature de $ExePath avec $signtool ..."
& $signtool sign /f $pfxPath /p ([Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pfxPassword))) `
    /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $ExePath

Remove-Item $pfxPath -Force
Remove-Item "Cert:\CurrentUser\My\$($cert.Thumbprint)" -Force

Write-Host "✅ $ExePath signé (certificat auto-signé, non approuvé par Windows)."
