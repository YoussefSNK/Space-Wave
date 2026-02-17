"""
Zone de test pour tester les power-ups du joueur.
Permet d'acquérir les power-ups en se déplaçant sur des carrés,
de tester contre des vagues d'ennemis, et de supprimer les pouvoirs actuels.
"""

import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, CYAN
from entities.player import Player
from entities.enemy import Enemy
from entities.projectiles import RicochetProjectile, MissileProjectile
from graphics.background import Background
from graphics.effects import Explosion


class PowerUpZone:
    """Carré cliquable qui donne un power-up au joueur"""
    def __init__(self, x, y, power_type, color, label):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.power_type = power_type
        self.color = color
        self.label = label
        self.hover = False

    def check_collision(self, player_rect):
        """Vérifie si le joueur touche ce carré"""
        return self.rect.colliderect(player_rect)

    def draw(self, surface, font):
        # Bordure plus épaisse si hover
        border_width = 4 if self.hover else 2
        pygame.draw.rect(surface, self.color, self.rect, border_width)

        # Remplissage semi-transparent
        s = pygame.Surface((self.rect.width - 8, self.rect.height - 8), pygame.SRCALPHA)
        s.fill((*self.color, 60))
        surface.blit(s, (self.rect.x + 4, self.rect.y + 4))

        # Label
        text = font.render(self.label, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


class ClearPowerZone:
    """Carré qui supprime les power-ups actuels"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.color = (255, 50, 50)  # Rouge
        self.label = "CLEAR"
        self.hover = False

    def check_collision(self, player_rect):
        """Vérifie si le joueur touche ce carré"""
        return self.rect.colliderect(player_rect)

    def draw(self, surface, font):
        # Bordure plus épaisse si hover
        border_width = 4 if self.hover else 2
        pygame.draw.rect(surface, self.color, self.rect, border_width)

        # Remplissage semi-transparent
        s = pygame.Surface((self.rect.width - 8, self.rect.height - 8), pygame.SRCALPHA)
        s.fill((*self.color, 60))
        surface.blit(s, (self.rect.x + 4, self.rect.y + 4))

        # Label
        text = font.render(self.label, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


def run_powerup_test():
    """Lance la zone de test des power-ups"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test - Power-ups")
    clock = pygame.time.Clock()

    background = Background(speed=0)  # Fond statique
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    projectiles = []
    enemies = []
    explosions = []

    # Créer les zones de power-ups en grille
    powerup_zones = [
        PowerUpZone(50, 50, 'double', CYAN, 'DOUBLE'),
        PowerUpZone(170, 50, 'triple', (255, 0, 255), 'TRIPLE'),
        PowerUpZone(290, 50, 'spread', (0, 255, 100), 'SPREAD'),
        PowerUpZone(410, 50, 'ricochet', (255, 100, 0), 'RICOCHET'),
        PowerUpZone(530, 50, 'zigzag', (255, 0, 200), 'ZIGZAG'),
        PowerUpZone(650, 50, 'missile', (255, 80, 0), 'MISSILE'),
    ]

    # Zone pour supprimer les power-ups
    clear_zone = ClearPowerZone(50, 170)

    # Système de spawn d'ennemis
    last_spawn_time = pygame.time.get_ticks()
    spawn_interval = 5000  # 5 secondes

    running = True
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_h:
                    # Heal le joueur
                    player.hp = 10
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(projectiles)

        # Gérer les déplacements clavier
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # Tir automatique si espace est maintenu
        if keys[pygame.K_SPACE]:
            player.shoot(projectiles)

        # Vérifier les collisions avec les zones de power-up
        for zone in powerup_zones:
            zone.hover = False
            if zone.check_collision(player.rect):
                zone.hover = True
                # Appliquer le power-up
                if player.power_type != zone.power_type:
                    player.apply_powerup(zone.power_type)

        # Vérifier collision avec la zone de clear
        clear_zone.hover = False
        if clear_zone.check_collision(player.rect):
            clear_zone.hover = True
            # Supprimer le power-up
            if player.power_type != 'normal':
                player.power_type = 'normal'
                print("Power-ups supprimés!")

        # Spawn de vagues d'ennemis toutes les 5 secondes
        now = pygame.time.get_ticks()
        if now - last_spawn_time >= spawn_interval:
            last_spawn_time = now
            # Créer une vague de 5 ennemis basiques
            for i in range(5):
                x = 100 + i * 150
                y = -20 - i * 30  # Décalés verticalement
                enemies.append(Enemy(x, y))
            print(f"Vague d'ennemis spawned! Total: {len(enemies)}")

        # Update projectiles
        for projectile in projectiles:
            projectile.update()
        projectiles = [p for p in projectiles if p.rect.bottom > 0]

        # Update ennemis
        for enemy in enemies:
            enemy.update()

        # Supprimer les ennemis hors écran
        enemies = [e for e in enemies if e.rect.top < SCREEN_HEIGHT]

        # Collisions projectiles -> ennemis
        for projectile in projectiles[:]:
            for enemy in enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    # Gérer le missile : explosion AOE au point d'impact
                    if isinstance(projectile, MissileProjectile):
                        impact_x, impact_y = projectile.rect.centerx, projectile.rect.centery
                        try:
                            projectiles.remove(projectile)
                        except ValueError:
                            pass
                        explosions.append(Explosion(impact_x, impact_y))
                        # Dégâts AOE à tous les ennemis dans le rayon
                        for aoe_enemy in enemies[:]:
                            dx = aoe_enemy.rect.centerx - impact_x
                            dy = aoe_enemy.rect.centery - impact_y
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist <= projectile.aoe_radius:
                                aoe_enemy.hp -= projectile.aoe_damage
                                if aoe_enemy.hp <= 0 and aoe_enemy in enemies:
                                    enemies.remove(aoe_enemy)
                                    explosions.append(Explosion(aoe_enemy.rect.centerx, aoe_enemy.rect.centery))
                    # Gérer le ricochet : le projectile rebondit au lieu d'être détruit
                    elif isinstance(projectile, RicochetProjectile):
                        can_continue = projectile.ricochet()
                        if not can_continue:
                            try:
                                projectiles.remove(projectile)
                            except ValueError:
                                pass
                        enemy.hp -= 1
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                            explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    else:
                        try:
                            projectiles.remove(projectile)
                        except ValueError:
                            pass
                        enemy.hp -= 1
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                            explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    break

        # Collisions ennemis -> joueur
        for enemy in enemies[:]:
            if enemy.rect.colliderect(player.rect) and not player.invulnerable:
                player.hp -= 1
                if player.hp <= 0:
                    player.hp = 10  # Auto-heal en mode test
                player.invulnerable = True
                player.invuln_start = pygame.time.get_ticks()
                enemies.remove(enemy)
                explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))

        # Update explosions
        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if not exp.is_finished()]

        # Rendu
        screen.fill(BLACK)
        background.draw(screen)

        # Dessiner les zones de power-up
        for zone in powerup_zones:
            zone.draw(screen, font)

        # Dessiner la zone de clear
        clear_zone.draw(screen, font)

        # Dessiner les ennemis
        for enemy in enemies:
            enemy.draw(screen)

        # Dessiner les projectiles
        for projectile in projectiles:
            projectile.draw(screen)

        # Dessiner le joueur
        player.draw(screen)

        # Dessiner les explosions
        for exp in explosions:
            exp.draw(screen)

        # UI
        hp_text = title_font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 200))

        power_text = title_font.render(f"Power: {player.power_type.upper()}", True, CYAN)
        screen.blit(power_text, (10, 240))

        enemy_count = title_font.render(f"Ennemis: {len(enemies)}", True, (255, 100, 100))
        screen.blit(enemy_count, (10, 280))

        # Instructions
        instructions = [
            "Déplacez-vous sur les carrés pour acquérir des power-ups",
            "Carrés de power-up en haut: DOUBLE, TRIPLE, SPREAD, RICOCHET, ZIGZAG, MISSILE",
            "Carré rouge (CLEAR): supprime les power-ups actuels",
            "Vagues de 5 ennemis toutes les 5 secondes",
            "",
            "ESPACE: Tirer | H: Heal | ESC: Quitter"
        ]

        for i, instr in enumerate(instructions):
            text = font.render(instr, True, (150, 150, 150))
            screen.blit(text, (10, SCREEN_HEIGHT - 150 + i * 25))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def main():
    run_powerup_test()


if __name__ == "__main__":
    main()
