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
from entities.enemy import Enemy, ShootingEnemy
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
    """Affiche le menu de sélection"""
    options = [
        "1 - Boss 1 (Miedd)",
        "2 - Boss 2 (Hexagone violet)",
        "3 - Boss 3 (Diamant cyan)",
        "4 - Boss 4 (Soleil doré)",
        "5 - Boss 5 (Oeil du chaos)",
        "6 - Boss 6 (Vortex du néant)",
        "7 - Boss 7 (Maitre des spheres)",
        "8 - Boss 8 (Leviathan cristallin)",
        "9 - Boss 9 (Void Phoenix)",
        "B - Ennemi basique",
        "A - Ennemi tireur",
        "0 - Tous les ennemis",
        "",
        "ESC - Quitter"
    ]

    screen.fill(BLACK)
    title = font.render("TEST DES ENTITES", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    subtitle = font.render("Choisissez une entité à tester:", True, WHITE)
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 180))

    for i, option in enumerate(options):
        color = WHITE if option else BLACK
        if "Boss 1" in option:
            color = (255, 100, 100)
        elif "Boss 2" in option:
            color = (150, 0, 255)
        elif "Boss 3" in option:
            color = (0, 255, 255)
        elif "Boss 4" in option:
            color = (255, 215, 0)
        elif "Boss 5" in option:
            color = (0, 255, 100)
        elif "Boss 6" in option:
            color = (150, 0, 200)
        elif "Boss 7" in option:
            color = (180, 180, 180)
        elif "Boss 8" in option:
            color = (100, 200, 255)
        elif "Boss 9" in option:
            color = (180, 100, 255)

        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 50))

    pygame.display.flip()


def run_test(entity_type):
    """Lance le test avec l'entité spécifiée"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Test - {entity_type}")
    clock = pygame.time.Clock()

    background = Background(speed=0)  # Fond statique pour les boss
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    projectiles = []
    enemy_projectiles = []
    explosions = []
    enemies = []
    combo = ComboSystem()

    # Créer l'entité à tester
    if entity_type == "Boss 1":
        enemy = Boss(SCREEN_WIDTH // 2, -50)
        enemies.append(enemy)
    elif entity_type == "Boss 2":
        enemy = Boss2(SCREEN_WIDTH // 2, -70)
        enemies.append(enemy)
    elif entity_type == "Boss 3":
        enemy = Boss3(SCREEN_WIDTH // 2, -80)
        enemies.append(enemy)
    elif entity_type == "Boss 4":
        enemy = Boss4(SCREEN_WIDTH // 2, -90)
        enemies.append(enemy)
    elif entity_type == "Boss 5":
        enemy = Boss5(SCREEN_WIDTH // 2, -100)
        enemies.append(enemy)
    elif entity_type == "Boss 6":
        enemy = Boss6(SCREEN_WIDTH // 2, -110)
        enemies.append(enemy)
    elif entity_type == "Boss 7":
        enemy = Boss7(SCREEN_WIDTH // 2, -100)
        enemies.append(enemy)
    elif entity_type == "Boss 8":
        enemy = Boss8(SCREEN_WIDTH // 2, -120)
        enemies.append(enemy)
    elif entity_type == "Boss 9":
        enemy = Boss9(SCREEN_WIDTH // 2, -130)
        enemies.append(enemy)
    elif entity_type == "Ennemi basique":
        for i in range(5):
            e = Enemy(100 + i * 150, -20 - i * 30)
            enemies.append(e)
    elif entity_type == "Ennemi tireur":
        for i in range(3):
            e = ShootingEnemy(150 + i * 250, -20)
            enemies.append(e)
    elif entity_type == "Tous les ennemis":
        enemies.append(Enemy(200, -20))
        enemies.append(Enemy(400, -40))
        enemies.append(Enemy(600, -20))
        enemies.append(ShootingEnemy(300, -60))
        enemies.append(ShootingEnemy(500, -80))

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
                    # Respawn l'entité
                    enemies.clear()
                    enemy_projectiles.clear()
                    if entity_type == "Boss 1":
                        enemies.append(Boss(SCREEN_WIDTH // 2, -50))
                    elif entity_type == "Boss 2":
                        enemies.append(Boss2(SCREEN_WIDTH // 2, -70))
                    elif entity_type == "Boss 3":
                        enemies.append(Boss3(SCREEN_WIDTH // 2, -80))
                    elif entity_type == "Boss 4":
                        enemies.append(Boss4(SCREEN_WIDTH // 2, -90))
                    elif entity_type == "Boss 5":
                        enemies.append(Boss5(SCREEN_WIDTH // 2, -100))
                    elif entity_type == "Boss 6":
                        enemies.append(Boss6(SCREEN_WIDTH // 2, -110))
                    elif entity_type == "Boss 7":
                        enemies.append(Boss7(SCREEN_WIDTH // 2, -100))
                    elif entity_type == "Boss 8":
                        enemies.append(Boss8(SCREEN_WIDTH // 2, -120))
                    elif entity_type == "Boss 9":
                        enemies.append(Boss9(SCREEN_WIDTH // 2, -130))
                    elif entity_type == "Ennemi basique":
                        for i in range(5):
                            enemies.append(Enemy(100 + i * 150, -20 - i * 30))
                    elif entity_type == "Ennemi tireur":
                        for i in range(3):
                            enemies.append(ShootingEnemy(150 + i * 250, -20))
                    elif entity_type == "Tous les ennemis":
                        enemies.append(Enemy(200, -20))
                        enemies.append(Enemy(400, -40))
                        enemies.append(Enemy(600, -20))
                        enemies.append(ShootingEnemy(300, -60))
                        enemies.append(ShootingEnemy(500, -80))
                if event.key == pygame.K_h:
                    # Heal le joueur
                    player.hp = 10
                if event.key == pygame.K_k:
                    # Kill tous les ennemis (pour tester la mort)
                    for e in enemies:
                        if hasattr(e, 'hp'):
                            e.hp = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(projectiles)

        # Updates
        background.update()

        # Gérer les déplacements clavier
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # Tir automatique si espace est maintenu
        if keys[pygame.K_SPACE]:
            player.shoot(projectiles)

        for projectile in projectiles:
            projectile.update()
        projectiles = [p for p in projectiles if p.rect.bottom > 0]

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
            else:
                enemy.update()

        # Supprimer les ennemis hors écran (sauf boss)
        enemies = [e for e in enemies if e.rect.top < SCREEN_HEIGHT or isinstance(e, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8, Boss9))]

        # Update projectiles ennemis avec le gestionnaire centralisé
        enemy_projectiles = manage_enemy_projectiles(enemy_projectiles, player.rect.center)

        # Collisions projectiles joueur -> ennemis
        for projectile in projectiles[:]:
            for enemy in enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8, Boss9)) and enemy.is_dying:
                        continue
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    combo.hit()
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8, Boss9)):
                        enemy.take_damage(1)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                    else:
                        enemy.hp -= 1
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
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
                        player.hp = 10  # Auto-heal en mode test
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

        # Afficher HP du boss et pattern si présent
        for enemy in enemies:
            if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8, Boss9)):
                boss_hp = font.render(f"Boss HP: {enemy.hp}", True, (255, 100, 100))
                screen.blit(boss_hp, (10, 90))

                # Afficher le pattern actuel
                pattern_name = get_pattern_name(enemy)
                if isinstance(enemy, Boss6):
                    pattern_num = enemy.pattern
                elif isinstance(enemy, Boss7):
                    pattern_num = enemy.pattern_index
                else:
                    pattern_num = getattr(enemy, 'current_pattern', 0)
                pattern_text = font.render(f"Pattern: {pattern_num} - {pattern_name}", True, (100, 200, 255))
                screen.blit(pattern_text, (10, 130))

                # Afficher modes spéciaux si actifs
                if isinstance(enemy, Boss5) and enemy.rage_mode:
                    rage_text = font.render("MODE RAGE!", True, (255, 50, 50))
                    screen.blit(rage_text, (10, 170))
                elif isinstance(enemy, Boss6) and enemy.fury_mode:
                    fury_text = font.render("MODE FUREUR!", True, (200, 50, 255))
                    screen.blit(fury_text, (10, 170))
                elif isinstance(enemy, Boss6) and enemy.black_hole_active:
                    bh_text = font.render("TROU NOIR ACTIF", True, (150, 0, 200))
                    screen.blit(bh_text, (10, 170))
                elif isinstance(enemy, Boss8) and enemy.shattered_mode:
                    shattered_text = font.render("MODE SHATTERED!", True, (255, 100, 50))
                    screen.blit(shattered_text, (10, 170))
                elif isinstance(enemy, Boss8) and enemy.shield_active:
                    shield_text = font.render("BOUCLIER CRISTALLIN", True, (100, 200, 255))
                    screen.blit(shield_text, (10, 170))
                elif isinstance(enemy, Boss9) and enemy.rebirth_mode:
                    rebirth_text = font.render("MODE RENAISSANCE!", True, (255, 150, 50))
                    screen.blit(rebirth_text, (10, 170))
                elif isinstance(enemy, Boss9) and enemy.rebirth_transition:
                    trans_text = font.render("TRANSITION...", True, (255, 200, 100))
                    screen.blit(trans_text, (10, 170))
                break

        # Instructions
        instructions = [
            "ESC: Menu | R: Respawn | H: Heal | K: Kill (1 HP)"
        ]
        for i, instr in enumerate(instructions):
            text = small_font.render(instr, True, (150, 150, 150))
            screen.blit(text, (10, SCREEN_HEIGHT - 30 - i * 20))

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
                    if not run_test("Tous les ennemis"):
                        running = False

    pygame.quit()


if __name__ == "__main__":
    main()
