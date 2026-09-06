# -*- coding: utf-8 -*-
"""Personnalisation légère de l'ISO Arch Linux (hostname + utilisateur par défaut).

Nécessite sur Windows :
  - 7-Zip (7z.exe) pour extraire/reconstruire l'ISO
  - oscdimg.exe (fourni par le "Windows ADK - Deployment Tools") pour regénérer une
    ISO bootable UEFI/BIOS hybride après modification

On ne modifie pas le noyau ni les paquets : on ajoute juste un script d'amorçage
('fritax-setup.sh') dans le profil archiso, exécuté automatiquement par
`archinstall`/le script d'installation pour préconfigurer le nom de machine et
l'utilisateur, sans toucher au reste de l'ISO officielle.
"""

import glob
import os
import shutil
import subprocess

from config import (
    HOSTNAME,
    ISO_CUSTOM_PATH,
    ISO_DOWNLOAD_PATH,
    ISO_EXTRACT_DIR,
    UCODE_PACKAGE,
    USERNAME,
    WORKDIR,
)

SEVEN_ZIP_CANDIDATES = [
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
]
OSCDIMG_CANDIDATES = [
    r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe",
]


def _trouver_outil(candidats, nom):
    for chemin in candidats:
        if os.path.isfile(chemin):
            return chemin
    trouve = shutil.which(nom)
    if trouve:
        return trouve
    raise FileNotFoundError(
        f"❌ Impossible de trouver {nom}. Installe-le puis relance l'assistant. 🙏"
    )


FRITAX_SETUP_SH = f"""#!/usr/bin/env bash
# Généré automatiquement par l'installateur Fritax — préconfigure le nom de
# machine et l'utilisateur par défaut avant de lancer archinstall.
set -e
echo "{HOSTNAME}" > /etc/hostname
useradd -m -G wheel -s /bin/bash "{USERNAME}" || true
echo "✨ Bienvenue {USERNAME} ! Ton PC va s'appeler {HOSTNAME} 😄"
echo "N'oublie pas d'installer le microcode : {UCODE_PACKAGE} 🧠"
"""


def _trouver_image_efi(extract_dir):
    """Localise l'image de démarrage EFI, en gérant les deux structures d'ISO Arch.

    Les ISO Arch récentes (2024+) sont passées à systemd-boot et ne contiennent
    plus 'EFI/archiso/efiboot.img' : 7-Zip extrait alors les images El Torito
    à part dans un dossier '[BOOT]' (ex: '2-Boot-NoEmul.img', la plus grosse
    étant l'image EFI). On la copie hors de l'arborescence pour ne pas
    l'inclure telle quelle (dossier '[BOOT]') dans l'ISO reconstruite.
    """
    chemin_classique = os.path.join(extract_dir, "EFI", "archiso", "efiboot.img")
    if os.path.isfile(chemin_classique):
        return chemin_classique

    dossier_boot = os.path.join(extract_dir, "[BOOT]")
    candidats = glob.glob(os.path.join(dossier_boot, "*-Boot-NoEmul.img"))
    if not candidats:
        raise FileNotFoundError(
            "❌ Impossible de trouver l'image de démarrage EFI dans l'ISO extraite."
        )
    plus_grosse = max(candidats, key=os.path.getsize)

    efi_img_tmp = os.path.join(WORKDIR, "efiboot_extrait.img")
    shutil.copy2(plus_grosse, efi_img_tmp)
    shutil.rmtree(dossier_boot, ignore_errors=True)
    return efi_img_tmp


def personnaliser_iso(progress_callback=None):
    def _log(pct, texte):
        if progress_callback:
            progress_callback(pct, texte)

    seven_zip = _trouver_outil(SEVEN_ZIP_CANDIDATES, "7z.exe")
    oscdimg = _trouver_outil(OSCDIMG_CANDIDATES, "oscdimg.exe")

    _log(5, "🗜️ Extraction de l'ISO officielle...")
    if os.path.isdir(ISO_EXTRACT_DIR):
        shutil.rmtree(ISO_EXTRACT_DIR)
    os.makedirs(ISO_EXTRACT_DIR, exist_ok=True)
    subprocess.run([seven_zip, "x", ISO_DOWNLOAD_PATH, f"-o{ISO_EXTRACT_DIR}", "-y"], check=True)

    _log(40, "✏️ Ajout du script de personnalisation (nom du PC, utilisateur)...")
    scripts_dir = os.path.join(ISO_EXTRACT_DIR, "arch", "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    with open(os.path.join(scripts_dir, "fritax-setup.sh"), "w", newline="\n", encoding="utf-8") as f:
        f.write(FRITAX_SETUP_SH)

    _log(70, "💿 Reconstruction d'une ISO bootable (BIOS + UEFI)...")
    boot_bin = os.path.join(ISO_EXTRACT_DIR, "boot", "syslinux", "isolinux.bin")
    efi_img = _trouver_image_efi(ISO_EXTRACT_DIR)
    cmd = [
        oscdimg, "-m", "-u2", "-udfver102",
        f"-bootdata:2#p0,e,b{boot_bin}#pEF,e,b{efi_img}",
        ISO_EXTRACT_DIR, ISO_CUSTOM_PATH,
    ]
    subprocess.run(cmd, check=True)

    _log(100, "✅ ISO personnalisée prête ! 🎉")
    return ISO_CUSTOM_PATH
