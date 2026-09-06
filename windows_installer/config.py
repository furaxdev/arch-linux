# -*- coding: utf-8 -*-
"""Configuration de l'installateur Arch Linux pour Fritax."""

# --- Identité de la machine ---
HOSTNAME = "PC-de-Fritax"
USERNAME = "fritaxdev"

# --- Variante CPU de cette branche ---
# "amd"   -> branche amd64-x86   (paquet amd-ucode)
# "intel" -> branche intel64-x86 (paquet intel-ucode)
CPU_VENDOR = "intel"
UCODE_PACKAGE = "amd-ucode" if CPU_VENDOR == "amd" else "intel-ucode"

# --- Téléchargement de l'ISO ---
# NB: Arch Linux ne fournit plus d'ISO 32 bits (x86) depuis 2017,
# uniquement du x86_64. On télécharge donc toujours la même ISO 64 bits,
# la distinction AMD/Intel ne joue que sur le microcode installé.
ARCH_MIRROR_ISO_URL = "https://geo.mirror.pkgbuild.com/iso/latest/archlinux-x86_64.iso"
ARCH_MIRROR_CHECKSUM_URL = "https://geo.mirror.pkgbuild.com/iso/latest/sha256sums.txt"

# --- Dossiers de travail sur Windows ---
WORKDIR = r"C:\FritaxArchInstaller"
ISO_DOWNLOAD_PATH = WORKDIR + r"\archlinux-x86_64.iso"
ISO_CUSTOM_PATH = WORKDIR + r"\archlinux-fritax.iso"
ISO_EXTRACT_DIR = WORKDIR + r"\iso_extrait"
BOOT_LOOPBACK_DIR = r"\FritaxArchBoot"  # dossier créé à la racine de la partition EFI/système

# --- Système de secours (rescue) ---
RESCUE_ENABLED = True
RESCUE_LABEL = "Fritax-Secours"
RESCUE_SIZE_MIB = 4096  # taille de la partition de secours en Mio

# --- Raccourcis post-installation (label français -> commande shell) ---
SHORTCUTS = [
    ("🔄 Faire une mise à jour", "sudo pacman -Syu"),
    ("📦 Installer un logiciel", "sudo pacman -S "),
    ("🧹 Nettoyer le cache des paquets", "sudo pacman -Sc"),
    ("🌐 Afficher l'adresse IP", "ip a"),
    ("🖥️ Infos système", "neofetch"),
    ("🩹 Réparer les paquets", "sudo pacman -Syyu"),
    ("🚑 Démarrer sur le système de secours", "systemctl reboot --boot-loader-entry=fritax-secours"),
]
