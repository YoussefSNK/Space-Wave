"""
Module pour gérer un background partagé entre toutes les scènes.
Permet de conserver le même fond étoilé entre le menu, la sélection de niveau et le jeu.
"""

from graphics.background import Background

# Instance globale du background partagé
_shared_background = None


def get_shared_background(speed=2):
    """
    Retourne l'instance partagée du background.
    Crée le background s'il n'existe pas encore.

    Args:
        speed: Vitesse de défilement (utilisé seulement à la création initiale)

    Returns:
        L'instance Background partagée
    """
    global _shared_background
    if _shared_background is None:
        _shared_background = Background(speed=speed)
    return _shared_background


def set_background_speed(speed):
    """
    Modifie la vitesse du background partagé.

    Args:
        speed: Nouvelle vitesse de défilement
    """
    global _shared_background
    if _shared_background is not None:
        _shared_background.speed = speed
        _shared_background.default_speed = speed


def reset_shared_background():
    """
    Réinitialise le background partagé (force la régénération).
    À utiliser uniquement si nécessaire.
    """
    global _shared_background
    _shared_background = None
