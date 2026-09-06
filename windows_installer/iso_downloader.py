# -*- coding: utf-8 -*-
"""Téléchargement de l'ISO Arch Linux officielle avec suivi de progression."""

import hashlib
import os
import urllib.request

from config import ARCH_MIRROR_ISO_URL, ARCH_MIRROR_CHECKSUM_URL, ISO_DOWNLOAD_PATH, WORKDIR


def telecharger_iso(progress_callback=None):
    """Télécharge l'ISO officielle Arch Linux (aucune modification à ce stade).

    progress_callback(percent: float, texte: str) est appelé régulièrement.
    """
    os.makedirs(WORKDIR, exist_ok=True)

    if progress_callback:
        progress_callback(0, "📡 Connexion au miroir Arch Linux...")

    def _hook(block_num, block_size, total_size):
        if total_size <= 0 or not progress_callback:
            return
        downloaded = block_num * block_size
        percent = min(100.0, downloaded * 100.0 / total_size)
        progress_callback(percent, f"⬇️ Téléchargement de l'ISO... {percent:.0f} %")

    urllib.request.urlretrieve(ARCH_MIRROR_ISO_URL, ISO_DOWNLOAD_PATH, reporthook=_hook)

    if progress_callback:
        progress_callback(100, "✅ Téléchargement terminé !")

    return ISO_DOWNLOAD_PATH


def verifier_checksum(iso_path=ISO_DOWNLOAD_PATH):
    """Vérifie le sha256 de l'ISO téléchargée par rapport au fichier officiel de sommes."""
    try:
        with urllib.request.urlopen(ARCH_MIRROR_CHECKSUM_URL) as resp:
            sums_text = resp.read().decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover - dépend du réseau
        return None, f"⚠️ Impossible de récupérer les sommes de contrôle : {exc}"

    filename = os.path.basename(iso_path)
    expected = None
    for line in sums_text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == filename:
            expected = parts[0]
            break

    if not expected:
        return None, "⚠️ Somme de contrôle introuvable pour ce fichier."

    sha256 = hashlib.sha256()
    with open(iso_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)
    actual = sha256.hexdigest()

    if actual.lower() == expected.lower():
        return True, "✅ Somme de contrôle vérifiée, l'ISO est intègre !"
    return False, "❌ La somme de contrôle ne correspond pas, retélécharge l'ISO !"
