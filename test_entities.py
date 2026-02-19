"""
Fichier de test pour tester les entités individuellement.
Permet de choisir quel boss ou ennemi tester sans jouer tout le jeu.
"""

import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, YELLOW
from entities.player import Player
from entities.projectiles import (
    Projectile, SpreadProjectile,
    EnemyProjectile, BossProjectile, Boss2Projectile, Boss3Projectile,
    Boss4Projectile, Boss5Projectile, Boss6Projectile,
    ZigZagProjectile, GravityProjectile, TeleportingProjectile,
    VortexProjectile
)
from entities.powerup import PowerUp
from entities.enemy import (
    Enemy, ShootingEnemy,
    SniperEnemy, MineEnemy, ShieldEnemy, GhostEnemy, BomberEnemy,
    TeleporterEnemy, PulseEnemy, ReflectorEnemy, BurstEnemy,
    SpinnerEnemy, OrbiterEnemy, LaserDroneEnemy, ArmoredEnemy, ClonerEnemy,
    HealerEnemy, MagnetEnemy, OverchargedEnemy, SentinelEnemy, EchoEnemy,
    ChargerEnemy, ShadowEnemy, DrainerEnemy, SwarmEnemy, GridEnemy,
    FreezerEnemy, DiveEnemy, ScatterEnemy, AnchorEnemy, MirageEnemy,
    RipperEnemy, ChainEnemy
)
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8, Boss9
from graphics.background import Background
from graphics.effects import Explosion
from systems.combo import ComboSystem
from systems.projectile_manager import manage_enemy_projectiles


def get_pattern_name(enemy):
    """Retourne le nom du pattern actuel du boss"""
    # Boss6 et Boss7 utilisent 'pattern', les autres utilisent 'current_pattern'
    if isinstance(enemy, Boss9):
        patterns = {
            0: "Pluie de plumes",
            1: "Flammes de l'âme",
            2: "Orbes d'annihilation",
            3: "Spirale void",
            4: "Vague phoenix",
            5: "Barrage d'ailes",
            6: "Explosion renaissance (Rebirth)",
            7: "Double spirale (Rebirth)",
            8: "Apocalypse (Rebirth)"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    elif isinstance(enemy, Boss8):
        patterns = {
            0: "Pluie de cristaux",
            1: "Rayons prismatiques",
            2: "Tirs réfléchissants",
            3: "Spirale cristalline",
            4: "Fragments orbitaux",
            5: "Mur cristallin",
            6: "Explosion cristalline (Shattered)",
            7: "Tempête prismatique (Shattered)"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    elif isinstance(enemy, Boss7):
        patterns = {
            0: "Diagonale (210° / 330°)",
            1: "Vague (230° → 310°)",
            2: "Éventail (200° → 340°)",
            3: "Orbite (rotation 360°)",
            4: "Nova (8 directions x2)",
            5: "Mix Edge Roller + Curve Stalker (x2 côtés)",
            6: "Vague inversée (310° → 230° + finish 210°)"
        }
        return patterns.get(enemy.pattern_index, "Inconnu")

    elif isinstance(enemy, Boss6):
        patterns = {
            0: "Vortex orbital",
            1: "Ondes de choc",
            2: "Miroirs diviseurs",
            3: "Spirale inversée",
            4: "Trou noir",
            5: "Mur de distorsion",
            6: "Étoiles filantes",
            7: "Double vortex (Fureur)",
            8: "Apocalypse (Fureur)"
        }
        return patterns.get(enemy.pattern, "Inconnu")

    elif isinstance(enemy, Boss5):
        patterns = {
            0: "Projectiles zigzag",
            1: "Projectiles à gravité",
            2: "Projectiles téléporteurs",
            3: "Double spirale",
            4: "Mur ondulant",
            5: "Clone illusion",
            6: "Tempête (Rage)",
            7: "Chaos total (Rage)"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    elif isinstance(enemy, Boss4):
        patterns = {
            0: "Projectiles rebondissants",
            1: "Projectiles qui se divisent",
            2: "Charge",
            3: "Bouclier + tir radial",
            4: "Tempête solaire",
            5: "Rayons de soleil",
            6: "Nova"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    elif isinstance(enemy, Boss3):
        patterns = {
            0: "Missiles à tête chercheuse",
            1: "Mur avec trou",
            2: "Laser",
            3: "Vagues convergentes",
            4: "Pluie en diagonale",
            5: "Spirale double"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    elif isinstance(enemy, Boss2):
        patterns = {
            0: "Spirale",
            1: "Pluie verticale",
            2: "Double vague",
            3: "Croix rotative",
            4: "Rafale ciblée"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    elif isinstance(enemy, Boss):
        patterns = {
            0: "Tir ciblé",
            1: "Spirale",
            2: "Mur de projectiles",
            3: "Tir en éventail",
            4: "Pluie aléatoire"
        }
        return patterns.get(enemy.current_pattern, "Inconnu")

    return ""


def show_menu(screen, font):
    """Affiche le menu de sélection en trois colonnes"""
    screen.fill(BLACK)

    title = font.render("TEST DES ENTITES", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 14))

    item_font = pygame.font.SysFont(None, 22)
    start_y = 50
    spacing = 24

    # ── Colonne gauche : Bosses ──────────────────────────────────────
    col1_x = 30
    col1_label = item_font.render("[ BOSSES ]", True, (180, 180, 60))
    screen.blit(col1_label, (col1_x, start_y))
    boss_items = [
        ("1 - Boss 1 (Miedd)",              (255, 100, 100)),
        ("2 - Boss 2 (Hexagone violet)",     (150, 0, 255)),
        ("3 - Boss 3 (Diamant cyan)",        (0, 255, 255)),
        ("4 - Boss 4 (Soleil dore)",         (255, 215, 0)),
        ("5 - Boss 5 (Oeil du chaos)",       (0, 255, 100)),
        ("6 - Boss 6 (Vortex du neant)",     (150, 0, 200)),
        ("7 - Boss 7 (Spheres)",             (180, 180, 180)),
        ("8 - Boss 8 (Leviathan)",           (100, 200, 255)),
        ("9 - Boss 9 (Void Phoenix)",        (180, 100, 255)),
        ("",                                 WHITE),
        ("ESC - Quitter",                    (100, 100, 100)),
    ]
    for i, (text, color) in enumerate(boss_items):
        if text:
            screen.blit(item_font.render(text, True, color),
                        (col1_x, start_y + 26 + i * spacing))

    # ── Colonne centrale : Ennemis batches 1-3 ──────────────────────
    col2_x = 265
    col2_label = item_font.render("[ ENNEMIS 1-3 ]", True, (60, 180, 60))
    screen.blit(col2_label, (col2_x, start_y))
    mid_items = [
        ("--- Anciens ---",           (120, 120, 120)),
        ("B - Basique",               (255, 80, 80)),
        ("A - Tireur",                (200, 80, 200)),
        ("0 - Tous anciens",          (160, 160, 160)),
        ("--- Nouveaux 1 ---",        (120, 120, 120)),
        ("C - Sniper",                (140, 0, 255)),
        ("D - Mine",                  (200, 100, 0)),
        ("E - Bouclier",              (0, 180, 255)),
        ("F - Fantome",               (180, 200, 255)),
        ("G - Kamikaze",              (255, 60, 0)),
        ("--- Nouveaux 2 ---",        (120, 120, 120)),
        ("H - Teleporteur",           (220, 0, 180)),
        ("I - Pulseur",               (0, 200, 255)),
        ("J - Miroir",                (200, 215, 225)),
        ("L - Rafale",                (240, 100, 0)),
        ("--- Nouveaux 3 ---",        (120, 120, 120)),
        ("M - Tournoyeur",            (0, 200, 180)),
        ("O - Orbital",               (100, 0, 150)),
        ("P - Drone Laser",           (220, 25, 25)),
        ("Q - Blinde",                (95, 105, 115)),
        ("R - Clonateur",             (195, 195, 45)),
    ]
    for i, (text, color) in enumerate(mid_items):
        if text:
            screen.blit(item_font.render(text, True, color),
                        (col2_x, start_y + 26 + i * spacing))

    # ── Colonne droite : Ennemis batches 4-6 + N ────────────────────
    col3_x = 530
    col3_label = item_font.render("[ ENNEMIS 4-6 ]", True, (60, 180, 180))
    screen.blit(col3_label, (col3_x, start_y))
    right_items = [
        ("--- Nouveaux 4 ---",        (120, 120, 120)),
        ("S - Soigneur",              (100, 220, 100)),
        ("T - Aimant",                (70, 100, 200)),
        ("U - Surcharge",             (255, 180, 0)),
        ("V - Sentinelle",            (80, 100, 200)),
        ("W - Echo",                  (210, 140, 220)),
        ("--- Nouveaux 5 ---",        (120, 120, 120)),
        ("K - Chargeur",              (255, 140, 0)),
        ("X - Ombre",                 (80, 130, 220)),
        ("Y - Draineur",              (160, 60, 255)),
        ("Z - Essaim",                (150, 255, 50)),
        (". - Grille",                (0, 220, 220)),
        ("--- Nouveaux 6 ---",        (120, 120, 120)),
        ("F1 - Glaceur",              (150, 220, 255)),
        ("F2 - Plongeur",             (220, 30, 30)),
        ("F3 - Dispersion",           (255, 150, 30)),
        ("F4 - Blindé lourd",         (140, 155, 165)),
        ("F5 - Mirage",               (200, 140, 255)),
        ("F6 - Faucheur",             (80, 220, 80)),
        ("F7 - Binome",               (255, 220, 0)),
        ("N  - Tous nouveaux",        (200, 200, 0)),
    ]
    for i, (text, color) in enumerate(right_items):
        if text:
            screen.blit(item_font.render(text, True, color),
                        (col3_x, start_y + 26 + i * spacing))

    pygame.display.flip()


def _spawn_enemies(entity_type):
    """Retourne la liste initiale d'ennemis pour un type donné."""
    enemies = []
    cx = SCREEN_WIDTH // 2

    if entity_type == "Boss 1":
        enemies.append(Boss(cx, -50))
    elif entity_type == "Boss 2":
        enemies.append(Boss2(cx, -70))
    elif entity_type == "Boss 3":
        enemies.append(Boss3(cx, -80))
    elif entity_type == "Boss 4":
        enemies.append(Boss4(cx, -90))
    elif entity_type == "Boss 5":
        enemies.append(Boss5(cx, -100))
    elif entity_type == "Boss 6":
        enemies.append(Boss6(cx, -110))
    elif entity_type == "Boss 7":
        enemies.append(Boss7(cx, -100))
    elif entity_type == "Boss 8":
        enemies.append(Boss8(cx, -120))
    elif entity_type == "Boss 9":
        enemies.append(Boss9(cx, -130))
    elif entity_type == "Ennemi basique":
        for i in range(5):
            enemies.append(Enemy(100 + i * 150, -20 - i * 30))
    elif entity_type == "Ennemi tireur":
        for i in range(3):
            enemies.append(ShootingEnemy(150 + i * 250, -20))
    elif entity_type == "Tous anciens":
        enemies.append(Enemy(200, -20))
        enemies.append(Enemy(400, -40))
        enemies.append(Enemy(600, -20))
        enemies.append(ShootingEnemy(300, -60))
        enemies.append(ShootingEnemy(500, -80))
    elif entity_type == "Sniper":
        for i in range(3):
            enemies.append(SniperEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Mine":
        for i in range(4):
            enemies.append(MineEnemy(120 + i * 185, -20 - i * 15))
    elif entity_type == "Bouclier":
        for i in range(3):
            enemies.append(ShieldEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Fantome":
        for i in range(3):
            enemies.append(GhostEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Kamikaze":
        for i in range(3):
            enemies.append(BomberEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Teleporteur":
        for i in range(3):
            enemies.append(TeleporterEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Pulseur":
        for i in range(3):
            enemies.append(PulseEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Miroir":
        for i in range(3):
            enemies.append(ReflectorEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Rafale":
        for i in range(3):
            enemies.append(BurstEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Tournoyeur":
        for i in range(3):
            enemies.append(SpinnerEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Orbital":
        for i in range(2):
            enemies.append(OrbiterEnemy(200 + i * 400, -40 - i * 30))
    elif entity_type == "Drone Laser":
        for i in range(2):
            enemies.append(LaserDroneEnemy(200 + i * 400, -60 - i * 30))
    elif entity_type == "Blindé":
        for i in range(3):
            enemies.append(ArmoredEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Clonateur":
        for i in range(2):
            enemies.append(ClonerEnemy(200 + i * 400, -40 - i * 30))
    elif entity_type == "Soigneur":
        for i in range(3):
            enemies.append(HealerEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Aimant":
        for i in range(2):
            enemies.append(MagnetEnemy(200 + i * 400, -40))
    elif entity_type == "Surchargé":
        for i in range(3):
            enemies.append(OverchargedEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Sentinelle":
        for i in range(3):
            enemies.append(SentinelEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Echo":
        for i in range(3):
            enemies.append(EchoEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Chargeur":
        for i in range(3):
            enemies.append(ChargerEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Ombre":
        for i in range(2):
            enemies.append(ShadowEnemy(200 + i * 400, -40))
    elif entity_type == "Draineur":
        for i in range(3):
            enemies.append(DrainerEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Essaim":
        for i in range(7):
            enemies.append(SwarmEnemy(80 + i * 100, -20 - i * 15))
    elif entity_type == "Grille":
        for i in range(3):
            enemies.append(GridEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Glaceur":
        for i in range(3):
            enemies.append(FreezerEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Plongeur":
        for i in range(4):
            enemies.append(DiveEnemy(100 + i * 200, -20 - i * 30))
    elif entity_type == "Dispersion":
        for i in range(3):
            enemies.append(ScatterEnemy(150 + i * 250, -30 - i * 20))
    elif entity_type == "Blindé lourd":
        enemies.append(AnchorEnemy(cx - 150, -40))
        enemies.append(AnchorEnemy(cx + 150, -60))
    elif entity_type == "Mirage":
        for i in range(2):
            enemies.append(MirageEnemy(200 + i * 400, -40))
    elif entity_type == "Faucheur":
        for i in range(3):
            enemies.append(RipperEnemy(100 + i * 280, -20 - i * 25))
    elif entity_type == "Binôme":
        for i in range(2):
            a = ChainEnemy(150 + i * 150, -20 - i * 20)
            b = ChainEnemy(450 + i * 100, -30 - i * 20)
            a.partner = b
            b.partner = a
            enemies.extend([a, b])
    elif entity_type == "Tous nouveaux":
        enemies.append(SniperEnemy(cx - 280, -20))
        enemies.append(MineEnemy(cx - 150, -20))
        enemies.append(MineEnemy(cx + 150, -20))
        enemies.append(ShieldEnemy(cx + 280, -30))
        enemies.append(GhostEnemy(cx - 250, -60))
        enemies.append(BomberEnemy(cx, -50))
        enemies.append(TeleporterEnemy(cx + 300, -80))
        enemies.append(PulseEnemy(cx - 100, -100))
        enemies.append(ReflectorEnemy(cx + 100, -100))
        enemies.append(BurstEnemy(cx - 320, -120))
        enemies.append(SpinnerEnemy(cx + 320, -120))
        enemies.append(OrbiterEnemy(cx, -150))
        enemies.append(LaserDroneEnemy(cx - 250, -160))
        enemies.append(ArmoredEnemy(cx + 250, -140))
        enemies.append(ClonerEnemy(cx, -200))
        enemies.append(HealerEnemy(cx - 200, -220))
        enemies.append(MagnetEnemy(cx + 200, -220))
        enemies.append(OverchargedEnemy(cx - 100, -240))
        enemies.append(SentinelEnemy(cx + 100, -240))
        enemies.append(EchoEnemy(cx, -260))
        enemies.append(ChargerEnemy(cx - 300, -280))
        enemies.append(ShadowEnemy(cx + 100, -300))
        enemies.append(DrainerEnemy(cx - 100, -300))
        for i in range(4):
            enemies.append(SwarmEnemy(cx - 180 + i * 120, -320 - i * 10))
        enemies.append(GridEnemy(cx, -360))
        enemies.append(FreezerEnemy(cx - 280, -380))
        enemies.append(DiveEnemy(cx + 280, -380))
        enemies.append(ScatterEnemy(cx - 150, -400))
        enemies.append(AnchorEnemy(cx + 150, -400))
        enemies.append(MirageEnemy(cx, -430))
        enemies.append(RipperEnemy(cx - 200, -450))
        a = ChainEnemy(cx + 100, -460)
        b = ChainEnemy(cx + 260, -460)
        a.partner = b
        b.partner = a
        enemies.extend([a, b])

    return enemies


def run_test(entity_type):
    """Lance le test avec l'entité spécifiée"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Test - {entity_type}")
    clock = pygame.time.Clock()

    background = Background(speed=0)
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    projectiles = []
    enemy_projectiles = []
    explosions = []
    enemies = _spawn_enemies(entity_type)
    combo = ComboSystem()

    running = True
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Retour au menu
                if event.key == pygame.K_r:
                    enemies.clear()
                    enemy_projectiles.clear()
                    enemies = _spawn_enemies(entity_type)
                if event.key == pygame.K_h:
                    player.hp = 10
                if event.key == pygame.K_k:
                    for e in enemies:
                        if hasattr(e, 'hp'):
                            e.hp = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(projectiles)

        # Updates
        background.update()
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        if keys[pygame.K_SPACE]:
            player.shoot(projectiles)

        for projectile in projectiles:
            projectile.update()
        projectiles = [p for p in projectiles if p.rect.bottom > 0]

        # Effet magnétique
        for enemy in enemies:
            if isinstance(enemy, MagnetEnemy):
                enemy.apply_magnet(projectiles)

        # Update ennemis
        for enemy in enemies[:]:
            if isinstance(enemy, Boss):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(5):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 100),
                            enemy.rect.top + random.randint(0, 100),
                            duration=500
                        ))
            elif isinstance(enemy, Boss2):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(8):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 120),
                            enemy.rect.top + random.randint(0, 120),
                            duration=600
                        ))
            elif isinstance(enemy, Boss3):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(12):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 140),
                            enemy.rect.top + random.randint(0, 140),
                            duration=700
                        ))
            elif isinstance(enemy, Boss4):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(20):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 160),
                            enemy.rect.top + random.randint(0, 160),
                            duration=800
                        ))
            elif isinstance(enemy, Boss5):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(30):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 180),
                            enemy.rect.top + random.randint(0, 180),
                            duration=1000
                        ))
            elif isinstance(enemy, Boss6):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(40):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 200),
                            enemy.rect.top + random.randint(0, 200),
                            duration=1200
                        ))
            elif isinstance(enemy, Boss7):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(45):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 180),
                            enemy.rect.top + random.randint(0, 180),
                            duration=1300
                        ))
            elif isinstance(enemy, Boss8):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(60):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 200),
                            enemy.rect.top + random.randint(0, 200),
                            duration=1500
                        ))
            elif isinstance(enemy, Boss9):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    enemies.remove(enemy)
                    for _ in range(70):
                        explosions.append(Explosion(
                            enemy.rect.left + random.randint(0, 220),
                            enemy.rect.top + random.randint(0, 220),
                            duration=1800
                        ))
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, SniperEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, GhostEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, BomberEnemy):
                enemy.update_with_player(player.rect.center)
            elif isinstance(enemy, TeleporterEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, PulseEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, BurstEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, SpinnerEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, OrbiterEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, HealerEnemy):
                enemy.update(enemies)
            elif isinstance(enemy, OverchargedEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, SentinelEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, ChargerEnemy):
                enemy.update(player.rect.center)
            elif isinstance(enemy, ShadowEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, SwarmEnemy):
                enemy.update(player.rect.center)
            elif isinstance(enemy, GridEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, DiveEnemy):
                enemy.update(player.rect.center)
            elif isinstance(enemy, ScatterEnemy):
                enemy.update(player.rect.center, enemy_projectiles)
            elif isinstance(enemy, FreezerEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, AnchorEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, RipperEnemy):
                enemy.update(enemy_projectiles)
            elif isinstance(enemy, ChainEnemy):
                enemy.update(enemy_projectiles)
            else:
                # MineEnemy, ShieldEnemy, ReflectorEnemy, LaserDroneEnemy,
                # ArmoredEnemy, ClonerEnemy, MagnetEnemy, EchoEnemy,
                # DrainerEnemy, MirageEnemy, Enemy de base
                enemy.update()

        # ClonerEnemy - génération des décoys
        new_clones = []
        for enemy in enemies:
            if isinstance(enemy, ClonerEnemy) and not enemy.is_decoy and not enemy.has_cloned:
                if enemy.timer >= enemy.clone_delay:
                    new_clones.append(enemy.clone())
                    enemy.has_cloned = True
        enemies.extend(new_clones)

        # MirageEnemy - génération des mirages
        new_mirages = []
        for enemy in enemies:
            if isinstance(enemy, MirageEnemy) and not enemy.is_mirage and not enemy.has_spawned:
                if enemy.timer >= enemy.spawn_delay:
                    new_mirages.extend(enemy.get_mirages())
                    enemy.has_spawned = True
        enemies.extend(new_mirages)

        # Collision Kamikaze -> joueur (dès qu'il est en dash)
        for enemy in enemies[:]:
            if isinstance(enemy, BomberEnemy) and enemy.is_dashing:
                if enemy.rect.colliderect(player.rect) and not player.invulnerable:
                    for proj in enemy.explode():
                        enemy_projectiles.append(proj)
                    for _ in range(6):
                        explosions.append(Explosion(
                            enemy.rect.centerx + random.randint(-20, 20),
                            enemy.rect.centery + random.randint(-20, 20),
                            duration=400
                        ))
                    try:
                        enemies.remove(enemy)
                    except ValueError:
                        pass
                    player.hp -= 2
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()

        # Collision ChargerEnemy en charge -> joueur
        for enemy in enemies[:]:
            if isinstance(enemy, ChargerEnemy) and enemy.is_charging and not player.invulnerable:
                if enemy.rect.colliderect(player.rect):
                    player.hp -= 1
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()

        # Collision DiveEnemy en plongée -> joueur
        for enemy in enemies[:]:
            if isinstance(enemy, DiveEnemy) and enemy.is_diving and not player.invulnerable:
                if enemy.rect.colliderect(player.rect):
                    player.hp -= 1
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery,
                                                duration=300))
                    try:
                        enemies.remove(enemy)
                    except ValueError:
                        pass

        # Collision SwarmEnemy au contact -> joueur
        for enemy in enemies[:]:
            if isinstance(enemy, SwarmEnemy) and not player.invulnerable:
                if enemy.rect.colliderect(player.rect):
                    player.hp -= 1
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery,
                                                duration=300))
                    try:
                        enemies.remove(enemy)
                    except ValueError:
                        pass

        # Supprimer les ennemis hors écran (sauf boss et sentinelles)
        boss_types = (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8, Boss9)
        enemies = [
            e for e in enemies
            if e.rect.top < SCREEN_HEIGHT
            or isinstance(e, boss_types)
            or isinstance(e, (SentinelEnemy, ShadowEnemy, GridEnemy))
        ]

        # Update projectiles ennemis
        enemy_projectiles = manage_enemy_projectiles(enemy_projectiles, player.rect.center)

        # Collision laser LaserDroneEnemy -> joueur
        for enemy in enemies:
            if isinstance(enemy, LaserDroneEnemy) and enemy.laser_active and not player.invulnerable:
                if enemy.get_laser_rect().colliderect(player.rect):
                    player.hp -= 1
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()

        # Collisions projectiles joueur -> ennemis
        for projectile in projectiles[:]:
            for enemy in enemies[:]:
                # Orbes de l'OrbiterEnemy (peuvent être hors du rect principal)
                if isinstance(enemy, OrbiterEnemy):
                    orb_hit = False
                    for orb_rect in enemy.get_orb_rects():
                        if projectile.rect.colliderect(orb_rect):
                            try:
                                projectiles.remove(projectile)
                            except ValueError:
                                pass
                            explosions.append(Explosion(orb_rect.centerx, orb_rect.centery))
                            orb_hit = True
                            break
                    if orb_hit:
                        break

                if not projectile.rect.colliderect(enemy.rect):
                    continue
                if isinstance(enemy, boss_types) and enemy.is_dying:
                    continue

                # Bouclier bloque le tir
                if isinstance(enemy, ShieldEnemy) and enemy.is_blocked_by_shield(projectile.rect):
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    explosions.append(Explosion(projectile.rect.centerx, projectile.rect.centery))
                    break

                # Miroir réfléchit le tir vers le bas
                if isinstance(enemy, ReflectorEnemy) and enemy.is_reflected(projectile.rect):
                    ex, ey = projectile.rect.center
                    enemy_projectiles.append(EnemyProjectile(ex, ey, 0, 1, speed=7))
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    explosions.append(Explosion(ex, ey))
                    break

                # Fantôme invincible quand invisible
                if isinstance(enemy, GhostEnemy) and enemy.is_invisible():
                    continue

                try:
                    projectiles.remove(projectile)
                except ValueError:
                    pass

                combo.hit()

                if isinstance(enemy, boss_types):
                    enemy.take_damage(1)
                    if enemy.hp <= 0 and not enemy.is_dying:
                        enemy.is_dying = True
                elif isinstance(enemy, DrainerEnemy):
                    # Absorbe le projectile et tire en retour si chargé
                    died = enemy.absorb_hit(player.rect.center, enemy_projectiles)
                    if died:
                        try:
                            enemies.remove(enemy)
                        except ValueError:
                            pass
                elif isinstance(enemy, ArmoredEnemy):
                    # Blindage absorbe les impacts en priorité
                    died = enemy.take_hit()
                    if died:
                        try:
                            enemies.remove(enemy)
                        except ValueError:
                            pass
                else:
                    enemy.hp -= 1
                    # EchoEnemy riposte à chaque impact
                    if isinstance(enemy, EchoEnemy):
                        enemy.on_hit(player.rect.center, enemy_projectiles)
                    if enemy.hp <= 0:
                        # Explosion au décès pour Mine et Kamikaze
                        if isinstance(enemy, (MineEnemy, BomberEnemy)):
                            for proj in enemy.explode():
                                enemy_projectiles.append(proj)
                        # Réaction en chaîne ChainEnemy
                        if isinstance(enemy, ChainEnemy) and enemy.partner is not None:
                            if enemy.partner in enemies:
                                enemy.partner.chain_explode(enemy_projectiles)
                                explosions.append(Explosion(
                                    enemy.partner.rect.centerx,
                                    enemy.partner.rect.centery, duration=400))
                                try:
                                    enemies.remove(enemy.partner)
                                except ValueError:
                                    pass
                        try:
                            enemies.remove(enemy)
                        except ValueError:
                            pass

                explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                break

        # Collisions projectiles ennemis -> joueur
        for e_proj in enemy_projectiles[:]:
            if e_proj.rect.colliderect(player.rect):
                try:
                    enemy_projectiles.remove(e_proj)
                except ValueError:
                    pass
                if not player.invulnerable:
                    player.hp -= 1
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()

        # Collision laser Boss 3
        for enemy in enemies:
            if isinstance(enemy, Boss3) and enemy.laser_active and not player.invulnerable:
                laser_rect = pygame.Rect(enemy.laser_target_x - 25, 0, 50, SCREEN_HEIGHT)
                if player.rect.colliderect(laser_rect):
                    player.hp -= 2
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()

        # Collision charge Boss 4
        for enemy in enemies:
            if isinstance(enemy, Boss4) and enemy.charging and not player.invulnerable:
                if enemy.rect.colliderect(player.rect):
                    player.hp -= 3
                    if player.hp <= 0:
                        player.hp = 10
                    player.invulnerable = True
                    player.invuln_start = pygame.time.get_ticks()

        # Update explosions
        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if not exp.is_finished()]

        combo.update()

        # Rendu
        screen.fill(BLACK)
        background.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        for projectile in projectiles:
            projectile.draw(screen)

        for e_proj in enemy_projectiles:
            e_proj.draw(screen)

        player.draw(screen)

        for exp in explosions:
            exp.draw(screen)

        # UI
        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 10))

        entity_text = font.render(f"Test: {entity_type}", True, YELLOW)
        screen.blit(entity_text, (10, 50))

        # Info ennemis spéciaux actifs
        ghost_count = sum(1 for e in enemies if isinstance(e, GhostEnemy) and not e.is_invisible())
        if ghost_count > 0 or any(isinstance(e, GhostEnemy) for e in enemies):
            ghost_info = small_font.render(
                f"Fantomes: {sum(1 for e in enemies if isinstance(e, GhostEnemy))} "
                f"(visibles: {ghost_count})", True, (180, 200, 255)
            )
            screen.blit(ghost_info, (10, 85))

        # Afficher HP du boss et pattern si présent
        for enemy in enemies:
            if isinstance(enemy, boss_types):
                boss_hp = font.render(f"Boss HP: {enemy.hp}", True, (255, 100, 100))
                screen.blit(boss_hp, (10, 90))

                pattern_name = get_pattern_name(enemy)
                if isinstance(enemy, Boss6):
                    pattern_num = enemy.pattern
                elif isinstance(enemy, Boss7):
                    pattern_num = enemy.pattern_index
                else:
                    pattern_num = getattr(enemy, 'current_pattern', 0)
                pattern_text = font.render(f"Pattern: {pattern_num} - {pattern_name}", True, (100, 200, 255))
                screen.blit(pattern_text, (10, 130))

                if isinstance(enemy, Boss5) and enemy.rage_mode:
                    screen.blit(font.render("MODE RAGE!", True, (255, 50, 50)), (10, 170))
                elif isinstance(enemy, Boss6) and enemy.fury_mode:
                    screen.blit(font.render("MODE FUREUR!", True, (200, 50, 255)), (10, 170))
                elif isinstance(enemy, Boss6) and enemy.black_hole_active:
                    screen.blit(font.render("TROU NOIR ACTIF", True, (150, 0, 200)), (10, 170))
                elif isinstance(enemy, Boss8) and enemy.shattered_mode:
                    screen.blit(font.render("MODE SHATTERED!", True, (255, 100, 50)), (10, 170))
                elif isinstance(enemy, Boss8) and enemy.shield_active:
                    screen.blit(font.render("BOUCLIER CRISTALLIN", True, (100, 200, 255)), (10, 170))
                elif isinstance(enemy, Boss9) and enemy.rebirth_mode:
                    screen.blit(font.render("MODE RENAISSANCE!", True, (255, 150, 50)), (10, 170))
                elif isinstance(enemy, Boss9) and enemy.rebirth_transition:
                    screen.blit(font.render("TRANSITION...", True, (255, 200, 100)), (10, 170))
                break

        # Instructions
        instr = small_font.render("ESC: Menu | R: Respawn | H: Heal | K: Kill (1 HP) | ESPACE: Tir auto", True, (150, 150, 150))
        screen.blit(instr, (10, SCREEN_HEIGHT - 25))

        combo.draw(screen, font)

        pygame.display.flip()
        clock.tick(FPS)

    return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test des Entités - Menu")
    font = pygame.font.SysFont(None, 48)

    running = True
    while running:
        show_menu(screen, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    if not run_test("Boss 1"):
                        running = False
                elif event.key == pygame.K_2:
                    if not run_test("Boss 2"):
                        running = False
                elif event.key == pygame.K_3:
                    if not run_test("Boss 3"):
                        running = False
                elif event.key == pygame.K_4:
                    if not run_test("Boss 4"):
                        running = False
                elif event.key == pygame.K_5:
                    if not run_test("Boss 5"):
                        running = False
                elif event.key == pygame.K_6:
                    if not run_test("Boss 6"):
                        running = False
                elif event.key == pygame.K_7:
                    if not run_test("Boss 7"):
                        running = False
                elif event.key == pygame.K_8:
                    if not run_test("Boss 8"):
                        running = False
                elif event.key == pygame.K_9:
                    if not run_test("Boss 9"):
                        running = False
                elif event.key == pygame.K_b:
                    if not run_test("Ennemi basique"):
                        running = False
                elif event.key == pygame.K_a:
                    if not run_test("Ennemi tireur"):
                        running = False
                elif event.key == pygame.K_0:
                    if not run_test("Tous anciens"):
                        running = False
                # Nouveaux ennemis
                elif event.key == pygame.K_c:
                    if not run_test("Sniper"):
                        running = False
                elif event.key == pygame.K_d:
                    if not run_test("Mine"):
                        running = False
                elif event.key == pygame.K_e:
                    if not run_test("Bouclier"):
                        running = False
                elif event.key == pygame.K_f:
                    if not run_test("Fantome"):
                        running = False
                elif event.key == pygame.K_g:
                    if not run_test("Kamikaze"):
                        running = False
                elif event.key == pygame.K_h:
                    if not run_test("Teleporteur"):
                        running = False
                elif event.key == pygame.K_i:
                    if not run_test("Pulseur"):
                        running = False
                elif event.key == pygame.K_j:
                    if not run_test("Miroir"):
                        running = False
                elif event.key == pygame.K_l:
                    if not run_test("Rafale"):
                        running = False
                elif event.key == pygame.K_m:
                    if not run_test("Tournoyeur"):
                        running = False
                elif event.key == pygame.K_o:
                    if not run_test("Orbital"):
                        running = False
                elif event.key == pygame.K_p:
                    if not run_test("Drone Laser"):
                        running = False
                elif event.key == pygame.K_q:
                    if not run_test("Blindé"):
                        running = False
                elif event.key == pygame.K_r:
                    if not run_test("Clonateur"):
                        running = False
                elif event.key == pygame.K_n:
                    if not run_test("Tous nouveaux"):
                        running = False
                elif event.key == pygame.K_s:
                    if not run_test("Soigneur"):
                        running = False
                elif event.key == pygame.K_t:
                    if not run_test("Aimant"):
                        running = False
                elif event.key == pygame.K_u:
                    if not run_test("Surchargé"):
                        running = False
                elif event.key == pygame.K_v:
                    if not run_test("Sentinelle"):
                        running = False
                elif event.key == pygame.K_w:
                    if not run_test("Echo"):
                        running = False
                elif event.key == pygame.K_k:
                    if not run_test("Chargeur"):
                        running = False
                elif event.key == pygame.K_x:
                    if not run_test("Ombre"):
                        running = False
                elif event.key == pygame.K_y:
                    if not run_test("Draineur"):
                        running = False
                elif event.key == pygame.K_z:
                    if not run_test("Essaim"):
                        running = False
                elif event.key == pygame.K_PERIOD:
                    if not run_test("Grille"):
                        running = False
                elif event.key == pygame.K_F1:
                    if not run_test("Glaceur"):
                        running = False
                elif event.key == pygame.K_F2:
                    if not run_test("Plongeur"):
                        running = False
                elif event.key == pygame.K_F3:
                    if not run_test("Dispersion"):
                        running = False
                elif event.key == pygame.K_F4:
                    if not run_test("Blindé lourd"):
                        running = False
                elif event.key == pygame.K_F5:
                    if not run_test("Mirage"):
                        running = False
                elif event.key == pygame.K_F6:
                    if not run_test("Faucheur"):
                        running = False
                elif event.key == pygame.K_F7:
                    if not run_test("Binôme"):
                        running = False

    pygame.quit()


if __name__ == "__main__":
    main()
