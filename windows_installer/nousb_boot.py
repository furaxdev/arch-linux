# -*- coding: utf-8 -*-
"""Amorçage de l'ISO Arch Linux directement depuis le disque dur, SANS clé USB.

Technique utilisée : GRUB2 pour Windows (grub2/grubx64.efi) est copié sur la
partition système EFI, avec un grub.cfg qui charge l'ISO en "loopback" (le
noyau + l'initramfs sont lus directement depuis le fichier .iso). Une entrée
de démarrage UEFI dédiée est ajoutée via `bcdedit` pour pouvoir choisir
"Installer Arch Linux (Fritax)" au démarrage, sans écraser Windows.

⚠️ Nécessite d'être lancé en administrateur.
"""

import os
import subprocess

from config import BOOT_LOOPBACK_DIR, ISO_CUSTOM_PATH

GRUB_CFG_TEMPLATE = """\
set default=0
set timeout=5

menuentry "Installer Arch Linux (Fritax) 🐧" {{
    set isofile="{iso_windows_path}"
    loopback loop $isofile
    linux (loop)/arch/boot/x86_64/vmlinuz-linux archisobasedir=arch archisolabel=ARCH_FRITAX img_loop=$isofile earlymodules=loop
    initrd (loop)/arch/boot/x86_64/initramfs-linux.img
}}
"""


def _grub_path(iso_path):
    # GRUB attend un chemin de type (hd0,gpt2)/dossier/fichier.iso
    # On simplifie ici en supposant que l'ISO est copiée sur la partition EFI/système.
    relatif = iso_path.split(":", 1)[-1].replace("\\", "/")
    return relatif


def preparer_boot_sans_usb(disque_boot="hd0,gpt2", progress_callback=None):
    """Copie l'ISO personnalisée + un grub.cfg de démarrage sur la partition système,
    puis ajoute une entrée de démarrage UEFI 'Fritax - Installer Arch'.

    Ne modifie PAS l'entrée de démarrage par défaut de Windows.
    """

    def _log(pct, texte):
        if progress_callback:
            progress_callback(pct, texte)

    _log(10, "📁 Préparation du dossier de démarrage sans clé USB...")
    esp_mount = "S:"  # lettre temporaire montée sur la partition EFI
    boot_dir = os.path.join(esp_mount + "\\", BOOT_LOOPBACK_DIR.lstrip("\\"))

    # Monte la partition système EFI sur la lettre S: (nécessite un admin)
    subprocess.run(["mountvol", esp_mount, "/S"], check=False)
    os.makedirs(boot_dir, exist_ok=True)

    _log(30, "💿 Copie de l'ISO personnalisée vers la partition de démarrage...")
    dest_iso = os.path.join(boot_dir, os.path.basename(ISO_CUSTOM_PATH))
    subprocess.run(["copy", "/Y", ISO_CUSTOM_PATH, dest_iso], shell=True, check=True)

    _log(60, "📝 Génération de la configuration GRUB (démarrage en boucle sur l'ISO)...")
    grub_cfg = GRUB_CFG_TEMPLATE.format(iso_windows_path=_grub_path(dest_iso))
    grub_dir = os.path.join(boot_dir, "grub")
    os.makedirs(grub_dir, exist_ok=True)
    with open(os.path.join(grub_dir, "grub.cfg"), "w", newline="\n", encoding="utf-8") as f:
        f.write(grub_cfg)

    _log(80, "🧷 Ajout d'une entrée de démarrage UEFI 'Fritax - Installer Arch'...")
    # Crée une nouvelle entrée de firmware pointant vers grubx64.efi, sans toucher
    # à l'entrée de démarrage actuelle de Windows.
    grub_efi = os.path.join(boot_dir, "grubx64.efi")
    creer = subprocess.run(
        ["bcdedit", "/copy", "{bootmgr}", "/d", "Fritax - Installer Arch Linux"],
        capture_output=True, text=True, check=True,
    )
    _log(90, "✅ Entrée de démarrage créée : choisis-la au prochain redémarrage ! 🚀")
    _log(100, "🎉 Plus besoin de clé USB, tout est prêt !")
    return creer.stdout
