"""
Gestionnaire centralisé pour la mise à jour et le filtrage des projectiles ennemis.
Permet de gérer tous les projectiles depuis un seul endroit.
"""

import inspect
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from entities.projectiles import (
    HomingProjectile, EdgeRollerProjectile, BallBreakerProjectile,
    SplittingProjectile, MirrorProjectile, BlackHoleProjectile, PulseWaveProjectile
)


def update_enemy_projectiles(projectiles, player_position):
    """
    Met à jour tous les projectiles ennemis en détectant automatiquement
    leurs besoins via introspection.

    Args:
        projectiles: Liste des projectiles ennemis à mettre à jour
        player_position: Tuple (x, y) de la position du joueur

    Returns:
        Liste mise à jour des projectiles (incluant les nouveaux projectiles issus de divisions)
    """
    # Mise à jour de chaque projectile
    for proj in projectiles:
        # Obtenir la signature de la méthode update
        update_method = proj.update
        sig = inspect.signature(update_method)
        params = list(sig.parameters.keys())

        # Appeler update() avec les bons paramètres selon ce que le projectile attend
        if 'player_position' in params and 'other_projectiles' in params:
            # Le projectile a besoin de la position du joueur ET des autres projectiles
            # Ex: EdgeRollerProjectile
            proj.update(player_position, projectiles)
        elif 'player_position' in params:
            # Le projectile a besoin seulement de la position du joueur
            # Ex: HomingProjectile
            proj.update(player_position)
        elif 'other_projectiles' in params:
            # Le projectile a besoin seulement des autres projectiles
            # Ex: BallBreakerProjectile
            proj.update(projectiles)
        else:
            # Le projectile n'a besoin de rien
            # Ex: EnemyProjectile standard
            proj.update()

    # Gérer les projectiles qui se divisent
    new_split = []
    for proj in projectiles:
        if isinstance(proj, SplittingProjectile) and proj.should_split():
            new_split.extend(proj.split())
        elif isinstance(proj, MirrorProjectile) and proj.should_split():
            new_split.extend(proj.split())

    # Ajouter les nouveaux projectiles issus des divisions
    projectiles.extend(new_split)

    return projectiles


def filter_enemy_projectiles(projectiles):
    """
    Filtre les projectiles ennemis pour enlever ceux qui sont hors écran
    ou expirés.

    Args:
        projectiles: Liste des projectiles ennemis à filtrer

    Returns:
        Liste filtrée des projectiles
    """
    return [p for p in projectiles if (
        p.rect.top < SCREEN_HEIGHT and
        p.rect.left < SCREEN_WIDTH and
        p.rect.right > 0 and
        p.rect.bottom > 0 and
        not (isinstance(p, HomingProjectile) and p.is_expired()) and
        not (isinstance(p, BlackHoleProjectile) and p.is_expired()) and
        not (isinstance(p, PulseWaveProjectile) and p.is_expired()) and
        not (isinstance(p, BallBreakerProjectile) and p.bounces_left < 0)
    )]


def manage_enemy_projectiles(projectiles, player_position):
    """
    Fonction principale pour gérer tous les projectiles ennemis :
    - Met à jour tous les projectiles
    - Gère les divisions
    - Filtre les projectiles hors écran ou expirés

    Args:
        projectiles: Liste des projectiles ennemis
        player_position: Tuple (x, y) de la position du joueur

    Returns:
        Liste mise à jour et filtrée des projectiles
    """
    # Mettre à jour et gérer les divisions
    projectiles = update_enemy_projectiles(projectiles, player_position)

    # Filtrer les projectiles
    projectiles = filter_enemy_projectiles(projectiles)

    return projectiles
