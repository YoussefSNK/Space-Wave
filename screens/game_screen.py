import pygame
import random
from screens.base import Screen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE
from systems.level import Level
from systems.combo import ComboSystem
from systems.special_weapon import SpecialWeapon
from systems.projectile_manager import manage_enemy_projectiles
from entities.player import Player
from entities.powerup import PowerUp
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8
from entities.enemy import ShootingEnemy, DashEnemy, SplitterEnemy
from entities.projectiles import RicochetProjectile, PulseWaveProjectile
from graphics.effects import Explosion


class GameScreen(Screen):
    """Écran de jeu principal."""

    def __init__(self, screen, scalable_display=None, level_num=1):
        super().__init__(screen, scalable_display)
        self.level_num = level_num
        self.game_over = False
        self.victory = False
        self.paused = False
        self.player_crashing = False
        self.fade_timer = 0
        self.fade_duration = 240  # 4 secondes à 60 FPS

        # Initialisation du jeu
        self.level = Level()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.projectiles = []
        self.enemy_projectiles = []
        self.explosions = []
        self.powerups = []
        self.combo = ComboSystem()
        self.special_weapon = SpecialWeapon()
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

        # Si l'animation de crash est en cours, continuer le jeu mais sans contrôler le joueur
        if self.player_crashing:
            crash_finished = self.player.update()
            # Incrémenter le timer du fondu pendant le crash
            if self.fade_timer < self.fade_duration:
                self.fade_timer += 1
            if crash_finished:
                self.game_over = True
                self.player_crashing = False
        else:
            # Gestion des inputs clavier (seulement si pas en crash)
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)

            # Tir avec Espace ou clic souris
            if self.player.wants_to_shoot or pygame.mouse.get_pressed()[0]:
                self.player.shoot(self.projectiles)

            self.player.update()

        # Le jeu continue normalement (ennemis, projectiles, etc.)
        self.level.update()

        for projectile in self.projectiles:
            projectile.update()

        # Détecter les tirs qui quittent l'écran sans toucher
        projectiles_avant = len(self.projectiles)
        removed = [p for p in self.projectiles if p.rect.bottom <= 0]
        self.projectiles = [p for p in self.projectiles if p.rect.bottom > 0]
        tirs_rates = sum(1 for p in removed if not getattr(p, 'is_special_weapon', False))
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
        self.special_weapon.update()

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
                    self.level.boss6_defeated = True
            elif isinstance(enemy, Boss7):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(50):
                        rand_x = enemy.rect.left + random.randint(0, 180)
                        rand_y = enemy.rect.top + random.randint(0, 180)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=1300))
                    self.level.boss7_defeated = True
            elif isinstance(enemy, Boss8):
                result = enemy.update(self.player.rect.center, self.enemy_projectiles)
                if result is True:
                    self.level.enemies.remove(enemy)
                    for _ in range(60):
                        rand_x = enemy.rect.left + random.randint(0, 200)
                        rand_y = enemy.rect.top + random.randint(0, 200)
                        self.explosions.append(Explosion(rand_x, rand_y, duration=1500))
                    self.victory = True
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(self.player.rect.center, self.enemy_projectiles)
            elif isinstance(enemy, DashEnemy):
                enemy.update_with_player(self.player.rect.center)

    def _update_enemy_projectiles(self):
        # Utiliser le gestionnaire centralisé pour mettre à jour et filtrer les projectiles
        self.enemy_projectiles = manage_enemy_projectiles(
            self.enemy_projectiles,
            self.player.rect.center
        )

    def _check_projectile_collisions(self):
        for projectile in self.projectiles[:]:
            for enemy in self.level.enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8)) and enemy.is_dying:
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

                    new_count = self.combo.hit()
                    if self.special_weapon.check_trigger(new_count):
                        self.special_weapon.activate(self.player, self.projectiles)
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8)):
                        enemy.take_damage(1)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                    else:
                        enemy.hp -= 1
                        if enemy.hp <= 0:
                            if enemy.drops_powerup:
                                power_types = ['double', 'triple', 'spread', 'ricochet']
                                chosen_power = random.choice(power_types)
                                powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                                self.powerups.append(powerup)
                            # Gérer la division du SplitterEnemy
                            if isinstance(enemy, SplitterEnemy):
                                mini_enemies = enemy.split()
                                self.level.enemies.extend(mini_enemies)
                            self.level.enemies.remove(enemy)
                            self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                        else:
                            self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery, duration=150))
                    break

    def _check_enemy_projectile_collisions(self):
        for e_proj in self.enemy_projectiles[:]:
            if isinstance(e_proj, PulseWaveProjectile):
                if e_proj.check_collision(self.player.rect):
                    if not self.player.invulnerable:
                        self.player.hp -= 1
                        if self.player.hp <= 0:
                            if not self.player.is_crashing:
                                self.player.start_crash()
                                self.player_crashing = True
                                self.fade_timer = 0
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
                        if not self.player.is_crashing:
                            self.player.start_crash()
                            self.player_crashing = True
                    else:
                        self.player.invulnerable = True
                        self.player.invuln_start = pygame.time.get_ticks()

    def _check_enemy_collisions(self):
        for enemy in self.level.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8)) and enemy.is_dying:
                    continue
                if isinstance(enemy, Boss4) and enemy.charging:
                    if not self.player.invulnerable:
                        self.player.hp -= 3
                        if self.player.hp <= 0:
                            if not self.player.is_crashing:
                                self.player.start_crash()
                                self.player_crashing = True
                                self.fade_timer = 0
                        else:
                            self.player.invulnerable = True
                            self.player.invuln_start = pygame.time.get_ticks()
                    continue
                if not self.player.invulnerable:
                    self.player.hp -= self.player.contact_damage
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8)):
                        enemy.take_damage(self.player.contact_damage)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                    else:
                        enemy.hp -= self.player.contact_damage
                    impact_x = (self.player.rect.centerx + enemy.rect.centerx) // 2
                    impact_y = (self.player.rect.centery + enemy.rect.centery) // 2
                    self.explosions.append(Explosion(impact_x, impact_y))
                    if enemy.hp <= 0 and not isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6, Boss7, Boss8)):
                        if hasattr(enemy, 'drops_powerup') and enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            self.powerups.append(powerup)
                        # Gérer la division du SplitterEnemy
                        if isinstance(enemy, SplitterEnemy):
                            mini_enemies = enemy.split()
                            self.level.enemies.extend(mini_enemies)
                        self.level.enemies.remove(enemy)
                    if self.player.hp <= 0:
                        if not self.player.is_crashing:
                            self.player.start_crash()
                            self.player_crashing = True
                            self.fade_timer = 0
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
                        if not self.player.is_crashing:
                            self.player.start_crash()
                            self.player_crashing = True
                            self.fade_timer = 0
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
        self.special_weapon.draw(self.screen, self.font)

        # Fondu au noir progressif pendant le crash (4 secondes) et reste noir après
        if self.fade_timer > 0:
            progress = min(1.0, self.fade_timer / self.fade_duration)
            fade_alpha = int(255 * progress)
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_alpha))
            self.screen.blit(fade_surface, (0, 0))

        # Écrans de fin (afficher GAME OVER même pendant le crash)
        if self.player_crashing or self.game_over:
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
