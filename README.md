# <img src="docs/emoji/1f427.png" width="28" height="28" align="absmiddle"> Installateur Arch Linux — Fritax Edition <img src="docs/emoji/2728.png" width="24" height="24" align="absmiddle">

Installateur "tout-en-un" pour remplacer Windows par Arch Linux sur l'Acer
Aspire 5560 series (model no. MS2319), **sans clé USB**, avec une interface
Windows en français, une pluie Matrix pendant l'installation, un système de
secours, et des raccourcis pratiques.

<p>
  <a href="https://github.com/furaxdev/arch-linux/releases">
    <img alt="Dernière release" src="https://img.shields.io/github/v/release/furaxdev/arch-linux?style=for-the-badge&label=latest%20release&color=1793D1&labelColor=333333">
  </a>
  <a href="https://github.com/furaxdev/arch-linux/actions/workflows/build-exe.yml">
    <img alt="Build .exe" src="https://img.shields.io/github/actions/workflow/status/furaxdev/arch-linux/build-exe.yml?branch=amd64-x86&style=for-the-badge&label=build%20.exe&labelColor=333333">
  </a>
  <a href="https://fritax-arch-setup.vercel.app">
    <img alt="Site vitrine" src="https://img.shields.io/badge/site-vitrine-1793D1?style=for-the-badge&logo=vercel&labelColor=333333">
  </a>
  <a href="https://github.com/furaxdev/arch-linux">
    <img alt="Star ce dépôt" src="https://img.shields.io/github/stars/furaxdev/arch-linux?style=for-the-badge&logo=github&label=star%20this%20repo&color=2ea44f&labelColor=333333">
  </a>
</p>

## <img src="docs/emoji/1f440.png" width="22" height="22" align="absmiddle"> Aperçu

<p>
  <img src="docs/apercu-accueil.svg" width="49%" alt="Écran d'accueil de Fritax Arch Setup">
  <img src="docs/apercu-installation.svg" width="49%" alt="Écran d'installation avec pluie Matrix">
</p>

## <img src="docs/emoji/26a0.png" width="22" height="22" align="absmiddle"> Avertissements importants

- Cette installation **efface complètement** le disque choisi, y compris
  Windows. **Sauvegarde tes fichiers avant !**
- Arch Linux ne fournit plus d'ISO 32 bits (x86) depuis 2017 : seule l'ISO
  x86_64 (64 bits) existe. Les deux branches ci-dessous ne changent donc que
  le paquet de microcode installé (`amd-ucode` ou `intel-ucode`), pas
  l'architecture.
- Il faut lancer `windows_installer/ArchInstallerFritax.py` **en tant
  qu'administrateur** pour que l'étape "démarrage sans clé USB" fonctionne
  (modification de la partition système / `bcdedit`).

## <img src="docs/emoji/1f33f.png" width="22" height="22" align="absmiddle"> Branches

| Branche | Pour quel processeur ? | Microcode installé |
|---|---|---|
| `amd64-x86` (celle-ci) | AMD | `amd-ucode` |
| `intel64-x86` | Intel | `intel-ucode` |

## <img src="docs/emoji/1f680.png" width="22" height="22" align="absmiddle"> Utilisation

### 0. <img src="docs/emoji/1f4e6.png" width="18" height="18" align="absmiddle"> Obtenir le fichier .exe (deux options)

**Option A — GitHub Actions (automatique) :** chaque push déclenche le
workflow `.github/workflows/build-exe.yml`, qui compile l'application sur un
runner Windows. Va dans l'onglet **Actions** du dépôt → dernier run
**"<img src="docs/emoji/1f427.png" width="16" height="16" align="absmiddle"> Build ArchInstallerFritax.exe"** → télécharge l'artifact
`ArchInstallerFritax-<branche>.exe`.

**Option B — Compiler toi-même sur Windows :**

```powershell
cd windows_installer
build_exe.bat
```

Le fichier `dist\ArchInstallerFritax.exe` est généré (demande automatiquement
les droits administrateur au démarrage, grâce à `--uac-admin`).

> ⚠️ **Windows Defender peut signaler l'exe** (ex: `Trojan:Win32/Sabsik.EN.D!ml`).
> C'est un **faux positif très courant** sur les exécutables PyInstaller non
> signés (détection heuristique par IA, pas une signature de virus connu —
> le `!ml` dans le nom l'indique). Le code source est entièrement visible
> dans ce dépôt. Pour continuer :
> 1. Clique sur "Plus d'infos" → "Exécuter quand même" dans l'alerte SmartScreen, ou
> 2. Restaure le fichier en PowerShell admin :
>    `Add-MpPreference -ExclusionPath "chemin\vers\ArchInstallerFritax.exe"`
>    puis `"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -Restore -All`
> 3. (Optionnel) Signale le faux positif à Microsoft :
>    https://www.microsoft.com/en-us/wdsi/filesubmission

### 1. Sur Windows (préparation, sans clé USB)

Directement avec l'exécutable :

```powershell
ArchInstallerFritax.exe
```

Ou en lançant le script Python :

```powershell
cd windows_installer
python ArchInstallerFritax.py
```

L'application va :
1. <img src="docs/emoji/1f4e1.png" width="16" height="16" align="absmiddle"> Télécharger l'ISO officielle Arch Linux
2. <img src="docs/emoji/1f3a8.png" width="16" height="16" align="absmiddle"> La personnaliser (nom de PC `PC-de-Fritax`, utilisateur `fritaxdev`)
3. <img src="docs/emoji/1f97e.png" width="16" height="16" align="absmiddle"> Préparer une entrée de démarrage `Fritax - Installer Arch Linux`
   directement depuis le disque dur (technique GRUB "loopback", pas besoin
   de clé USB)
4. <img src="docs/emoji/1f327.png" width="16" height="16" align="absmiddle"> Afficher une pluie Matrix + barre de progression pendant les étapes
   longues, avec le message *"Nous installons votre système... (et dis
   merci à eden :3)"*

Outils requis sur Windows : **7-Zip** et **Windows ADK (oscdimg.exe)** — voir
`windows_installer/requirements.txt`.

### 2. Redémarrage → environnement Arch Linux live

Choisis l'entrée **"Fritax - Installer Arch Linux 🐧"** au démarrage, puis
lance :

```bash
bash /arch/scripts/fritax-setup.sh   # préconfigure hostname + utilisateur
bash scripts/install_arch.sh         # installation complète (partitionnement,
                                      # base, GRUB, système de secours)
```

Une confirmation explicite (`OUI EFFACER`) est demandée avant tout
effacement de disque.

### 3. <img src="docs/emoji/1f691.png" width="18" height="18" align="absmiddle"> Système de secours

Une partition dédiée (`Fritax-Secours`, 4 Gio par défaut) contenant un mini
Arch de réparation est automatiquement créée, avec sa propre entrée dans le
menu GRUB (`fritax-secours`). Si l'installation principale casse, choisis
cette entrée pour réparer (chroot, réinstaller GRUB, etc.).

### 4. <img src="docs/emoji/1f527.png" width="18" height="18" align="absmiddle"> Raccourcis une fois Arch installé

Un script `raccourcis-fritax.sh` est déposé dans le dossier personnel de
`fritaxdev` : un petit menu en français pour les commandes courantes
(mise à jour, installation de logiciels, infos système, etc.) :

```bash
bash ~/raccourcis-fritax.sh
```

## <img src="docs/emoji/1f4c1.png" width="22" height="22" align="absmiddle"> Structure du projet

```
windows_installer/       Application Windows (Tkinter)
  ArchInstallerFritax.py   Fenêtre principale
  matrix_rain.py           Effet pluie Matrix + barre de progression
  iso_downloader.py        Téléchargement + vérification de l'ISO
  iso_customizer.py        Personnalisation légère de l'ISO
  nousb_boot.py            Démarrage sans clé USB (GRUB loopback + UEFI)
  rescue_installer.py      Résumé du système de secours
  config.py                Config (hostname, utilisateur, raccourcis...)

scripts/                  Scripts exécutés dans l'environnement Arch live
  install_arch.sh            Installation complète automatisée
  setup_rescue.sh             Création du système de secours
  post_install_shortcuts.sh   Menu de raccourcis en français
```

Merci à eden :3
