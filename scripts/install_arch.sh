#!/usr/bin/env bash
# =============================================================================
#  Installateur automatique Arch Linux pour Fritax 🐧✨
#  À exécuter DANS l'environnement Arch Linux live (après démarrage sans clé
#  USB via l'entrée GRUB "Installer Arch Linux (Fritax)").
#
#  ⚠️⚠️⚠️  ATTENTION - DESTRUCTEUR  ⚠️⚠️⚠️
#  Ce script EFFACE ENTIÈREMENT le disque choisi (y compris Windows) pour
#  installer Arch Linux à la place, plus une petite partition de secours.
#  Une confirmation explicite ("OUI EFFACER") est demandée avant toute
#  opération destructrice.
# =============================================================================
set -euo pipefail

HOSTNAME="PC-de-Fritax"
USERNAME="fritaxdev"
UCODE_PACKAGE="${UCODE_PACKAGE:-intel-ucode}"   # amd-ucode ou intel-ucode selon la branche
RESCUE_LABEL="Fritax-Secours"
RESCUE_SIZE="4GiB"

# --- Petite pluie Matrix + message pendant les étapes longues ---------------
matrix_rain() {
    local message="$1"
    if command -v cmatrix >/dev/null 2>&1; then
        timeout 3 cmatrix -s || true
    fi
    clear
    tput setaf 2
    echo "═══════════════════════════════════════════════════════════"
    echo "  Nous installons votre système... (et dis merci à eden :3) 💚"
    echo "  $message"
    echo "═══════════════════════════════════════════════════════════"
    tput sgr0
}

barre_progression() {
    local pct=$1
    local largeur=40
    local rempli=$(( pct * largeur / 100 ))
    local vide=$(( largeur - rempli ))
    printf "\r["
    printf "%0.s#" $(seq 1 "$rempli") 2>/dev/null || true
    printf "%0.s-" $(seq 1 "$vide") 2>/dev/null || true
    printf "] %3d%%" "$pct"
}

etape() {
    local pct="$1"; shift
    matrix_rain "$*"
    barre_progression "$pct"
    echo ""
}

echo "🇫🇷 Bienvenue dans l'installateur Arch Linux de Fritax ! 😄"
echo ""
echo "Disques disponibles :"
lsblk -d -o NAME,SIZE,MODEL
echo ""
read -rp "👉 Sur quel disque veut-on installer Arch Linux (ex: sda, nvme0n1) ? " DISK
DISK="/dev/${DISK}"

echo ""
echo "⚠️  TOUT le contenu de $DISK (y compris Windows) va être EFFACÉ définitivement."
read -rp "Tape exactement OUI EFFACER pour continuer : " CONFIRM
if [[ "$CONFIRM" != "OUI EFFACER" ]]; then
    echo "❌ Annulé, aucune donnée n'a été modifiée. À bientôt ! 👋"
    exit 1
fi

etape 5 "Partitionnement du disque (EFI + racine + secours)..."

parted -s "$DISK" -- mklabel gpt
parted -s "$DISK" -- mkpart ESP fat32 1MiB 513MiB
parted -s "$DISK" -- set 1 esp on
parted -s "$DISK" -- mkpart primary ext4 513MiB -"$RESCUE_SIZE"
parted -s "$DISK" -- mkpart primary ext4 -"$RESCUE_SIZE" 100%

if [[ "$DISK" == *nvme* ]]; then
    P1="${DISK}p1"; P2="${DISK}p2"; P3="${DISK}p3"
else
    P1="${DISK}1"; P2="${DISK}2"; P3="${DISK}3"
fi

etape 15 "Formatage des partitions..."
mkfs.fat -F32 "$P1"
mkfs.ext4 -F -L fritax_root "$P2"
mkfs.ext4 -F -L "$RESCUE_LABEL" "$P3"

etape 25 "Montage des partitions..."
mount "$P2" /mnt
mkdir -p /mnt/boot
mount "$P1" /mnt/boot
mkdir -p /mnt/mnt/secours
mount "$P3" /mnt/mnt/secours

etape 35 "Installation du système de base (pacstrap) — ça peut prendre un moment ☕"
pacstrap -K /mnt base linux linux-firmware "$UCODE_PACKAGE" \
    networkmanager sudo grub efibootmgr sudo vim fastfetch cmatrix bash-completion

etape 60 "Génération de la table des systèmes de fichiers (fstab)..."
genfstab -U /mnt >> /mnt/etc/fstab

etape 65 "Configuration du système (nom de PC, utilisateur, locales)..."
arch-chroot /mnt /bin/bash -e <<CHROOT_EOF
echo "$HOSTNAME" > /etc/hostname
cat >> /etc/hosts <<HOSTS_EOF
127.0.0.1   localhost
::1         localhost
127.0.1.1   $HOSTNAME.localdomain $HOSTNAME
HOSTS_EOF

ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
hwclock --systohc

echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=fr_FR.UTF-8" > /etc/locale.conf
echo "KEYMAP=fr" > /etc/vconsole.conf

useradd -m -G wheel -s /bin/bash "$USERNAME"
echo "🔐 Choisis un mot de passe pour $USERNAME :"
passwd "$USERNAME"
echo "🔐 Et un mot de passe administrateur (root) :"
passwd root
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

systemctl enable NetworkManager

echo "Bienvenue $USERNAME ! Ton PC s'appelle $HOSTNAME 😄" > /etc/motd
CHROOT_EOF

etape 80 "Installation de GRUB (démarrage principal)..."
arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=Fritax
arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg

etape 85 "🎨 Installation du thème de démarrage Plymouth..."
cp -r "$(dirname "$0")" /mnt/root/fritax-scripts
arch-chroot /mnt bash /root/fritax-scripts/setup_plymouth.sh
rm -rf /mnt/root/fritax-scripts

etape 90 "Préparation du système de secours 'Fritax-Secours' 🚑..."
bash "$(dirname "$0")/setup_rescue.sh" "$P3"

etape 95 "Installation des raccourcis (mise à jour, etc.) 🔧..."
cp "$(dirname "$0")/post_install_shortcuts.sh" /mnt/home/"$USERNAME"/raccourcis-fritax.sh || true
arch-chroot /mnt chown "$USERNAME:$USERNAME" /home/"$USERNAME"/raccourcis-fritax.sh || true
arch-chroot /mnt chmod +x /home/"$USERNAME"/raccourcis-fritax.sh || true

etape 100 "Installation terminée ! 🎉🎉🎉"

echo ""
echo "✅ Arch Linux est installé sur $DISK, nom de machine : $HOSTNAME, utilisateur : $USERNAME."
echo "🚑 Un système de secours est disponible via l'entrée GRUB 'fritax-secours'."
echo "🔁 Tu peux redémarrer maintenant : reboot"
echo ""
echo "Merci à eden :3"
