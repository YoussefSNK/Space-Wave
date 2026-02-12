import pygame
import random

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, ScalableDisplay
from systems.level import Level
from systems.combo import ComboSystem
from systems.special_weapon import SpecialWeapon
from entities.player import Player
from entities.powerup import PowerUp
from entities.bosses import Boss, Boss2, Boss3, Boss4, Boss5, Boss6
from entities.enemy import ShootingEnemy
from entities.projectiles import HomingProjectile, SplittingProjectile, MirrorProjectile, BlackHoleProjectile, PulseWaveProjectile
from graphics.effects import Explosion


def run_game():
    pygame.init()
    display = ScalableDisplay()
    pygame.display.set_caption("Space Wave")
    screen = display.get_internal_surface()
    clock = pygame.time.Clock()
    running = True

    level = Level()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    projectiles = []
    enemy_projectiles = []
    explosions = []
    powerups = []
    combo = ComboSystem()
    special_weapon = SpecialWeapon()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                display.handle_resize(event.w, event.h)
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(projectiles)

        level.update()
        player.update()
        for projectile in projectiles:
            projectile.update()

        # Detecter les tirs qui quittent l'ecran sans toucher - reset le combo
        projectiles_avant = len(projectiles)
        removed = [p for p in projectiles if p.rect.bottom <= 0]
        projectiles = [p for p in projectiles if p.rect.bottom > 0]
        tirs_rates = sum(1 for p in removed if not getattr(p, 'is_special_weapon', False))
        if tirs_rates > 0:
            combo.miss()

        for enemy in level.enemies[:]:
            if isinstance(enemy, Boss):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(5):
                        rand_x = enemy.rect.left + random.randint(0, 100)
                        rand_y = enemy.rect.top + random.randint(0, 100)
                        explosions.append(Explosion(rand_x, rand_y, duration=500))
                    print("Boss 1 vaincu !")
                    level.boss1_defeated = True
            elif isinstance(enemy, Boss2):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(8):
                        rand_x = enemy.rect.left + random.randint(0, 120)
                        rand_y = enemy.rect.top + random.randint(0, 120)
                        explosions.append(Explosion(rand_x, rand_y, duration=600))
                    print("Boss 2 vaincu !")
                    level.boss2_defeated = True
            elif isinstance(enemy, Boss3):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(12):
                        rand_x = enemy.rect.left + random.randint(0, 140)
                        rand_y = enemy.rect.top + random.randint(0, 140)
                        explosions.append(Explosion(rand_x, rand_y, duration=700))
                    print("Boss 3 vaincu !")
                    level.boss3_defeated = True
            elif isinstance(enemy, Boss4):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(20):
                        rand_x = enemy.rect.left + random.randint(0, 160)
                        rand_y = enemy.rect.top + random.randint(0, 160)
                        explosions.append(Explosion(rand_x, rand_y, duration=800))
                    print("Boss 4 vaincu !")
                    level.boss4_defeated = True
            elif isinstance(enemy, Boss5):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(30):
                        rand_x = enemy.rect.left + random.randint(0, 180)
                        rand_y = enemy.rect.top + random.randint(0, 180)
                        explosions.append(Explosion(rand_x, rand_y, duration=1000))
                    print("Boss 5 vaincu !")
                    level.boss5_defeated = True
            elif isinstance(enemy, Boss6):
                result = enemy.update(player.rect.center, enemy_projectiles)
                if result is True:
                    level.enemies.remove(enemy)
                    for _ in range(40):
                        rand_x = enemy.rect.left + random.randint(0, 200)
                        rand_y = enemy.rect.top + random.randint(0, 200)
                        explosions.append(Explosion(rand_x, rand_y, duration=1200))
                    print("Boss 6 vaincu ! VICTOIRE ULTIME !")
            elif isinstance(enemy, ShootingEnemy):
                enemy.update(player.rect.center, enemy_projectiles)

        for e_proj in enemy_projectiles:
            if isinstance(e_proj, HomingProjectile):
                e_proj.update(player.rect.center)
            else:
                e_proj.update()

        # Gerer les projectiles qui se divisent
        new_split_projectiles = []
        for e_proj in enemy_projectiles:
            if isinstance(e_proj, SplittingProjectile) and e_proj.should_split():
                new_split_projectiles.extend(e_proj.split())
            elif isinstance(e_proj, MirrorProjectile) and e_proj.should_split():
                new_split_projectiles.extend(e_proj.split())
        enemy_projectiles.extend(new_split_projectiles)

        # Filtrer les projectiles hors ecran et les projectiles expires
        enemy_projectiles = [p for p in enemy_projectiles if (
            p.rect.top < SCREEN_HEIGHT and
            p.rect.left < SCREEN_WIDTH and
            p.rect.right > 0 and
            p.rect.bottom > 0 and
            not (isinstance(p, HomingProjectile) and p.is_expired()) and
            not (isinstance(p, BlackHoleProjectile) and p.is_expired()) and
            not (isinstance(p, PulseWaveProjectile) and p.is_expired())
        )]

        for projectile in projectiles[:]:
            for enemy in level.enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                        continue
                    try:
                        projectiles.remove(projectile)
                    except ValueError:
                        pass
                    new_count = combo.hit()
                    if special_weapon.check_trigger(new_count):
                        special_weapon.activate(player, projectiles)
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        enemy.take_damage(1)
                        if isinstance(enemy, Boss):
                            boss_name = "Boss 1"
                        elif isinstance(enemy, Boss2):
                            boss_name = "Boss 2"
                        elif isinstance(enemy, Boss3):
                            boss_name = "Boss 3"
                        elif isinstance(enemy, Boss4):
                            boss_name = "Boss 4"
                        elif isinstance(enemy, Boss5):
                            boss_name = "Boss 5"
                        else:
                            boss_name = "Boss 6"
                        print(f'{boss_name} touche ! HP restant : {enemy.hp}')
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                            print(f"{boss_name} en train de mourir...")
                    else:
                        if enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            powerups.append(powerup)
                            print(f"Power-up '{chosen_power}' largue !")
                        level.enemies.remove(enemy)
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    break

        for e_proj in enemy_projectiles[:]:
            # Collision speciale pour PulseWaveProjectile (onde de choc)
            if isinstance(e_proj, PulseWaveProjectile):
                if e_proj.check_collision(player.rect):
                    if not player.invulnerable:
                        player.hp -= 1
                        print(f'Player touche par onde de choc ! HP restant : {player.hp}')
                        if player.hp <= 0:
                            print("Player elimine ! Game Over.")
                            running = False
                        else:
                            player.invulnerable = True
                            player.invuln_start = pygame.time.get_ticks()
            elif e_proj.rect.colliderect(player.rect):
                try:
                    enemy_projectiles.remove(e_proj)
                except ValueError:
                    pass
                if not player.invulnerable:
                    player.hp -= 1
                    print(f'Player touche par projectile ! HP restant : {player.hp}')
                    if player.hp <= 0:
                        print("Player elimine ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        for enemy in level.enemies[:]:
            if enemy.rect.colliderect(player.rect):
                if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)) and enemy.is_dying:
                    continue
                # Collision avec Boss4 en charge = degats massifs
                if isinstance(enemy, Boss4) and enemy.charging:
                    if not player.invulnerable:
                        player.hp -= 3
                        print(f'Player ecrase par la charge ! HP restant : {player.hp}')
                        if player.hp <= 0:
                            print("Player elimine ! Game Over.")
                            running = False
                        else:
                            player.invulnerable = True
                            player.invuln_start = pygame.time.get_ticks()
                    continue
                if not player.invulnerable:
                    player.hp -= player.contact_damage
                    print(f'Player touche par ennemi ! HP restant : {player.hp}')
                    if isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        enemy.take_damage(player.contact_damage)
                        if enemy.hp <= 0 and not enemy.is_dying:
                            enemy.is_dying = True
                            if isinstance(enemy, Boss):
                                boss_name = "Boss 1"
                            elif isinstance(enemy, Boss2):
                                boss_name = "Boss 2"
                            elif isinstance(enemy, Boss3):
                                boss_name = "Boss 3"
                            elif isinstance(enemy, Boss4):
                                boss_name = "Boss 4"
                            elif isinstance(enemy, Boss5):
                                boss_name = "Boss 5"
                            else:
                                boss_name = "Boss 6"
                            print(f"{boss_name} en train de mourir...")
                    else:
                        enemy.hp -= player.contact_damage
                    impact_x = (player.rect.centerx + enemy.rect.centerx) // 2
                    impact_y = (player.rect.centery + enemy.rect.centery) // 2
                    explosions.append(Explosion(impact_x, impact_y))
                    if enemy.hp <= 0 and not isinstance(enemy, (Boss, Boss2, Boss3, Boss4, Boss5, Boss6)):
                        if hasattr(enemy, 'drops_powerup') and enemy.drops_powerup:
                            power_types = ['double', 'triple', 'spread']
                            chosen_power = random.choice(power_types)
                            powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, chosen_power)
                            powerups.append(powerup)
                            print(f"Power-up '{chosen_power}' largue !")
                        level.enemies.remove(enemy)
                    if player.hp <= 0:
                        print("Player elimine ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        # Collision avec le laser du Boss 3
        for enemy in level.enemies:
            if isinstance(enemy, Boss3) and enemy.laser_active and not player.invulnerable:
                laser_rect = pygame.Rect(enemy.laser_target_x - 25, 0, 50, SCREEN_HEIGHT)
                if player.rect.colliderect(laser_rect):
                    player.hp -= 2
                    print(f'Player touche par laser ! HP restant : {player.hp}')
                    if player.hp <= 0:
                        print("Player elimine ! Game Over.")
                        running = False
                    else:
                        player.invulnerable = True
                        player.invuln_start = pygame.time.get_ticks()

        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if not exp.is_finished()]

        for powerup in powerups:
            powerup.update()
        powerups = [p for p in powerups if p.rect.top < SCREEN_HEIGHT]

        for powerup in powerups[:]:
            if powerup.rect.colliderect(player.rect):
                player.apply_powerup(powerup.power_type)
                try:
                    powerups.remove(powerup)
                except ValueError:
                    pass

        combo.update()
        special_weapon.update()

        screen.fill(BLACK)
        level.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)
        for e_proj in enemy_projectiles:
            e_proj.draw(screen)
        for powerup in powerups:
            powerup.draw(screen)
        player.draw(screen)
        for exp in explosions:
            exp.draw(screen)

        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Timer: {level.timer}", True, WHITE)
        screen.blit(timer_text, (10, 10))
        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 50))

        combo.draw(screen, font)
        special_weapon.draw(screen, font)

        display.render()
        clock.tick(FPS)
    pygame.quit()
