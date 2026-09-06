@echo off
REM =============================================================================
REM  Construit ArchInstallerFritax.exe a partir des sources Python.
REM  A executer sur Windows, dans le dossier windows_installer.
REM
REM  Prerequis : Python 3.9+ installe et disponible dans le PATH.
REM =============================================================================

echo Installation de PyInstaller...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Construction de l'executable...
python -m PyInstaller --noconfirm --onefile --windowed --uac-admin --noupx ^
    --version-file version_info.txt ^
    --name ArchInstallerFritax ^
    ArchInstallerFritax.py

echo.
echo Signature de l'executable (certificat auto-signe "FuraxDev")...
powershell -ExecutionPolicy Bypass -File sign_exe.ps1 -ExePath dist\ArchInstallerFritax.exe -Publisher FuraxDev

echo.
echo Termine ! L'executable se trouve dans dist\ArchInstallerFritax.exe
echo Clic droit dessus -^> "Executer en tant qu'administrateur" pour le lancer.
pause
