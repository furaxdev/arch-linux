# -*- coding: utf-8 -*-
"""
🐧✨ Installateur Arch Linux pour Fritax ✨🐧

Application Windows (Tkinter) qui :
  1. Télécharge l'ISO officielle Arch Linux
  2. La personnalise un tout petit peu (nom de PC "PC-de-Fritax",
     utilisateur "fritaxdev")
  3. Prépare un démarrage SANS clé USB (GRUB loopback + entrée UEFI)
  4. Affiche une pluie Matrix + barre de progression pendant les étapes longues
  5. Donne des raccourcis pratiques une fois Arch installé

⚠️ Doit être lancé en tant qu'ADMINISTRATEUR sur Windows pour l'étape de
   préparation du démarrage (modification de la partition système / bcdedit).

Lancement : python ArchInstallerFritax.py
"""

import ctypes
import sys
import threading
import tkinter as tk
from tkinter import messagebox

from config import HOSTNAME, RESCUE_ENABLED, SHORTCUTS, USERNAME
from iso_customizer import personnaliser_iso
from iso_downloader import telecharger_iso, verifier_checksum
from matrix_rain import MatrixRain
from nousb_boot import preparer_boot_sans_usb
from rescue_installer import generer_resume

BG = "#0d0d0d"
FG = "#00ff41"


def est_administrateur():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


class FenetrePrincipale(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐧 Installateur Arch Linux - Fritax Edition ✨")
        self.geometry("760x560")
        self.configure(bg=BG)
        self.resizable(False, False)

        self._construire_accueil()

    # ------------------------------------------------------------------
    # Écran d'accueil
    # ------------------------------------------------------------------
    def _construire_accueil(self):
        for w in self.winfo_children():
            w.destroy()

        tk.Label(
            self, text="Coucou :) Bienvenue dans l'installateur Arch Linux de Fritax ! 😄",
            bg=BG, fg=FG, font=("Consolas", 15, "bold"), wraplength=700, justify="center",
        ).pack(pady=(30, 10))

        infos = (
            f"🖥️ Nom du PC : {HOSTNAME}\n"
            f"👤 Utilisateur : {USERNAME}\n"
            f"🚑 Système de secours : {'activé' if RESCUE_ENABLED else 'désactivé'}\n\n"
            "⚠️ ATTENTION : cette installation va REMPLACER COMPLÈTEMENT Windows\n"
            "par Arch Linux sur le disque choisi. Sauvegarde tes fichiers importants\n"
            "avant de continuer ! 🙏\n\n"
            "Aucune clé USB n'est nécessaire, tout se fait depuis Windows. 🚀"
        )
        tk.Label(self, text=infos, bg=BG, fg="white", font=("Consolas", 11), justify="left").pack(pady=10)

        if not est_administrateur():
            tk.Label(
                self, text="⚠️ Lance cette application en tant qu'ADMINISTRATEUR pour continuer !",
                bg=BG, fg="orange", font=("Consolas", 10, "bold"),
            ).pack(pady=5)

        tk.Button(
            self, text="🚀 Cliquez ici pour commencer ;D)", font=("Consolas", 13, "bold"),
            bg=FG, fg="black", activebackground="#00cc33", command=self._confirmer_depart,
        ).pack(pady=30)

        tk.Button(
            self, text="🔧 J'ai déjà installé Arch, voir les raccourcis",
            font=("Consolas", 10), bg="#222", fg=FG, command=self._construire_raccourcis,
        ).pack()

    def _confirmer_depart(self):
        reponse = messagebox.askyesno(
            "Confirmation ⚠️",
            "Es-tu sûr·e de vouloir remplacer Windows par Arch Linux ?\n"
            "Cette action effacera TOUT le contenu du disque choisi.\n\n"
            "(La suppression réelle du disque se fera à la toute fin, dans "
            "l'environnement Arch, avec une seconde confirmation.)",
        )
        if reponse:
            self._construire_ecran_installation()

    # ------------------------------------------------------------------
    # Écran d'installation avec pluie Matrix + progress bar
    # ------------------------------------------------------------------
    def _construire_ecran_installation(self):
        for w in self.winfo_children():
            w.destroy()

        self.rain = MatrixRain(self, width=740, height=460)
        self.rain.pack(pady=10)
        self.rain.start()

        threading.Thread(target=self._lancer_pipeline, daemon=True).start()

    def _maj_progression(self, pourcentage, texte):
        # Appelé depuis un thread de fond -> on repasse par le thread Tk
        self.after(0, lambda: (self.rain.set_progress(pourcentage), self.rain.set_message(texte)))

    def _lancer_pipeline(self):
        try:
            self._maj_progression(0, "📡 Téléchargement de l'ISO Arch Linux officielle...")
            telecharger_iso(progress_callback=lambda p, t: self._maj_progression(p * 0.4, t))

            ok, message = verifier_checksum()
            self._maj_progression(42, message)

            self._maj_progression(45, "🎨 Personnalisation de l'ISO (nom du PC, utilisateur)...")
            personnaliser_iso(progress_callback=lambda p, t: self._maj_progression(45 + p * 0.3, t))

            self._maj_progression(78, "🥾 Préparation du démarrage SANS clé USB...")
            preparer_boot_sans_usb(progress_callback=lambda p, t: self._maj_progression(78 + p * 0.15, t))

            resume_secours = generer_resume()
            self._maj_progression(98, f"🚑 {resume_secours}")

            self._maj_progression(100, "✅ Tout est prêt ! Redémarre et choisis 'Fritax - Installer Arch Linux'. 🎉")
            self.after(0, self._fin_pipeline)
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: messagebox.showerror("Erreur ❌", f"Une erreur est survenue :\n{exc}"))

    def _fin_pipeline(self):
        self.rain.stop()
        for w in self.winfo_children():
            w.destroy()

        tk.Label(
            self, text="🎉 Préparation terminée ! Redémarre ton PC.",
            bg=BG, fg=FG, font=("Consolas", 16, "bold"),
        ).pack(pady=30)
        tk.Label(
            self,
            text=(
                "Au démarrage, choisis l'entrée :\n"
                "  🐧 'Fritax - Installer Arch Linux'\n\n"
                "L'installation continuera automatiquement (partitionnement,\n"
                "système de secours, etc.) via le script scripts/install_arch.sh."
            ),
            bg=BG, fg="white", font=("Consolas", 11), justify="center",
        ).pack(pady=10)

        tk.Button(
            self, text="🔄 Redémarrer maintenant", font=("Consolas", 12, "bold"),
            bg=FG, fg="black", command=self._redemarrer,
        ).pack(pady=20)

    def _redemarrer(self):
        if messagebox.askyesno("Redémarrage", "Redémarrer maintenant ? Sauvegarde bien tes fichiers avant !"):
            import subprocess
            subprocess.run(["shutdown", "/r", "/t", "5"])

    # ------------------------------------------------------------------
    # Écran des raccourcis post-installation
    # ------------------------------------------------------------------
    def _construire_raccourcis(self):
        for w in self.winfo_children():
            w.destroy()

        tk.Label(
            self, text="🔧 Raccourcis Fritax (à utiliser une fois sous Arch Linux)",
            bg=BG, fg=FG, font=("Consolas", 13, "bold"),
        ).pack(pady=20)

        for label, commande in SHORTCUTS:
            frame = tk.Frame(self, bg=BG)
            frame.pack(fill="x", padx=40, pady=4)
            tk.Label(frame, text=label, bg=BG, fg="white", font=("Consolas", 11), anchor="w").pack(side="left")
            tk.Label(frame, text=commande, bg=BG, fg="#888", font=("Consolas", 9), anchor="e").pack(side="right")

        tk.Button(
            self, text="⬅️ Retour", font=("Consolas", 10), bg="#222", fg=FG,
            command=self._construire_accueil,
        ).pack(pady=20)


if __name__ == "__main__":
    if sys.platform == "win32" and not est_administrateur():
        messagebox.showwarning(
            "Droits administrateur requis ⚠️",
            "Relance cette application en tant qu'administrateur pour pouvoir\n"
            "préparer le démarrage sans clé USB.",
        )
    app = FenetrePrincipale()
    app.mainloop()
