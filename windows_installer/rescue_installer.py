# -*- coding: utf-8 -*-
"""Préparation d'un système de secours (rescue), au cas où l'installation
principale d'Arch Linux serait cassée.

Le système de secours est une petite partition dédiée contenant une seconde
copie minimale d'Arch (base + outils de réparation), avec sa propre entrée
de démarrage GRUB "fritax-secours", indépendante de l'installation
principale. Si le système principal ne démarre plus, on choisit cette
entrée pour réparer (chroot, réinstaller GRUB, restaurer une sauvegarde...).

Ce module génère uniquement les scripts que archinstall / le script shell
`scripts/setup_rescue.sh` exécutera une fois dans l'environnement Arch live
(voir ce fichier) : la vraie création de partitions se fait depuis Linux,
pas depuis Windows, pour rester fiable avec GPT/LVM/btrfs.
"""

from config import RESCUE_ENABLED, RESCUE_LABEL, RESCUE_SIZE_MIB


def generer_resume(progress_callback=None):
    if progress_callback:
        progress_callback(100, "🚑 Le système de secours sera créé pendant l'installation Linux.")
    if not RESCUE_ENABLED:
        return "Système de secours désactivé."
    return (
        f"Une partition '{RESCUE_LABEL}' de {RESCUE_SIZE_MIB} Mio sera créée "
        f"pour héberger un système Arch minimal de secours, démarrable via "
        f"l'entrée GRUB 'fritax-secours'."
    )
