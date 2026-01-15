import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, CYAN, ORANGE
from graphics.background import Background
from entities.enemy import Enemy, ShootingEnemy, TankEnemy, DashEnemy, SplitterEnemy
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6
from systems.movement_patterns import (
    SineWavePattern, ZigZagPattern, SwoopPattern, HorizontalWavePattern
)


class Level:
    def __init__(self):
        self.background = Background(speed=2)
        self.timer = 0
        self.enemies = []
        self.spawn_events = [
            (180, lambda: self.spawn_enemies(3)),
            (300, lambda: self.spawn_formation_v(5)),
            (480, lambda: self.spawn_sine_wave_group(4)),
            (600, lambda: self.spawn_zigzag_group(3)),
            (720, lambda: self.spawn_formation_line(6)),
            (840, lambda: self.spawn_swoop_attack()),
            (900, lambda: self.spawn_shooting_enemy(1)),
            (1020, lambda: self.spawn_horizontal_squadron()),
            (1200, lambda: self.spawn_boss())
        ]
        self.spawn_events.sort(key=lambda event: event[0])

        self.boss1_defeated = False
        self.boss1_defeat_timer = 0
        self.boss2_spawn_delay = 600
        self.boss2_spawned = False

        self.boss2_defeated = False
        self.boss2_defeat_timer = 0
        self.boss3_spawn_delay = 600
        self.boss3_spawned = False

        self.boss3_defeated = False
        self.boss3_defeat_timer = 0
        self.boss4_spawn_delay = 600
        self.boss4_spawned = False

        self.boss4_defeated = False
        self.boss4_defeat_timer = 0
        self.boss5_spawn_delay = 600
        self.boss5_spawned = False

        self.boss5_defeated = False
        self.boss5_defeat_timer = 0
        self.boss6_spawn_delay = 600
        self.boss6_spawned = False

        # Spawns d'ennemis post-boss1 (nouveaux ennemis)
        self.post_boss1_spawn_events = []
        self.post_boss1_spawns_initialized = False

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

    def spawn_boss2(self):
        boss2 = Boss2(SCREEN_WIDTH // 2, -70)
        self.enemies.append(boss2)
        self.boss2_spawned = True
        print(f'Spawned Boss 2 at timer {self.timer}')

    def spawn_boss3(self):
        boss3 = Boss3(SCREEN_WIDTH // 2, -80)
        self.enemies.append(boss3)
        self.boss3_spawned = True
        print(f'Spawned Boss 3 at timer {self.timer}')

    def spawn_boss4(self):
        boss4 = Boss4(SCREEN_WIDTH // 2, -90)
        self.enemies.append(boss4)
        self.boss4_spawned = True
        print(f'Spawned Boss 4 at timer {self.timer}')

    def spawn_boss5(self):
        boss5 = Boss5(SCREEN_WIDTH // 2, -100)
        self.enemies.append(boss5)
        self.boss5_spawned = True
        print(f'Spawned Boss 5 at timer {self.timer}')

    def spawn_boss6(self):
        boss6 = Boss6(SCREEN_WIDTH // 2, -110)
        self.enemies.append(boss6)
        self.boss6_spawned = True
        print(f'Spawned Boss 6 at timer {self.timer}')

    def spawn_formation_v(self, count):
        """Spawn des ennemis en formation V"""
        center_x = SCREEN_WIDTH // 2
        spacing = 60
        for i in range(count):
            offset = (i - count // 2) * spacing
            y_offset = abs(i - count // 2) * 30
            enemy = Enemy(center_x + offset, -20 - y_offset, speed=2.5)
            enemy.image.fill(CYAN)
            self.enemies.append(enemy)
        print(f'Spawned V formation with {count} enemies at timer {self.timer}')

    def spawn_formation_line(self, count):
        """Spawn des ennemis en ligne horizontale"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            enemy = Enemy(x, -20, speed=2)
            enemy.image.fill(ORANGE)
            self.enemies.append(enemy)
        print(f'Spawned line formation with {count} enemies at timer {self.timer}')

    def spawn_sine_wave_group(self, count):
        """Spawn des ennemis avec mouvement sinusoidal"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            pattern = SineWavePattern(amplitude=80, frequency=0.05, base_speed=2.5)
            enemy = Enemy(x, -20, movement_pattern=pattern)
            enemy.image.fill((255, 100, 200))
            self.enemies.append(enemy)
        print(f'Spawned {count} sine wave enemies at timer {self.timer}')

    def spawn_zigzag_group(self, count):
        """Spawn des ennemis avec mouvement zigzag"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            pattern = ZigZagPattern(amplitude=60, switch_time=25, base_speed=3)
            enemy = Enemy(x, -20, movement_pattern=pattern)
            enemy.image.fill((100, 255, 100))
            self.enemies.append(enemy)
        print(f'Spawned {count} zigzag enemies at timer {self.timer}')

    def spawn_swoop_attack(self):
        """Spawn des ennemis qui font un pique depuis les cotes"""
        pattern_right = SwoopPattern(swoop_direction=1)
        enemy_left = Enemy(50, -20, movement_pattern=pattern_right)
        enemy_left.image.fill((255, 200, 0))
        self.enemies.append(enemy_left)

        pattern_left = SwoopPattern(swoop_direction=-1)
        enemy_right = Enemy(SCREEN_WIDTH - 50, -20, movement_pattern=pattern_left)
        enemy_right.image.fill((255, 200, 0))
        self.enemies.append(enemy_right)

        powerup_dropper = random.choice([enemy_left, enemy_right])
        powerup_dropper.drops_powerup = True

        print(f'Spawned swoop attack at timer {self.timer}')

    def spawn_horizontal_squadron(self):
        """Spawn une escadrille qui se deplace horizontalement"""
        y_positions = [-20, -80, -140]
        for i, y in enumerate(y_positions):
            direction = 1 if i % 2 == 0 else -1
            start_x = 50 if direction == 1 else SCREEN_WIDTH - 50
            pattern = HorizontalWavePattern(direction=direction, speed=5)
            enemy = Enemy(start_x, y, movement_pattern=pattern)
            enemy.image.fill((150, 150, 255))
            self.enemies.append(enemy)
        print(f'Spawned horizontal squadron at timer {self.timer}')

    # ===== Nouveaux ennemis post-Boss 1 =====

    def spawn_tank_enemies(self, count):
        """Spawn des TankEnemy - ennemis blindés et résistants"""
        for _ in range(count):
            x = random.randint(60, SCREEN_WIDTH - 60)
            enemy = TankEnemy(x, -30)
            self.enemies.append(enemy)
        print(f'Spawned {count} tank enemies at timer {self.timer}')

    def spawn_dash_enemies(self, count):
        """Spawn des DashEnemy - ennemis qui chargent le joueur"""
        spacing = SCREEN_WIDTH // (count + 1)
        for i in range(count):
            x = spacing * (i + 1)
            enemy = DashEnemy(x, -20)
            self.enemies.append(enemy)
        print(f'Spawned {count} dash enemies at timer {self.timer}')

    def spawn_splitter_enemies(self, count):
        """Spawn des SplitterEnemy - ennemis qui se divisent"""
        for _ in range(count):
            x = random.randint(80, SCREEN_WIDTH - 80)
            enemy = SplitterEnemy(x, -30)
            self.enemies.append(enemy)
        print(f'Spawned {count} splitter enemies at timer {self.timer}')

    def spawn_mixed_wave_post_boss1(self):
        """Spawn une vague mixte avec les nouveaux types d'ennemis"""
        # Un tank au centre
        tank = TankEnemy(SCREEN_WIDTH // 2, -30)
        self.enemies.append(tank)

        # Deux dashers sur les côtés
        dash_left = DashEnemy(100, -50)
        dash_right = DashEnemy(SCREEN_WIDTH - 100, -50)
        self.enemies.append(dash_left)
        self.enemies.append(dash_right)
        print(f'Spawned mixed wave at timer {self.timer}')

    def spawn_tank_formation(self):
        """Formation de tanks en ligne"""
        positions = [SCREEN_WIDTH // 4, SCREEN_WIDTH // 2, 3 * SCREEN_WIDTH // 4]
        for x in positions:
            tank = TankEnemy(x, -40)
            self.enemies.append(tank)
        print(f'Spawned tank formation at timer {self.timer}')

    def spawn_dash_ambush(self):
        """Embuscade de dashers depuis les côtés"""
        for i in range(4):
            x = 50 if i % 2 == 0 else SCREEN_WIDTH - 50
            y = -20 - (i * 40)
            dash = DashEnemy(x, y)
            self.enemies.append(dash)
        print(f'Spawned dash ambush at timer {self.timer}')

    def initialize_post_boss1_spawns(self):
        """Initialise les événements de spawn après la défaite du Boss 1"""
        base_timer = self.timer
        self.post_boss1_spawn_events = [
            (base_timer + 120, lambda: self.spawn_tank_enemies(2)),
            (base_timer + 240, lambda: self.spawn_dash_enemies(3)),
            (base_timer + 360, lambda: self.spawn_splitter_enemies(2)),
            (base_timer + 480, lambda: self.spawn_mixed_wave_post_boss1()),
            (base_timer + 550, lambda: self.spawn_shooting_enemy(2)),
            (base_timer + 600, lambda: self.spawn_tank_formation()),
            (base_timer + 720, lambda: self.spawn_dash_ambush()),
            (base_timer + 800, lambda: self.spawn_splitter_enemies(3)),
            (base_timer + 900, lambda: self.spawn_sine_wave_group(4)),
            (base_timer + 1000, lambda: self.spawn_tank_enemies(1)),
            (base_timer + 1000, lambda: self.spawn_dash_enemies(2)),
        ]
        self.post_boss1_spawn_events.sort(key=lambda event: event[0])
        self.post_boss1_spawns_initialized = True
        print(f'Initialized post-boss1 spawn events at timer {self.timer}')

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
            if not isinstance(enemy, (ShootingEnemy, Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                enemy.update()
        self.enemies = [e for e in self.enemies if (e.rect.top < SCREEN_HEIGHT or isinstance(e, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)))]

        # Gestion du spawn du Boss 2 apres defaite du Boss 1
        if self.boss1_defeated and not self.boss2_spawned:
            # Initialiser les spawns post-boss1 une seule fois
            if not self.post_boss1_spawns_initialized:
                self.initialize_post_boss1_spawns()

            # Exécuter les spawns post-boss1
            events_to_remove_post = []
            for event in self.post_boss1_spawn_events:
                if self.timer >= event[0]:
                    event[1]()
                    events_to_remove_post.append(event)
            for event in events_to_remove_post:
                self.post_boss1_spawn_events.remove(event)

            self.boss1_defeat_timer += 1
            if self.boss1_defeat_timer >= self.boss2_spawn_delay:
                self.spawn_boss2()

        # Gestion du spawn du Boss 3 apres defaite du Boss 2
        if self.boss2_defeated and not self.boss3_spawned:
            self.boss2_defeat_timer += 1
            if self.boss2_defeat_timer >= self.boss3_spawn_delay:
                self.spawn_boss3()

        # Gestion du spawn du Boss 4 apres defaite du Boss 3
        if self.boss3_defeated and not self.boss4_spawned:
            self.boss3_defeat_timer += 1
            if self.boss3_defeat_timer >= self.boss4_spawn_delay:
                self.spawn_boss4()

        # Gestion du spawn du Boss 5 apres defaite du Boss 4
        if self.boss4_defeated and not self.boss5_spawned:
            self.boss4_defeat_timer += 1
            if self.boss4_defeat_timer >= self.boss5_spawn_delay:
                self.spawn_boss5()

        # Gestion du spawn du Boss 6 apres defaite du Boss 5
        if self.boss5_defeated and not self.boss6_spawned:
            self.boss5_defeat_timer += 1
            if self.boss5_defeat_timer >= self.boss6_spawn_delay:
                self.spawn_boss6()

        if any(isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) for enemy in self.enemies):
            if self.background.speed > 0:
                self.background.speed = max(self.background.speed - 0.05, 0)
        else:
            if self.background.speed < self.background.default_speed:
                self.background.speed = min(self.background.speed + 0.05, self.background.default_speed)

    def draw(self, surface):
        self.background.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
