#!/usr/bin/env bash
# =============================================================================
#  Installe le thème de démarrage Plymouth "Fritax" (spinner hexagonal animé,
#  adapté de adi1090x/plymouth-themes, + barre de progression discrète) sur
#  le système Arch installé.
#
#  À exécuter APRÈS install_arch.sh, soit :
#    - directement sur le système installé (après le premier redémarrage), ou
#    - en chroot : arch-chroot /mnt bash scripts/setup_plymouth.sh
#
#  Nécessite les droits root.
# =============================================================================
set -euo pipefail

THEME_DIR="/usr/share/plymouth/themes/fritax"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/plymouth-fritax" && pwd)"

echo "🎨 Installation du thème Plymouth Fritax..."

pacman -Sy --needed --noconfirm plymouth

mkdir -p "$THEME_DIR"
cp "$SRC_DIR/fritax.plymouth" "$THEME_DIR/"
cp "$SRC_DIR/fritax.script" "$THEME_DIR/"
cp "$SRC_DIR"/progress-*.png "$THEME_DIR/"

echo "🖌️ Activation du thème..."
plymouth-set-default-theme -R fritax

# --- Ajoute le hook plymouth à mkinitcpio (avant udev, juste après base) ---
if ! grep -q "plymouth" /etc/mkinitcpio.conf; then
    sed -i 's/^HOOKS=(base /HOOKS=(base plymouth /' /etc/mkinitcpio.conf
    mkinitcpio -P
fi

# --- Active le splash dans GRUB ---
if [ -f /etc/default/grub ]; then
    if ! grep -q "splash" /etc/default/grub; then
        sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="splash /' /etc/default/grub
        grub-mkconfig -o /boot/grub/grub.cfg
    fi
fi

echo "✅ Thème Fritax installé ! Il s'affichera au prochain démarrage."
