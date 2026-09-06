# -*- coding: utf-8 -*-
"""Petite pluie Matrix animée en Tkinter, affichée pendant l'installation."""

import random
import string
import tkinter as tk

CHARSET = string.ascii_letters + string.digits + "アイウエオカキクケコサシスセソ0123456789"


class MatrixRain(tk.Canvas):
    """Canvas avec un effet 'pluie Matrix' en fond, plus un message et une barre de progression."""

    def __init__(self, master, width=700, height=420, **kwargs):
        super().__init__(master, width=width, height=height, bg="black", highlightthickness=0, **kwargs)
        self._width = width
        self._height = height
        self.font_size = 16
        self.columns = width // self.font_size
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self._running = False

        # Message + barre de progression posés par-dessus la pluie
        self.message_id = self.create_text(
            width // 2, height // 2 - 30,
            text="Nous installons votre système... (et dis merci à eden :3) 💚",
            fill="#00ff41", font=("Consolas", 12, "bold"), width=width - 60,
            justify="center",
        )
        self.progress_bg = self.create_rectangle(
            60, height // 2 + 10, width - 60, height // 2 + 35,
            outline="#00ff41", width=2,
        )
        self.progress_bar = self.create_rectangle(
            60, height // 2 + 10, 60, height // 2 + 35,
            fill="#00ff41", width=0,
        )
        self.progress_text = self.create_text(
            width // 2, height // 2 + 55,
            text="0 %", fill="#00ff41", font=("Consolas", 10),
        )

    def set_message(self, text):
        self.itemconfig(self.message_id, text=text)

    def set_progress(self, percent):
        percent = max(0, min(100, percent))
        x0 = 60
        x1 = 60 + (self._width - 120) * (percent / 100.0)
        self.coords(self.progress_bar, x0, self._height // 2 + 10, x1, self._height // 2 + 35)
        self.itemconfig(self.progress_text, text=f"{percent:.0f} %")

    def start(self):
        self._running = True
        self._tick()

    def stop(self):
        self._running = False

    def _tick(self):
        if not self._running:
            return
        # Efface juste les colonnes de texte (pas le message/la barre : on les remonte au-dessus)
        self.delete("glyph")
        for i, y in enumerate(self.drops):
            x = i * self.font_size
            char = random.choice(CHARSET)
            color = "#00ff41" if random.random() > 0.1 else "#ffffff"
            self.create_text(x, y * self.font_size, text=char, fill=color,
                              font=("Consolas", self.font_size), tags="glyph")
            if y * self.font_size > self._height and random.random() > 0.975:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        # Garde le message et la barre de progression visibles au-dessus de la pluie
        self.tag_raise(self.message_id)
        self.tag_raise(self.progress_bg)
        self.tag_raise(self.progress_bar)
        self.tag_raise(self.progress_text)

        self.after(50, self._tick)
