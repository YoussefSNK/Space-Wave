import pygame
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 1000
FPS = 60

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Background:
    def __init__(self, image_path=None, speed=2):
        self.speed = speed
        if image_path:
            self.image = pygame.image.load(image_path).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image.fill((10, 10, 30))
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.image, (255, 255, 255), (x, y), 1)
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

class Enemy:
    def __init__(self, x, y, speed=3):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.hp = 1

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


class Level:
    def __init__(self):
        self.background = Background(speed=2)
        self.timer = 0
        self.enemies = []
        self.spawn_events = [
            (180, lambda: self.spawn_enemies(3)),   # À 3 secondes, spawn 3
            (600, lambda: self.spawn_enemies(5)),
            (1200, lambda: self.spawn_boss())
        ]
        self.spawn_events.sort(key=lambda event: event[0])

    def spawn_enemies(self, count):
        for _ in range(count):
            x = random.randint(20, SCREEN_WIDTH - 20)
            enemy = Enemy(x, -20)
            self.enemies.append(enemy)
        print(f'Spawned {count} enemies at timer {self.timer}')

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
            enemy.update()
        self.enemies = [e for e in self.enemies if e.rect.top < SCREEN_HEIGHT]

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

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def shoot(self, projectile_list):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            projectile = Projectile(self.rect.centerx, self.rect.top)
            projectile_list.append(projectile)
            self.last_shot = now

    def draw(self, surface):
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
                    break

        screen.fill(BLACK)
        level.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        player.draw(screen)

        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Timer: {level.timer}", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
