# FritaxLoader 🐧⚡

Mini bootloader x86 en mode réel BIOS (16 bits) : un secteur de boot de
512 octets qui affiche juste "Fritax Loader" à l'écran. C'est un projet
"toy" pour apprendre/s'amuser avec le bas niveau — **pas** un remplacement
de GRUB (celui-ci reste le bootloader réel du système installé).

## Compiler

```bash
sudo pacman -S nasm qemu-full   # sur Arch
nasm -f bin boot.asm -o boot.bin
```

## Tester (sans toucher à du matériel réel)

```bash
qemu-system-x86_64 -drive format=raw,file=boot.bin
```

## Écrire sur une vraie clé USB (⚠️ efface tout dessus)

```bash
sudo dd if=boot.bin of=/dev/sdX bs=512 status=progress
```
