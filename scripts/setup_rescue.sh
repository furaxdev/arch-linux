#!/usr/bin/env bash
# =============================================================================
#  Système de secours "Fritax-Secours" 🚑
#  Installe un mini-système Arch (juste de quoi réparer : base, outils
#  réseau, GRUB) sur la partition de secours, avec sa propre entrée GRUB
#  visible depuis le menu de démarrage, indépendante du système principal.
#
#  Usage : setup_rescue.sh /dev/sdaX
# =============================================================================
set -euo pipefail

RESCUE_PART="${1:?Usage: setup_rescue.sh /dev/sdaX}"
RESCUE_MNT="/mnt/mnt/secours"

echo "🚑 Installation du système de secours sur $RESCUE_PART..."

mkdir -p "$RESCUE_MNT"
mountpoint -q "$RESCUE_MNT" || mount "$RESCUE_PART" "$RESCUE_MNT"

pacstrap -K "$RESCUE_MNT" base linux linux-firmware networkmanager \
    grub efibootmgr vim parted

arch-chroot "$RESCUE_MNT" /bin/bash -e <<'CHROOT_EOF'
echo "fritax-secours" > /etc/hostname
echo "root:secours" | chpasswd
systemctl enable NetworkManager
echo "🚑 Système de secours Fritax prêt. Utilise-moi pour réparer le système principal !" > /etc/motd
CHROOT_EOF

# Ajoute une entrée dans le GRUB du système principal pointant vers ce noyau
# de secours (chargement direct du noyau/initramfs de la partition secours).
RESCUE_UUID=$(blkid -s UUID -o value "$RESCUE_PART")
cat >> /mnt/etc/grub.d/40_custom <<GRUB_EOF

menuentry "🚑 Fritax - Système de secours" --id fritax-secours {
    search --no-floppy --fs-uuid --set=root $RESCUE_UUID
    linux /boot/vmlinuz-linux root=UUID=$RESCUE_UUID rw
    initrd /boot/initramfs-linux.img
}
GRUB_EOF

arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg

echo "✅ Système de secours installé et ajouté au menu de démarrage GRUB."
