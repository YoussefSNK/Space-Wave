"""Utilitaire pour gérer les chemins de ressources avec PyInstaller."""
import os
import sys


def resource_path(relative_path):
    """Obtient le chemin absolu d'une ressource, fonctionne pour dev et pour PyInstaller.

    Args:
        relative_path: Chemin relatif de la ressource (ex: "sprites/Spaceship.png")

    Returns:
        Chemin absolu de la ressource
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En développement, utiliser le répertoire courant
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
