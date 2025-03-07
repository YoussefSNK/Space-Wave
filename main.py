import pygame
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 1000
FPS = 60

BLACK   = (0, 0, 0)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
YELLOW  = (255, 255, 0)
WHITE   = (255, 255, 255)

class Background:
    def __init__(self, image_path=None, speed=2):
        self.speed = speed
        self.default_speed = speed
        if image_path:
            self.image = pygame.image.load(image_path).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image.fill((10, 10, 30))
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.image, WHITE, (x, y), 1)
        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

    def update(self):
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = -SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = -SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))


class Explosion:
    def __init__(self, x, y, duration=300):
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.max_radius = 30

    def update(self):
        pass 

    def draw(self, surface):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            return
        progress = elapsed / self.duration
        if progress < 0.5:
            radius = int(self.max_radius * (progress * 2))
        else:
            radius = int(self.max_radius * (1 - (progress - 0.5) * 2))
        if radius < 1:
            radius = 1
        alpha = int(255 * (1 - progress))
        explosion_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surf, (255, 255, 0, alpha), (radius, radius), radius)
        surface.blit(explosion_surf, (self.x - radius, self.y - radius))

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time > self.duration

class Enemy:
    def __init__(self, x, y, speed=3):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hp = 2

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Boss(Enemy):
    def __init__(self, x, y, speed=1):
        super().__init__(x, y, speed)
        self.image = pygame.Surface((100, 100))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 5

    def update(self):
        self.rect.y += self.speed


class ShootingEnemy(Enemy):
    def __init__(self, x, y, speed=3, shoot_delay_frames=60):
        super().__init__(x, y, speed)
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 0, 200))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.shoot_delay_frames = shoot_delay_frames
        self.last_shot_frame = 0

    def update(self, player_position, enemy_projectiles):
        self.timer += 1
        if self.timer < 120:
            self.rect.y += self.speed
        else:
            if self.timer - self.last_shot_frame >= self.shoot_delay_frames:
                self.last_shot_frame = self.timer
                proj = self.shoot(player_position)
                enemy_projectiles.append(proj)

    def shoot(self, player_position):
        ex, ey = self.rect.center
        px, py = player_position
        dx = px - ex
        dy = py - ey
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            dist = 1
        dx /= dist
        dy /= dist
        return EnemyProjectile(ex, ey, dx, dy, speed=7)

class EnemyProjectile:
    def __init__(self, x, y, dx, dy, speed=7):
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Level:
    def __init__(self):
        self.background = Background(speed=2)
        self.timer = 0
        self.enemies = []
        self.spawn_events = [
            (180, lambda: self.spawn_enemies(3)),   # À 3 secondes, spawn 3
            (600, lambda: self.spawn_enemies(5)),
            (900, lambda: self.spawn_shooting_enemy(1)),
            (1200, lambda: self.spawn_boss())
        ]
        self.spawn_events.sort(key=lambda event: event[0])

    def spawn_enemies(self, count):
        for _ in range(count):
            x = random.randint(20, SCREEN_WIDTH - 20)
            enemy = Enemy(x, -20)
            self.enemies.append(enemy)
        print(f'Spawned {count} enemies at timer {self.timer}')

    def spawn_shooting_enemy(self, count):
        for _ in range(count):
            x = random.randint(20, SCREEN_WIDTH - 20)
            enemy = ShootingEnemy(x, -20)
            self.enemies.append(enemy)
        print(f'Spawned {count} shooting enemy at timer {self.timer}')

    def spawn_boss(self):
        boss = Boss(SCREEN_WIDTH // 2, -50)
        self.enemies.append(boss)
        print(f'Spawned boss at timer {self.timer}')

    def update(self):
        self.background.update()
        self.timer += 1
        events_to_remove = []
        for event in self.spawn_events:
            if self.timer >= event[0]:
                event[1]()
                events_to_remove.append(event)
        for event in events_to_remove:
            self.spawn_events.remove(event)
        for enemy in self.enemies:
            if not isinstance(enemy, ShootingEnemy):
                enemy.update()
        self.enemies = [e for e in self.enemies if e.rect.top < SCREEN_HEIGHT]

        if any(isinstance(enemy, Boss) for enemy in self.enemies):
            if self.background.speed > 0:
                self.background.speed = max(self.background.speed - 0.05, 0)
        else:
            if self.background.speed < self.background.default_speed:
                self.background.speed = min(self.background.speed + 0.05, self.background.default_speed)

    def draw(self, surface):
        self.background.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)

class Projectile:
    def __init__(self, x, y, speed=10):
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect(center=(x, y))
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.hp = 10
        self.contact_damage = 1
        self.invulnerable = False
        self.invuln_duration = 500 
        self.invuln_start = 0

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos
        if self.invulnerable:
            now = pygame.time.get_ticks()
            if now - self.invuln_start >= self.invuln_duration:
                self.invulnerable = False

    def shoot(self, projectile_list):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            projectile = Projectile(self.rect.centerx, self.rect.top)
            projectile_list.append(projectile)
            self.last_shot = now

    def draw(self, surface):
        if self.invulnerable:
            temp_img = self.image.copy()
            pygame.draw.rect(temp_img, YELLOW, temp_img.get_rect(), 3)
            surface.blit(temp_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Wave")
    clock = pygame.time.Clock()
    running = True

    level = Level()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    projectiles = []
    enemy_projectiles = []
    explosions = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(projectiles)

        level.update()
        player.update()
        for projectile in projectiles:
            projectile.update()
        projectiles = [p for p in projectiles if p.rect.bottom > 0]

        for enemy in level.enemies:
            if isinstance(enemy, ShootingEnemy):
                enemy.update(player.rect.center, enemy_projectiles)

        for e_proj in enemy_projectiles:
            e_proj.update()
        enemy_projectiles = [p for p in enemy_projectiles if (p.rect.top < SCREEN_HEIGHT and 
                                                              p.rect.left < SCREEN_WIDTH and 
                                                              p.rect.right > 0)]

        for projectile in projectiles[:]:
            for enemy in level.enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    if isinstance(enemy, Boss):
                        enemy.hp -= 1
                        print(f'Boss touché ! HP restant : {enemy.hp}')
                        if enemy.hp <= 0:
                            level.enemies.remove(enemy)
                    else:
                        level.enemies.remove(enemy)
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    break

        for e_proj in enemy_projectiles[:]:
            if e_proj.rect.colliderect(player.rect):
                try:
                    enemy_projectiles.remove(e_proj)
                except ValueError:
                    pass
                if not player.invulnerable:
                    player.hp -= 1
                    print(f'Player touché par projectile ! HP restant : {player.hp}')
                    if player.hp <= 0:
                        print("Player éliminé ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        for enemy in level.enemies[:]:
            if enemy.rect.colliderect(player.rect):
                if not player.invulnerable:
                    player.hp -= player.contact_damage
                    print(f'Player touché par ennemi ! HP restant : {player.hp}')
                    enemy.hp -= player.contact_damage
                    impact_x = (player.rect.centerx + enemy.rect.centerx) // 2
                    impact_y = (player.rect.centery + enemy.rect.centery) // 2
                    explosions.append(Explosion(impact_x, impact_y))
                    if enemy.hp <= 0:
                        level.enemies.remove(enemy)
                    if player.hp <= 0:
                        print("Player éliminé ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if not exp.is_finished()]

        screen.fill(BLACK)
        level.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        for e_proj in enemy_projectiles:
            e_proj.draw(screen)
        player.draw(screen)
        for exp in explosions:
            exp.draw(screen)

        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Timer: {level.timer}", True, WHITE)
        screen.blit(timer_text, (10, 10))
        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 50))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
