import pygame
import random
import math


class Explosion:
    def __init__(self, x, y, duration=300):
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.max_radius = 30

        self.particles = []
        num_particles = random.randint(8, 15)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'radius': random.randint(2, 6),
                'color': random.choice([
                    (255, 100, 0),
                    (255, 150, 0),
                    (255, 200, 50),
                    (255, 50, 0),
                ])
            }
            self.particles.append(particle)

    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            p['radius'] = max(0, p['radius'] - 0.1)

    def draw(self, surface):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            return
        progress = elapsed / self.duration

        if progress < 0.3:
            radius = int(self.max_radius * (progress / 0.3))
        else:
            radius = int(self.max_radius * (1 - (progress - 0.3) / 0.7))

        if radius < 1:
            radius = 1
        alpha = int(255 * (1 - progress))

        size = radius * 2 + 20
        explosion_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        if radius > 5:
            outer_alpha = int(alpha * 0.3)
            pygame.draw.circle(explosion_surf, (100, 30, 0, outer_alpha), (center, center), radius + 5)

        if radius > 3:
            mid_alpha = int(alpha * 0.6)
            pygame.draw.circle(explosion_surf, (255, 100, 0, mid_alpha), (center, center), int(radius * 0.8))

        if radius > 2:
            inner_alpha = int(alpha * 0.9)
            pygame.draw.circle(explosion_surf, (255, 200, 50, inner_alpha), (center, center), int(radius * 0.5))

        if progress < 0.2 and radius > 1:
            flash_alpha = int(255 * (1 - progress / 0.2))
            pygame.draw.circle(explosion_surf, (255, 255, 255, flash_alpha), (center, center), int(radius * 0.3))

        surface.blit(explosion_surf, (self.x - center, self.y - center))

        for p in self.particles:
            if p['radius'] > 0:
                particle_alpha = int(alpha * 0.8)
                color_with_alpha = (*p['color'], particle_alpha)
                particle_surf = pygame.Surface((int(p['radius']*2), int(p['radius']*2)), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color_with_alpha, (int(p['radius']), int(p['radius'])), int(p['radius']))
                surface.blit(particle_surf, (int(p['x'] - p['radius']), int(p['y'] - p['radius'])))

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time > self.duration
