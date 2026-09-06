# -*- coding: utf-8 -*-
"""
🐧✨ Installateur Arch Linux pour Fritax ✨🐧

Application Windows (Tkinter) qui :
  1. Télécharge l'ISO officielle Arch Linux
  2. La personnalise un tout petit peu (nom de PC "PC-de-Fritax",
     utilisateur "fritaxdev")
  3. Prépare un démarrage SANS clé USB (GRUB loopback + entrée UEFI)
  4. Affiche une pluie Matrix EN PLEIN ÉCRAN + barre de progression pendant
     l'installation
  5. Donne des raccourcis pratiques une fois Arch installé

⚠️ Doit être lancé en tant qu'ADMINISTRATEUR sur Windows pour l'étape de
   préparation du démarrage (modification de la partition système / bcdedit).

Lancement : python ArchInstallerFritax.py
"""

import ctypes
import sys
import threading
import tkinter as tk
import urllib.request
from tkinter import messagebox

from config import HOSTNAME, RESCUE_ENABLED, SHORTCUTS, USERNAME
from iso_customizer import personnaliser_iso
from iso_downloader import telecharger_iso, verifier_checksum
from matrix_rain import MatrixRain
from nousb_boot import preparer_boot_sans_usb
from rescue_installer import generer_resume

ACCENT      = "#1793D1"
ACCENT_FONC = "#0F6FA3"
BLANC       = "#ffffff"
FOND        = "#F7F8FA"
TEXTE       = "#1B1B1F"
TEXTE_GRIS  = "#6B7280"
BORDURE     = "#E3E5E8"

LOGO_URL = "https://images.icon-icons.com/2108/PNG/512/archlinux_icon_130988.png"


def est_administrateur():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def rect_arrondi(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class FenetrePrincipale(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fritax Arch Setup")
        self.geometry("900x620")
        self.configure(bg=FOND)
        self._logo_cache = None

        self._construire_accueil()

    # ------------------------------------------------------------------
    # Utilitaires visuels
    # ------------------------------------------------------------------
    def _logo_arch(self, taille_cible=110):
        if self._logo_cache is None:
            try:
                req = urllib.request.Request(
                    LOGO_URL,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                        "Referer": "https://icon-icons.com/",
                    },
                )
                data = urllib.request.urlopen(req, timeout=8).read()
                img = tk.PhotoImage(data=data)
                facteur = max(1, round(img.width() / taille_cible))
                self._logo_cache = img.subsample(facteur, facteur)
            except Exception as exc:  # noqa: BLE001
                print("Logo Arch indisponible :", exc)
                self._logo_cache = False
        return self._logo_cache or None

    def _bouton_arrondi(self, parent, texte, cmd, primaire=True, largeur=280, hauteur=46, r=23):
        bg = ACCENT if primaire else BLANC
        fg = BLANC if primaire else TEXTE
        outline = "" if primaire else BORDURE
        c = tk.Canvas(parent, width=largeur, height=hauteur, bg=FOND, highlightthickness=0, cursor="hand2")
        forme = rect_arrondi(c, 1, 1, largeur - 1, hauteur - 1, r, fill=bg, outline=outline)
        txt = c.create_text(largeur / 2, hauteur / 2, text=texte, fill=fg, font=("Segoe UI", 11, "bold"))
        hover = ACCENT_FONC if primaire else "#F0F1F3"
        c.tag_bind(forme, "<Enter>", lambda e: c.itemconfig(forme, fill=hover))
        c.tag_bind(txt, "<Enter>", lambda e: c.itemconfig(forme, fill=hover))
        c.tag_bind(forme, "<Leave>", lambda e: c.itemconfig(forme, fill=bg))
        c.tag_bind(txt, "<Leave>", lambda e: c.itemconfig(forme, fill=bg))
        c.tag_bind(forme, "<Button-1>", lambda e: cmd())
        c.tag_bind(txt, "<Button-1>", lambda e: cmd())
        return c

    def _carte(self, parent, icone, label, valeur, largeur=580, hauteur=64, r=16):
        c = tk.Canvas(parent, width=largeur, height=hauteur, bg=FOND, highlightthickness=0)
        rect_arrondi(c, 1, 1, largeur - 1, hauteur - 1, r, fill=BLANC, outline=BORDURE)
        inner = tk.Frame(c, bg=BLANC)
        c.create_window(r, hauteur / 2, window=inner, anchor="w", width=largeur - 2 * r)
        ligne = tk.Frame(inner, bg=BLANC)
        ligne.pack(fill="both", expand=True)
        tk.Label(ligne, text=icone, bg=BLANC, font=("Segoe UI", 14)).pack(side="left", padx=(0, 12))
        txt = tk.Frame(ligne, bg=BLANC)
        txt.pack(side="left", fill="x", expand=True)
        tk.Label(txt, text=label, bg=BLANC, fg=TEXTE_GRIS, font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x")
        tk.Label(txt, text=valeur, bg=BLANC, fg=TEXTE, font=("Segoe UI", 12), anchor="w").pack(fill="x")
        tk.Label(ligne, text="▾", bg=BLANC, fg=TEXTE_GRIS, font=("Segoe UI", 11)).pack(side="right", padx=(0, 12))
        return c

    def _etapes(self, parent, actif):
        noms = ["Informations", "Installation", "Terminé"]
        fond = tk.Frame(parent, bg=BLANC)
        for i, nom in enumerate(noms):
            couleur = ACCENT if i <= actif else BORDURE
            texte_c = TEXTE if i <= actif else TEXTE_GRIS
            pastille = tk.Canvas(fond, width=22, height=22, bg=BLANC, highlightthickness=0)
            pastille.create_oval(2, 2, 20, 20, fill=couleur, outline="")
            pastille.create_text(11, 11, text=str(i + 1), fill=BLANC, font=("Segoe UI", 9, "bold"))
            pastille.pack(side="left", padx=(10 if i == 0 else 0, 0))
            tk.Label(fond, text=nom, bg=BLANC, fg=texte_c, font=("Segoe UI", 9)).pack(side="left", padx=(6, 18))
        return fond

    def _panneau_lateral(self, sous_titre):
        cote = tk.Frame(self, bg=ACCENT, width=260)
        cote.pack(side="left", fill="y")
        cote.pack_propagate(False)
        milieu = tk.Frame(cote, bg=ACCENT)
        milieu.place(relx=0.5, rely=0.42, anchor="center")

        img = self._logo_arch()
        if img:
            pad = 20
            taille = max(img.width(), img.height()) + pad * 2
            badge = tk.Canvas(milieu, width=taille, height=taille, bg=ACCENT, highlightthickness=0)
            badge.create_oval(1, 1, taille - 1, taille - 1, fill=BLANC, outline="")
            badge.create_image(taille / 2, taille / 2, image=img)
            badge.image = img
            badge.pack()
        else:
            tk.Label(milieu, text="🐧", bg=ACCENT, fg=BLANC, font=("Segoe UI", 40)).pack()

        tk.Label(milieu, text="Fritax Arch Setup", bg=ACCENT, fg=BLANC,
                  font=("Segoe UI", 15, "bold")).pack(pady=(14, 4))
        tk.Label(milieu, text=sous_titre, bg=ACCENT, fg="#DCEEFB",
                  font=("Segoe UI", 9), wraplength=190, justify="center").pack()
        tk.Label(cote, text="© eden & Fritax", bg=ACCENT, fg="#BFE0F5",
                  font=("Segoe UI", 8)).pack(side="bottom", pady=16)
        return cote

    # ------------------------------------------------------------------
    # Écran 1 : accueil
    # ------------------------------------------------------------------
    def _construire_accueil(self):
        for w in self.winfo_children():
            w.destroy()
        self.attributes("-fullscreen", False)
        self.configure(bg=FOND)

        self._panneau_lateral("Remplace Windows par Arch Linux, sans clé USB.")

        droite = tk.Frame(self, bg=FOND)
        droite.pack(side="left", fill="both", expand=True)

        haut = tk.Frame(droite, bg=FOND)
        haut.pack(fill="x", padx=48, pady=(30, 0))
        fond_etapes = tk.Frame(haut, bg=BLANC)
        self._etapes(fond_etapes, actif=0).pack(padx=4, pady=2)
        fond_etapes.pack(anchor="w")

        corps = tk.Frame(droite, bg=FOND)
        corps.pack(fill="both", expand=True, padx=48, pady=(20, 0))

        tk.Label(corps, text="Coucou :) Bienvenue !  😄", bg=FOND, fg=TEXTE,
                  font=("Segoe UI", 22, "bold"), anchor="w").pack(fill="x")
        tk.Label(corps, text="Vérifie les informations ci-dessous avant de continuer.",
                  bg=FOND, fg=TEXTE_GRIS, font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(2, 20))

        self._carte(corps, "🖥️", "NOM DU PC À INSTALLER", HOSTNAME).pack(fill="x", pady=6)
        self._carte(corps, "👤", "NOM D'UTILISATEUR", USERNAME).pack(fill="x", pady=6)
        self._carte(corps, "🚑", "SYSTÈME DE SECOURS", "activé" if RESCUE_ENABLED else "désactivé").pack(fill="x", pady=6)

        if not est_administrateur():
            tk.Label(corps, text="⚠️ Lance cette application en tant qu'ADMINISTRATEUR pour continuer !",
                      bg=FOND, fg="#B45309", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(16, 0))
        else:
            tk.Label(corps, text="⚠️  Cette installation REMPLACE COMPLÈTEMENT Windows. Sauvegarde tes fichiers !",
                      bg=FOND, fg="#B45309", font=("Segoe UI", 9)).pack(anchor="w", pady=(16, 0))

        bas = tk.Frame(droite, bg=FOND)
        bas.pack(fill="x", padx=48, pady=24, side="bottom")
        self._bouton_arrondi(bas, "Cliquez ici pour commencer ;D)  →", self._confirmer_depart, largeur=340).pack(side="right")
        self._bouton_arrondi(bas, "🔧 Voir les raccourcis", self._construire_raccourcis,
                              primaire=False, largeur=220).pack(side="right", padx=(0, 12))

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
    # Écran 2 : installation — pluie Matrix EN PLEIN ÉCRAN
    # ------------------------------------------------------------------
    def _construire_ecran_installation(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg="black")

        # Overlay plein écran : la fenêtre prend tout l'écran pendant l'installation
        self.attributes("-fullscreen", True)
        self.update_idletasks()
        largeur = self.winfo_screenwidth()
        hauteur = self.winfo_screenheight()

        self.rain = MatrixRain(self, width=largeur, height=hauteur)
        self.rain.pack(fill="both", expand=True)
        self.rain.start()

        # Échapper permet de quitter le plein écran en cas de besoin (debug/démo)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        threading.Thread(target=self._lancer_pipeline, daemon=True).start()

    def _maj_progression(self, pourcentage, texte):
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
            self.after(1200, self._fin_pipeline)
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: messagebox.showerror("Erreur ❌", f"Une erreur est survenue :\n{exc}"))

    def _fin_pipeline(self):
        self.rain.stop()
        self.attributes("-fullscreen", False)
        self._construire_ecran_fin()

    # ------------------------------------------------------------------
    # Écran 3 : fin
    # ------------------------------------------------------------------
    def _construire_ecran_fin(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=FOND)

        self._panneau_lateral("Merci d'avoir utilisé Fritax Arch Setup !")

        droite = tk.Frame(self, bg=FOND)
        droite.pack(side="left", fill="both", expand=True)

        haut = tk.Frame(droite, bg=FOND)
        haut.pack(fill="x", padx=48, pady=(30, 0))
        fond_etapes = tk.Frame(haut, bg=BLANC)
        self._etapes(fond_etapes, actif=2).pack(padx=4, pady=2)
        fond_etapes.pack(anchor="w")

        corps = tk.Frame(droite, bg=FOND)
        corps.pack(fill="both", expand=True, padx=48, pady=(24, 0))

        tk.Label(corps, text="✅  C'est prêt !", bg=FOND, fg=TEXTE,
                  font=("Segoe UI", 22, "bold"), anchor="w").pack(fill="x")
        tk.Label(corps, text="Redémarre et choisis 'Fritax - Installer Arch Linux 🐧' au démarrage.",
                  bg=FOND, fg=TEXTE_GRIS, font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(2, 20))

        tk.Label(corps, text="Raccourcis disponibles une fois Arch installé", bg=FOND, fg=TEXTE,
                  font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x", pady=(0, 8))
        for label, commande in SHORTCUTS:
            self._carte(corps, "🔧", label.upper(), commande).pack(fill="x", pady=4)

        bas = tk.Frame(droite, bg=FOND)
        bas.pack(fill="x", padx=48, pady=24, side="bottom")
        self._bouton_arrondi(bas, "🔄 Redémarrer maintenant", self._redemarrer, largeur=260).pack(side="right")

    def _redemarrer(self):
        if messagebox.askyesno("Redémarrage", "Redémarrer maintenant ? Sauvegarde bien tes fichiers avant !"):
            import subprocess
            subprocess.run(["shutdown", "/r", "/t", "5"])

    # ------------------------------------------------------------------
    # Écran des raccourcis (accessible sans lancer l'installation)
    # ------------------------------------------------------------------
    def _construire_raccourcis(self):
        for w in self.winfo_children():
            w.destroy()
        self.attributes("-fullscreen", False)
        self.configure(bg=FOND)

        self._panneau_lateral("Raccourcis à utiliser une fois sous Arch Linux.")

        droite = tk.Frame(self, bg=FOND)
        droite.pack(side="left", fill="both", expand=True)

        corps = tk.Frame(droite, bg=FOND)
        corps.pack(fill="both", expand=True, padx=48, pady=(40, 0))

        tk.Label(corps, text="🔧 Raccourcis Fritax", bg=FOND, fg=TEXTE,
                  font=("Segoe UI", 20, "bold"), anchor="w").pack(fill="x", pady=(0, 20))

        for label, commande in SHORTCUTS:
            self._carte(corps, "▶️", label.upper(), commande).pack(fill="x", pady=5)

        bas = tk.Frame(droite, bg=FOND)
        bas.pack(fill="x", padx=48, pady=24, side="bottom")
        self._bouton_arrondi(bas, "⬅️ Retour", self._construire_accueil, primaire=False, largeur=180).pack(side="right")


if __name__ == "__main__":
    if sys.platform == "win32" and not est_administrateur():
        messagebox.showwarning(
            "Droits administrateur requis ⚠️",
            "Relance cette application en tant qu'administrateur pour pouvoir\n"
            "préparer le démarrage sans clé USB.",
        )
    app = FenetrePrincipale()
    app.mainloop()
