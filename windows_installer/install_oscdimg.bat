@echo off
REM =============================================================================
REM  Installe oscdimg.exe via le vrai installeur officiel Microsoft (Windows ADK)
REM  -- pas de binaire isole telecharge depuis un depot GitHub tiers, on evite
REM  les copies non verifiees/renommees qui circulent (probleme de confiance
REM  de la chaine d'approvisionnement).
REM
REM  Installe silencieusement UNIQUEMENT le composant "Deployment Tools"
REM  (qui contient oscdimg.exe), pas tout l'ADK.
REM =============================================================================

set ADK_URL=https://download.microsoft.com/download/1/f/d/1fd2291e-c0e9-4ae0-beae-fbbe0fe41a5a/adk/adksetup.exe
set ADK_SETUP=%TEMP%\adksetup.exe

echo Telechargement de l'installeur officiel Windows ADK...
powershell -Command "Invoke-WebRequest -Uri '%ADK_URL%' -OutFile '%ADK_SETUP%'"

if not exist "%ADK_SETUP%" (
    echo ERREUR: le telechargement a echoue.
    pause
    exit /b 1
)

echo.
echo Installation silencieuse du composant "Deployment Tools" (oscdimg.exe)...
"%ADK_SETUP%" /quiet /features OptionId.DeploymentTools /norestart

echo.
echo Termine ! oscdimg.exe se trouve normalement dans :
echo   C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe
del "%ADK_SETUP%"
pause
