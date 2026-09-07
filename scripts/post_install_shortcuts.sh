#!/usr/bin/env bash
# =============================================================================
#  Raccourcis Fritax 🔧 — petit menu en français pour les commandes courantes.
#  Lance ce script avec : bash raccourcis-fritax.sh
# =============================================================================
set -uo pipefail

afficher_menu() {
    clear
    echo "🐧 ===== Raccourcis Fritax ===== 🐧"
    echo ""
    echo "  1) 🔄 Faire une mise à jour              (sudo pacman -Syu)"
    echo "  2) 📦 Installer un logiciel               (sudo pacman -S <nom>)"
    echo "  3) 🧹 Nettoyer le cache des paquets        (sudo pacman -Sc)"
    echo "  4) 🌐 Afficher l'adresse IP                (ip a)"
    echo "  5) 🖥️  Infos système                       (fastfetch)"
    echo "  6) 🩹 Réparer/forcer la mise à jour         (sudo pacman -Syyu)"
    echo "  7) 🚑 Redémarrer sur le système de secours"
    echo "  0) 👋 Quitter"
    echo ""
}

while true; do
    afficher_menu
    read -rp "Choisis une option : Cliquez ici ;D) " choix
    case "$choix" in
        1) sudo pacman -Syu ;;
        2) read -rp "📦 Nom du logiciel : " pkg; sudo pacman -S "$pkg" ;;
        3) sudo pacman -Sc ;;
        4) ip a ;;
        5) fastfetch ;;
        6) sudo pacman -Syyu ;;
        7) systemctl reboot --boot-loader-entry=fritax-secours ;;
        0) echo "Coucou :) à bientôt !"; break ;;
        *) echo "❓ Choix inconnu..." ;;
    esac
    echo ""
    read -rp "Appuie sur Entrée pour continuer..." _
done
