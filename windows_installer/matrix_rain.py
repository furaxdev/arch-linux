# -*- coding: utf-8 -*-
"""Pluie Matrix plein écran affichée pendant l'installation, avec un panneau
et une barre de progression aux coins arrondis."""

import random
import string
import tkinter as tk

CHARSET = string.ascii_letters + string.digits + "アイウエオカキクケコサシスセソ0123456789"
VERT = "#00ff41"


def rect_arrondi(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class MatrixRain(tk.Canvas):
    """Canvas plein écran avec un effet 'pluie Matrix', un panneau arrondi,
    un message et une barre de progression arrondie."""

    def __init__(self, master, width=700, height=420, **kwargs):
        super().__init__(master, width=width, height=height, bg="black", highlightthickness=0, **kwargs)
        self._width = width
        self._height = height
        self.font_size = 16
        self.columns = max(1, width // self.font_size)
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self._running = False
        self._bar_id = None

        self._dessiner_panneau()

    def _dessiner_panneau(self):
        w, h = self._width, self._height
        self.panel = rect_arrondi(
            self, w / 2 - 300, h / 2 - 80, w / 2 + 300, h / 2 + 80, 20,
            fill="#04120a", outline="#0a8a2a", width=1,
        )
        self.message_id = self.create_text(
            w // 2, h // 2 - 40,
            text="Nous installons votre système... (et dis merci à eden :3) 💚",
            fill=VERT, font=("Consolas", 13, "bold"), width=520, justify="center",
        )
        self.progress_bg = rect_arrondi(
            self, w / 2 - 240, h // 2 + 10, w / 2 + 240, h // 2 + 34, 12,
            fill="", outline=VERT, width=2,
        )
        self._bar_id = rect_arrondi(
            self, w / 2 - 240, h // 2 + 10, w / 2 - 240, h // 2 + 34, 12,
            fill=VERT, outline="",
        )
        self.progress_text = self.create_text(
            w // 2, h // 2 + 56,
            text="0 %", fill=VERT, font=("Consolas", 10, "bold"),
        )

    def set_message(self, text):
        self.itemconfig(self.message_id, text=text)

    def set_progress(self, percent):
        percent = max(0, min(100, percent))
        w, h = self._width, self._height
        x0 = w / 2 - 240
        x1 = x0 + max(24, 480 * (percent / 100.0))
        self.delete(self._bar_id)
        self._bar_id = rect_arrondi(self, x0, h // 2 + 10, x1, h // 2 + 34, 12, fill=VERT, outline="")
        self.itemconfig(self.progress_text, text=f"{percent:.0f} %")
        self.tag_raise(self.progress_text)

    def redimensionner(self, width, height):
        """Recalcule le panneau/la barre pour une nouvelle taille (ex: passage en plein écran)."""
        self._width, self._height = width, height
        self.config(width=width, height=height)
        self.columns = max(1, width // self.font_size)
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        for item in (self.panel, self.message_id, self.progress_bg, self._bar_id, self.progress_text):
            self.delete(item)
        self._dessiner_panneau()

    def start(self):
        self._running = True
        self._tick()

    def stop(self):
        self._running = False

    def _tick(self):
        if not self._running:
            return
        self.delete("glyph")
        for i, y in enumerate(self.drops):
            x = i * self.font_size
            char = random.choice(CHARSET)
            color = VERT if random.random() > 0.1 else "#ffffff"
            self.create_text(x, y * self.font_size, text=char, fill=color,
                              font=("Consolas", self.font_size), tags="glyph")
            if y * self.font_size > self._height and random.random() > 0.975:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        for item in (self.panel, self.message_id, self.progress_bg, self._bar_id, self.progress_text):
            self.tag_raise(item)

        self.after(50, self._tick)
