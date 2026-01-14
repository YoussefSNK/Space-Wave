import pygame
import random
from screens.base import Screen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE
from systems.level import Level
from systems.combo import ComboSystem
from entities.player import Player
from entities.powerup import PowerUp
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6
from entities.enemy import ShootingEnemy
from entities.projectiles import HomingProjectile, SplittingProjectile, MirrorProjectile, BlackHoleProjectile, PulseWaveProjectile, RicochetProjectile
from graphics.effects import Explosion


class GameScreen(Screen):
    """Écran de jeu principal."""

    def __init__(self, screen, level_num=1):
        super().__init__(screen)
        self.level_num = level_num
        self.game_over = False
        self.victory = False
        self.paused = False

        # Initialisation du jeu
        self.level = Level()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.projectiles = []
        self.enemy_projectiles = []
        self.explosions = []
        self.powerups = []
        self.combo = ComboSystem()
        self.font = pygame.font.SysFont(None, 36)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            if self.game_over or self.victory:
                self.next_screen = "menu"
                self.running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not self.game_over and not self.victory:
                    self.paused = not self.paused

    def update(self):
        if self.paused or self.game_over or self.victory:
            return

        # Gestion des inputs clavier
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # Tir avec Espace ou clic souris
        if self.player.wants_to_shoot or pygame.mouse.get_pressed()[0]:
            self.player.shoot(self.projectiles)

        self.level.update()
        self.player.update()

        for projectile in self.projectiles:
            projectile.update()

        # Détecter les tirs qui quittent l'écran sans toucher
        projectiles_avant = len(self.projectiles)
        self.projectiles = [p for p in self.projectiles if p.rect.bottom > 0]
        tirs_rates = projectiles_avant - len(self.projectiles)
        if tirs_rates > 0:
            self.combo.miss()

        self._update_enemies()
        self._update_enemy_projectiles()
        self._check_projectile_collisions()
        self._check_enemy_projectile_collisions()
        self._check_enemy_collisions()
        self._check_laser_collision()
        self._update_explosions()
        self._update_powerups()
        self.combo.update()

    def _update_enemies(self):
        for enemy in self.level.enemies[:]:
            if isinstance(enemy, Boss):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(5):
                        rand_x = enemy.rect.left + random.randint(0, 100)
                        rand_y = enemy.rect.top + random.randint(0, 100)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=500))
                    self.level.boss1_defeated = True
            elif isinstance(enemy, Boss2):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(8):
                        rand_x = enemy.rect.left + random.randint(0, 120)
                        rand_y = enemy.rect.top + random.randint(0, 120)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=600))
                    self.level.boss2_defeated = True
            elif isinstance(enemy, Boss3):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(12):
                        rand_x = enemy.rect.left + random.randint(0, 140)
                        rand_y = enemy.rect.top + random.randint(0, 140)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=700))
                    self.level.boss3_defeated = True
            elif isinstance(enemy, Boss4):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(20):
                        rand_x = enemy.rect.left + random.randint(0, 160)
                        rand_y = enemy.rect.top + random.randint(0, 160)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=800))
                    self.level.boss4_defeated = True
            elif isinstance(enemy, Boss5):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(30):
                        rand_x = enemy.rect.left + random.randint(0, 180)
                        rand_y = enemy.rect.top + random.randint(0, 180)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=1000))
                    self.level.boss5_defeated = True
            elif isinstance(enemy, Boss6):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(40):
                        rand_x = enemy.rect.left + random.randint(0, 200)
                        rand_y = enemy.rect.top + random.randint(0, 200)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=1200))
                    self.victory = True
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(self.player.rect.center, self.enemy_projectiles)

    def _update_enemy_projectiles(self):
        for e_proj in self.enemy_projectiles:
            if isinstance(e_proj, HomingProjectile):
                e_proj.update(self.player.rect.center)
            else:
                e_proj.update()

        # Gérer les projectiles qui se divisent
        new_split_projectiles = []
        for e_proj in self.enemy_projectiles:
            if isinstance(e_proj, SplittingProjectile) and e_proj.should_split():
                new_split_projectiles.extend(e_proj.split())
            elif isinstance(e_proj, MirrorProjectile) and e_proj.should_split():
                new_split_projectiles.extend(e_proj.split())
        self.enemy_projectiles.extend(new_split_projectiles)

        # Filtrer les projectiles hors écran et les projectiles expirés
        self.enemy_projectiles = [p for p in self.enemy_projectiles if (
            p.rect.top < SCREEN_HEIGHT and
            p.rect.left < SCREEN_WIDTH and
            p.rect.right > 0 and
            p.rect.bottom > 0 and
            not (isinstance(p, HomingProjectile) and p.is_expired()) and
            not (isinstance(p, BlackHoleProjectile) and p.is_expired()) and
            not (isinstance(p, PulseWaveProjectile) and p.is_expired())
        )]

    def _check_projectile_collisions(self):
        for projectile in self.projectiles[:]:
            for enemy in self.level.enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                        continue

                    # Gerer le ricochet : le projectile rebondit au lieu d'etre detruit
                    if isinstance(projectile, RicochetProjectile):
                        can_continue = projectile.ricochet()
                        if not can_continue:
                            try:
                                self.projectiles.remove(projectile)
                            except ValueError:
                                pass
                    else:
                        try:
                            self.projectiles.remove(projectile)
                        except ValueError:
                            pass

                    self.combo.hit()
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        enemy.take_damage(1)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                    else:
                        if enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread', 'ricochet']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            self.powerups.append(powerup)
                        self.level.enemies.remove(enemy)
                    self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    break

    def _check_enemy_projectile_collisions(self):
        for e_proj in self.enemy_projectiles[:]:
            if isinstance(e_proj, PulseWaveProjectile):
                if e_proj.check_collision(self.player.rect):
                    if not self.player.invulnerable:
                        self.player.hp -= 1
                        if self.player.hp <= 0:
                            self.game_over = True
                        else:
                            self.player.invulnerable = True
                            self.player.invuln_start = pygame.time.get_ticks()
            elif e_proj.rect.colliderect(self.player.rect):
                try:
                    self.enemy_projectiles.remove(e_proj)
                except ValueError:
                    pass
                if not self.player.invulnerable:
                    self.player.hp -= 1
                    if self.player.hp <= 0:
                        self.game_over = True
                    else:
                        self.player.invulnerable = True
                        self.player.invuln_start = pygame.time.get_ticks()

    def _check_enemy_collisions(self):
        for enemy in self.level.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                    continue
                if isinstance(enemy, Boss4) and enemy.charging:
                    if not self.player.invulnerable:
                        self.player.hp -= 3
                        if self.player.hp <= 0:
                            self.game_over = True
                        else:
                            self.player.invulnerable = True
                            self.player.invuln_start = pygame.time.get_ticks()
                    continue
                if not self.player.invulnerable:
                    self.player.hp -= self.player.contact_damage
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        enemy.take_damage(self.player.contact_damage)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                    else:
                        enemy.hp -= self.player.contact_damage
                    impact_x = (self.player.rect.centerx + enemy.rect.centerx) // 2
                    impact_y = (self.player.rect.centery + enemy.rect.centery) // 2
                    self.explosions.append(Explosion(impact_x, impact_y))
                    if enemy.hp <= 0 and not isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        if hasattr(enemy, 'drops_powerup') and enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            self.powerups.append(powerup)
                        self.level.enemies.remove(enemy)
                    if self.player.hp <= 0:
                        self.game_over = True
                    else:
                        self.player.invulnerable = True
                        self.player.invuln_start = pygame.time.get_ticks()

    def _check_laser_collision(self):
        for enemy in self.level.enemies:
            if isinstance(enemy, Boss3) and enemy.laser_active and not self.player.invulnerable:
                laser_rect = pygame.Rect(enemy.laser_target_x - 25, 0, 50, SCREEN_HEIGHT)
                if self.player.rect.colliderect(laser_rect):
                    self.player.hp -= 2
                    if self.player.hp <= 0:
                        self.game_over = True
                    else:
                        self.player.invulnerable = True
                        self.player.invuln_start = pygame.time.get_ticks()

    def _update_explosions(self):
        for exp in self.explosions:
            exp.update()
        self.explosions = [exp for exp in self.explosions if not exp.is_finished()]

    def _update_powerups(self):
        for powerup in self.powerups:
            powerup.update()
        self.powerups = [p for p in self.powerups if p.rect.top < SCREEN_HEIGHT]

        for powerup in self.powerups[:]:
            if powerup.rect.colliderect(self.player.rect):
                self.player.apply_powerup(powerup.power_type)
                try:
                    self.powerups.remove(powerup)
                except ValueError:
                    pass

    def draw(self):
        self.screen.fill(BLACK)
        self.level.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)
        for e_proj in self.enemy_projectiles:
            e_proj.draw(self.screen)
        for powerup in self.powerups:
            powerup.draw(self.screen)
        self.player.draw(self.screen)
        for exp in self.explosions:
            exp.draw(self.screen)

        # UI
        timer_text = self.font.render(f"Timer: {self.level.timer}", True, WHITE)
        self.screen.blit(timer_text, (10, 10))
        hp_text = self.font.render(f"HP: {self.player.hp}", True, WHITE)
        self.screen.blit(hp_text, (10, 50))
        self.combo.draw(self.screen, self.font)

        # Écrans de fin
        if self.game_over:
            self._draw_game_over()
        elif self.victory:
            self._draw_victory()
        elif self.paused:
            self._draw_pause()

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 72)
        game_over_text = big_font.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        small_font = pygame.font.SysFont(None, 32)
        hint_text = small_font.render("Cliquez pour revenir au menu", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(hint_text, hint_rect)

    def _draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 72)
        victory_text = big_font.render("VICTOIRE !", True, (50, 255, 50))
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, text_rect)

        small_font = pygame.font.SysFont(None, 32)
        hint_text = small_font.render("Cliquez pour revenir au menu", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(hint_text, hint_rect)

    def _draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 56)
        pause_text = big_font.render("PAUSE", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(pause_text, text_rect)

        small_font = pygame.font.SysFont(None, 28)
        hint_text = small_font.render("Appuyez sur Échap pour reprendre", True, (180, 180, 180))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(hint_text, hint_rect)
