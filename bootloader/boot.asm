; FritaxLoader — mini bootloader x86 BIOS (secteur de boot 512 octets)
; Assemble avec NASM : nasm -f bin boot.asm -o boot.bin
; Teste avec QEMU   : qemu-system-x86_64 -drive format=raw,file=boot.bin

[org 0x7c00]
[bits 16]

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00
    sti

    mov si, msg
.print:
    lodsb
    or al, al
    jz .halt
    mov ah, 0x0e
    int 0x10
    jmp .print

.halt:
    cli
    hlt
    jmp .halt

msg db "Fritax Loader", 13, 10, 0

times 510 - ($ - $$) db 0
dw 0xaa55
