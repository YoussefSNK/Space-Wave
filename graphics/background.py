import pygame
import random
import math
import numpy as np

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from resource_path import resource_path


def generate_perlin_noise_2d(shape, scale, octaves=4, persistence=0.5, seed=0, tileable_y=True):
    """Génère du bruit de Perlin 2D optimisé avec NumPy, tileable verticalement."""
    np.random.seed(seed)

    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    max_value = 0

    for _ in range(octaves):
        # Taille de la grille pour cette octave
        grid_h = max(2, int(shape[0] * scale * frequency) + 2)
        grid_w = max(2, int(shape[1] * scale * frequency) + 2)

        # Grille de valeurs aléatoires
        grid = np.random.rand(grid_h, grid_w)

        # Pour rendre tileable verticalement, copier la première ligne à la fin
        if tileable_y:
            grid[-1, :] = grid[0, :]

        # Coordonnées pour l'interpolation
        if tileable_y:
            # Coordonnées cycliques pour Y (0 à grid_h-1, puis reboucle)
            y_coords = np.linspace(0, grid_h - 1, shape[0], endpoint=False)
        else:
            y_coords = np.linspace(0, grid_h - 1.001, shape[0])

        x_coords = np.linspace(0, grid_w - 1.001, shape[1])

        # Indices entiers et fractions
        y0 = y_coords.astype(int) % (grid_h - 1)  # Modulo pour boucler
        x0 = x_coords.astype(int)
        y1 = (y0 + 1) % (grid_h - 1)
        x1 = x0 + 1

        fy = y_coords - y_coords.astype(int)
        fx = x_coords - x0

        # Interpolation bilinéaire vectorisée
        fy = fy.reshape(-1, 1)
        fx = fx.reshape(1, -1)

        v00 = grid[y0][:, x0]
        v01 = grid[y0][:, x1]
        v10 = grid[y1][:, x0]
        v11 = grid[y1][:, x1]

        # Interpolation avec smoothstep pour des transitions plus douces
        fy_smooth = fy * fy * (3 - 2 * fy)
        fx_smooth = fx * fx * (3 - 2 * fx)

        layer = (v00 * (1 - fx_smooth) * (1 - fy_smooth) +
                 v01 * fx_smooth * (1 - fy_smooth) +
                 v10 * (1 - fx_smooth) * fy_smooth +
                 v11 * fx_smooth * fy_smooth)

        noise += layer * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= 2

    return noise / max_value


class Background:
    def __init__(self, image_path=None, speed=2):
        self.speed = speed
        self.default_speed = speed
        self.planets = []  # Liste des planètes avec leurs propriétés individuelles
        self.shooting_stars = []  # Étoiles filantes
        self.twinkling_stars = []  # Étoiles qui scintillent
        self.time = 0  # Compteur de temps pour les animations
        self.planet_colors = [
            (50, 35, 65),   # Violet sombre
            (35, 50, 65),   # Bleu-gris
            (65, 45, 30),   # Marron-orange
            (45, 60, 45),   # Vert-gris
            (60, 35, 35),   # Rouge sombre
            (50, 50, 35),   # Jaune-gris
        ]

        if image_path:
            self.image = pygame.image.load(resource_path(image_path)).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.stars_layer = None
        else:
            # Fond spatial avec nébuleuses (bruit de Perlin)
            self.image = self._generate_space_background()

            # Générer les planètes initiales
            self._generate_initial_planets()

            # Couches d'étoiles avec parallaxe (3 couches de profondeur)
            self.star_layers = []
            # (couche, vitesse_relative, nombre_étoiles, tailles_max)
            layer_configs = [
                (0.3, 40, 1),   # Couche lointaine - petites, lentes
                (0.6, 60, 2),   # Couche moyenne
                (1.0, 50, 3),   # Couche proche - plus grandes, rapides
            ]

            # Couleurs basées sur la température stellaire (classification spectrale)
            star_types = [
                # (couleur_base, poids_distribution, tailles_possibles, poids_tailles)
                ((200, 220, 255), 5, [2, 2, 3, 3], [20, 30, 30, 20]),   # Bleu (O/B/A) - rares, brillantes
                ((255, 255, 255), 15, [1, 2, 2, 3], [30, 35, 25, 10]),  # Blanc (F) - assez communes
                ((255, 255, 200), 20, [1, 1, 2, 2], [40, 30, 20, 10]),  # Jaune (G) - type solaire
                ((255, 220, 180), 30, [1, 1, 1, 2], [50, 30, 15, 5]),   # Orange (K) - communes
                ((255, 200, 180), 30, [1, 1, 1, 1], [60, 25, 10, 5]),   # Rouge (M) - naines rouges, très communes
            ]

            for layer_idx, (speed_factor, num_stars, max_size) in enumerate(layer_configs):
                layer_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                layer_y = 0

                for _ in range(num_stars):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)

                    # Choisir le type d'étoile selon la distribution réaliste
                    base_color, _, sizes, size_weights = random.choices(
                        star_types,
                        weights=[t[1] for t in star_types]
                    )[0]

                    # Taille corrélée au type et à la couche
                    size = min(random.choices(sizes, weights=size_weights)[0], max_size)

                    # Variation de luminosité (couches lointaines plus sombres)
                    brightness_factor = random.uniform(0.5, 0.9) * (0.6 + speed_factor * 0.4)
                    star_color = (
                        int(base_color[0] * brightness_factor),
                        int(base_color[1] * brightness_factor),
                        int(base_color[2] * brightness_factor)
                    )

                    pygame.draw.circle(layer_surface, star_color, (x, y), size)

                    # Ajouter certaines étoiles à la liste des scintillantes (surtout les brillantes)
                    if size >= 2 and random.random() < 0.3:
                        self.twinkling_stars.append({
                            'x': x,
                            'y': y,
                            'base_color': base_color,
                            'size': size,
                            'phase': random.uniform(0, 2 * np.pi),
                            'phase2': random.uniform(0, 2 * np.pi),
                            'frequency': random.uniform(0.4, 1.2),
                            'frequency2': random.uniform(0.7, 2.0),
                            'layer': layer_idx
                        })

                self.star_layers.append({
                    'surface': layer_surface,
                    'speed_factor': speed_factor,
                    'y1': 0,
                    'y2': -SCREEN_HEIGHT
                })

            # Garder la référence pour compatibilité
            self.stars_layer = self.star_layers[-1]['surface'] if self.star_layers else None

        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

    def _spawn_shooting_star(self):
        """Crée une nouvelle étoile filante."""
        # Position de départ (en haut de l'écran, côté aléatoire)
        start_x = random.randint(0, SCREEN_WIDTH)
        start_y = random.randint(-50, SCREEN_HEIGHT // 3)

        # Direction (vers le bas avec angle)
        angle = random.uniform(0.3, 0.8)  # Angle en radians (vers la droite et le bas)
        if random.random() < 0.5:
            angle = np.pi - angle  # Parfois vers la gauche

        speed = random.uniform(8, 15)
        length = random.randint(30, 80)

        self.shooting_stars.append({
            'x': start_x,
            'y': start_y,
            'vx': np.cos(angle) * speed,
            'vy': np.sin(angle) * speed,
            'length': length,
            'life': 1.0,  # Durée de vie (1.0 = pleine, 0 = morte)
            'decay': random.uniform(0.015, 0.025),
            'color': random.choice([
                (255, 255, 255),
                (200, 220, 255),
                (255, 240, 200)
            ])
        })

    def _generate_space_background(self):
        """Génère un fond spatial avec nébuleuses utilisant le bruit de Perlin (optimisé NumPy)."""
        shape = (SCREEN_HEIGHT, SCREEN_WIDTH)

        # Couleur de base de l'espace (bleu très sombre)
        r = np.full(shape, 8, dtype=np.float32)
        g = np.full(shape, 8, dtype=np.float32)
        b = np.full(shape, 20, dtype=np.float32)

        # Couleurs des nébuleuses avec leurs paramètres
        # (couleur RGB, scale, seuil, intensité)
        nebula_layers = [
            # Grande nébuleuse violette diffuse (très zoomée) - arrière-plan
            ((60, 20, 80), 0.015, 0.30, 0.55),
            # Nébuleuse cyan/turquoise - effet de profondeur
            ((15, 60, 70), 0.025, 0.38, 0.4),
            # Nébuleuse bleue moyenne
            ((20, 50, 90), 0.035, 0.40, 0.45),
            # Nébuleuse magenta/rose plus petite
            ((80, 25, 50), 0.05, 0.45, 0.4),
            # Touches dorées/orange très subtiles
            ((70, 40, 15), 0.06, 0.55, 0.25),
        ]

        for (nr, ng, nb), scale, threshold, strength in nebula_layers:
            seed = random.randint(0, 10000)
            noise = generate_perlin_noise_2d(shape, scale, octaves=5, persistence=0.6, seed=seed)

            # Transition douce au lieu d'un seuil dur
            intensity = np.clip((noise - threshold) / (1 - threshold), 0, 1)
            intensity = intensity ** 2  # Courbe pour plus de contraste

            r += nr * intensity * strength
            g += ng * intensity * strength
            b += nb * intensity * strength

        # Limiter et convertir
        r = np.clip(r, 0, 255).astype(np.uint8)
        g = np.clip(g, 0, 255).astype(np.uint8)
        b = np.clip(b, 0, 255).astype(np.uint8)

        rgb_array = np.stack([r, g, b], axis=-1)
        surface = pygame.surfarray.make_surface(rgb_array.swapaxes(0, 1))

        return surface

    def _generate_initial_planets(self):
        """Génère une planète initiale (maximum 1 à l'écran)."""
        # 50% de chance d'avoir une planète au démarrage
        if random.random() < 0.5:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2)
            radius = random.randint(20, 50)

            # Choisir un type de planète
            planet_type = random.choice(['standard', 'jupiter'])

            if planet_type == 'standard':
                base_color = random.choice(self.planet_colors)
            else:
                base_color = None  # Pas utilisé pour les planètes spéciales

            # La vitesse dépend de la taille: plus c'est gros, plus c'est lent (effet de profondeur)
            speed_factor = 0.5 - (radius / 50) * 0.35

            # Créer la surface de la planète
            if planet_type == 'standard':
                planet_surface = self._create_planet_surface(radius, base_color)
            elif planet_type == 'jupiter':
                planet_surface = self._create_jupiter_planet(radius)

            # Stocker les propriétés de la planète
            self.planets.append({
                'surface': planet_surface,
                'x': x - radius - 2,
                'speed_factor': speed_factor,  # Facteur relatif à self.speed
                'y': y,
                'radius': radius
            })

    def _spawn_new_planet(self):
        """Génère une nouvelle planète en haut de l'écran."""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(-200, -50)  # Commence au-dessus de l'écran
        radius = random.randint(20, 50)

        # Choisir un type de planète
        planet_type = random.choice(['standard', 'jupiter'])

        if planet_type == 'standard':
            base_color = random.choice(self.planet_colors)
        else:
            base_color = None  # Pas utilisé pour les planètes spéciales

        # La vitesse dépend de la taille
        speed_factor = 0.5 - (radius / 50) * 0.35

        # Créer la surface de la planète
        if planet_type == 'standard':
            planet_surface = self._create_planet_surface(radius, base_color)
        elif planet_type == 'jupiter':
            planet_surface = self._create_jupiter_planet(radius)

        # Ajouter la nouvelle planète
        self.planets.append({
            'surface': planet_surface,
            'x': x - radius - 2,
            'speed_factor': speed_factor,  # Facteur relatif à self.speed
            'y': y,
            'radius': radius
        })

    def _create_jupiter_planet(self, radius):
        """Crée une planète de type Jupiter avec bandes atmosphériques et Grande Tache Rouge."""
        size = radius * 2 + 4
        planet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = radius + 2, radius + 2

        # Générer des textures de bruit pour les turbulences
        shape = (size, size)
        seed = random.randint(0, 10000)

        # Bruit pour les turbulences atmosphériques
        turbulence_noise = generate_perlin_noise_2d(shape, scale=0.2, octaves=4, persistence=0.6, seed=seed, tileable_y=False)
        detail_noise = generate_perlin_noise_2d(shape, scale=0.4, octaves=3, persistence=0.5, seed=seed+1, tileable_y=False)

        # Palette de couleurs pour Jupiter
        # Couleurs claires pour les bandes
        light_colors = [
            (242, 232, 216),  # #f2e8d8
            (230, 220, 200),  # #e6dcc8
        ]
        # Couleurs foncées pour les bandes
        dark_colors = [
            (196, 154, 108),  # #c49a6c
            (158, 107, 63),   # #9e6b3f
        ]

        # Configuration de la Grande Tache Rouge
        gtr_angle = random.uniform(0.3, 0.6) * np.pi  # Position angulaire (légèrement sous l'équateur)
        gtr_distance = radius * 0.5  # Distance du centre
        gtr_x = cx + gtr_distance * np.cos(gtr_angle)
        gtr_y = cy + gtr_distance * np.sin(gtr_angle)
        gtr_width = radius * 0.4
        gtr_height = radius * 0.25

        # Générer les bandes - nombre variable selon la taille de la planète
        num_bands = random.randint(8, 12)
        band_data = []

        for i in range(num_bands):
            # Alterner clair/foncé
            is_light = i % 2 == 0
            # Position verticale relative (-1 à 1, 0 = équateur)
            y_pos = -1 + (i / (num_bands - 1)) * 2
            # Largeur variable de la bande
            band_width = random.uniform(0.15, 0.3)

            if is_light:
                color = random.choice(light_colors)
            else:
                color = random.choice(dark_colors)

            band_data.append({
                'y_pos': y_pos,
                'width': band_width,
                'color': color,
                'is_light': is_light
            })

        # Dessiner la planète pixel par pixel
        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = np.sqrt(dx*dx + dy*dy)

                if dist > radius:
                    continue

                ratio = dist / radius

                # Calculer la position 3D sur la sphère
                if ratio < 1:
                    z = np.sqrt(max(0, 1 - ratio * ratio))

                    # Vecteur normal
                    nx = dx / radius
                    ny = dy / radius
                    nz = z

                    # Lumière venant du haut-gauche-devant
                    lx, ly, lz = -0.5, -0.5, 1.0
                    l_norm = np.sqrt(lx*lx + ly*ly + lz*lz)
                    lx, ly, lz = lx/l_norm, ly/l_norm, lz/l_norm

                    # Intensité lumineuse
                    light_intensity = max(0, nx*lx + ny*ly + nz*lz)
                    light_intensity = 0.4 + light_intensity * 0.6

                    # Dégradé radial (centre plus clair, bords plus sombres)
                    radial_gradient = 1.0 - (ratio ** 1.5) * 0.3

                    # Déterminer la couleur de base selon la position Y (bandes horizontales)
                    # Position normalisée en Y sur la sphère (-1 à 1)
                    y_sphere = ny

                    # Trouver la bande correspondante
                    base_color = dark_colors[0]  # Couleur par défaut
                    for band in band_data:
                        band_start = band['y_pos'] - band['width'] / 2
                        band_end = band['y_pos'] + band['width'] / 2

                        if band_start <= y_sphere <= band_end:
                            base_color = band['color']
                            break

                    # Ajouter les turbulences
                    turbulence_val = turbulence_noise[y, x] * 0.15
                    detail_val = detail_noise[y, x] * 0.08

                    # Ondulations horizontales (casser la régularité des bandes)
                    wave_offset = np.sin(y_sphere * 10 + turbulence_noise[y, x] * 3) * 0.02

                    # Facteur de texture combiné
                    texture_factor = 1.0 + turbulence_val + detail_val + wave_offset

                    # Calculer la couleur finale
                    r = int(base_color[0] * texture_factor * light_intensity * radial_gradient)
                    g = int(base_color[1] * texture_factor * light_intensity * radial_gradient)
                    b = int(base_color[2] * texture_factor * light_intensity * radial_gradient)

                    # Vérifier si on est dans la Grande Tache Rouge
                    dx_gtr = x - gtr_x
                    dy_gtr = y - gtr_y
                    gtr_dist = np.sqrt((dx_gtr / gtr_width)**2 + (dy_gtr / gtr_height)**2)

                    if gtr_dist < 1.0:
                        # Couleur de la Grande Tache Rouge
                        gtr_color = (193, 68, 46)  # #c1442e

                        # Intensité de la tache (plus fort au centre)
                        gtr_intensity = 1.0 - gtr_dist
                        gtr_intensity = gtr_intensity ** 0.7  # Adoucir les bords

                        # Centre plus clair
                        if gtr_dist < 0.3:
                            lightness = 1.3
                        else:
                            lightness = 1.0

                        # Effet de rotation (spirale subtile)
                        angle = np.arctan2(dy_gtr, dx_gtr)
                        spiral_val = np.sin(angle * 3 + gtr_dist * 5) * 0.1

                        # Mélanger avec la couleur de base
                        gtr_r = int(gtr_color[0] * lightness * light_intensity * radial_gradient * (1 + spiral_val))
                        gtr_g = int(gtr_color[1] * lightness * light_intensity * radial_gradient * (1 + spiral_val))
                        gtr_b = int(gtr_color[2] * lightness * light_intensity * radial_gradient * (1 + spiral_val))

                        # Interpolation entre la bande et la tache rouge
                        r = int(r * (1 - gtr_intensity) + gtr_r * gtr_intensity)
                        g = int(g * (1 - gtr_intensity) + gtr_g * gtr_intensity)
                        b = int(b * (1 - gtr_intensity) + gtr_b * gtr_intensity)

                    # Limiter les valeurs
                    r = max(0, min(255, r))
                    g = max(0, min(255, g))
                    b = max(0, min(255, b))

                    # Alpha fade aux bords pour anti-aliasing
                    if ratio > 0.95:
                        alpha = int(255 * (1 - ratio) / 0.05)
                    else:
                        alpha = 255

                    planet_surface.set_at((x, y), (r, g, b, alpha))

        # Ajouter un voile atmosphérique léger (translucide blanc)
        atmosphere_layer = pygame.Surface((size, size), pygame.SRCALPHA)
        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = np.sqrt(dx*dx + dy*dy)

                if dist <= radius:
                    ratio = dist / radius
                    # Voile très subtil, plus visible aux bords
                    atmosphere_alpha = int(15 * (ratio ** 2))
                    atmosphere_layer.set_at((x, y), (255, 255, 255, atmosphere_alpha))

        planet_surface.blit(atmosphere_layer, (0, 0))

        # Ajouter un halo atmosphérique fin sur le bord externe
        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = np.sqrt(dx*dx + dy*dy)

                # Halo juste à l'extérieur de la planète
                if radius < dist <= radius + 3:
                    halo_intensity = 1.0 - (dist - radius) / 3
                    halo_alpha = int(40 * halo_intensity)
                    current = planet_surface.get_at((x, y))

                    r = min(255, current[0] + 20)
                    g = min(255, current[1] + 15)
                    b = min(255, current[2] + 10)
                    alpha = max(current[3], halo_alpha)

                    planet_surface.set_at((x, y), (r, g, b, alpha))

        return planet_surface

    def _create_planet_surface(self, radius, base_color):
        """Crée une surface de planète avec texture Perlin et éclairage 3D."""
        size = radius * 2 + 4
        planet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = radius + 2, radius + 2

        # Générer texture de bruit Perlin pour la planète
        shape = (size, size)
        seed = random.randint(0, 10000)

        # Texture principale (cratères, terrain)
        noise = generate_perlin_noise_2d(shape, scale=0.15, octaves=4, persistence=0.6, seed=seed, tileable_y=False)

        # Texture de détails fins
        noise_detail = generate_perlin_noise_2d(shape, scale=0.3, octaves=3, persistence=0.5, seed=seed+1, tileable_y=False)

        # Créer un masque circulaire et calculer l'éclairage
        for y in range(size):
            for x in range(size):
                # Distance du centre
                dx = x - cx
                dy = y - cy
                dist = np.sqrt(dx*dx + dy*dy)

                # Si hors du cercle, pixel transparent
                if dist > radius:
                    continue

                # Ratio de distance (0 au centre, 1 au bord)
                ratio = dist / radius

                # Éclairage sphérique (lumière vient du haut-gauche)
                # Calculer la normale de la sphère
                if ratio < 1:
                    z = np.sqrt(max(0, 1 - ratio * ratio))  # Hauteur sur la sphère

                    # Vecteur normal normalisé
                    nx = dx / radius
                    ny = dy / radius
                    nz = z

                    # Vecteur lumière (vient du haut-gauche-devant)
                    lx, ly, lz = -0.5, -0.5, 1.0
                    l_norm = np.sqrt(lx*lx + ly*ly + lz*lz)
                    lx, ly, lz = lx/l_norm, ly/l_norm, lz/l_norm

                    # Produit scalaire = intensité lumineuse
                    light_intensity = max(0, nx*lx + ny*ly + nz*lz)
                    light_intensity = 0.3 + light_intensity * 0.7  # Lumière ambiante + diffuse

                    # Assombrir les bords (ambient occlusion)
                    edge_darkening = 1 - (ratio ** 2) * 0.4
                    light_intensity *= edge_darkening
                else:
                    light_intensity = 0.3

                # Texture Perlin pour variation de surface
                terrain_val = (noise[y, x] + 1) / 2  # 0 à 1
                detail_val = (noise_detail[y, x] + 1) / 2

                # Combiner texture et couleur de base
                texture_factor = 0.7 + terrain_val * 0.3 + detail_val * 0.1

                # Calculer couleur finale
                r = int(base_color[0] * texture_factor * light_intensity)
                g = int(base_color[1] * texture_factor * light_intensity)
                b = int(base_color[2] * texture_factor * light_intensity)

                # Limiter
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                # Alpha fade aux bords pour anti-aliasing
                if ratio > 0.95:
                    alpha = int(255 * (1 - ratio) / 0.05)
                else:
                    alpha = 255

                planet_surface.set_at((x, y), (r, g, b, alpha))

        # Ajouter un reflet brillant (spéculaire)
        highlight_x = int(cx - radius * 0.35)
        highlight_y = int(cy - radius * 0.35)
        highlight_radius = max(2, radius // 6)

        for y in range(max(0, highlight_y - highlight_radius), min(size, highlight_y + highlight_radius + 1)):
            for x in range(max(0, highlight_x - highlight_radius), min(size, highlight_x + highlight_radius + 1)):
                dx = x - highlight_x
                dy = y - highlight_y
                dist = np.sqrt(dx*dx + dy*dy)

                if dist < highlight_radius:
                    # Dégradé gaussien pour le reflet
                    intensity = np.exp(-(dist**2) / (highlight_radius**2 / 2))
                    current = planet_surface.get_at((x, y))

                    # Ajouter du blanc pour le reflet
                    r = min(255, int(current[0] + 100 * intensity))
                    g = min(255, int(current[1] + 100 * intensity))
                    b = min(255, int(current[2] + 100 * intensity))

                    planet_surface.set_at((x, y), (r, g, b, current[3]))

        return planet_surface

    def update(self):
        self.time += 1

        # Mise à jour du fond (nébuleuses)
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = -SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = -SCREEN_HEIGHT

        # Mise à jour des couches d'étoiles avec parallaxe
        if hasattr(self, 'star_layers'):
            for layer in self.star_layers:
                layer['y1'] += self.speed * layer['speed_factor']
                layer['y2'] += self.speed * layer['speed_factor']
                if layer['y1'] >= SCREEN_HEIGHT:
                    layer['y1'] = -SCREEN_HEIGHT
                if layer['y2'] >= SCREEN_HEIGHT:
                    layer['y2'] = -SCREEN_HEIGHT

        # Spawn aléatoire d'étoiles filantes
        if self.speed > 0 and random.random() < 0.008:
            self._spawn_shooting_star()

        # Mise à jour des étoiles filantes
        stars_to_remove = []
        for i, star in enumerate(self.shooting_stars):
            star['x'] += star['vx']
            star['y'] += star['vy']
            star['life'] -= star['decay']

            if star['life'] <= 0 or star['y'] > SCREEN_HEIGHT + 50:
                stars_to_remove.append(i)

        for i in reversed(stars_to_remove):
            self.shooting_stars.pop(i)

        # Mise à jour de chaque planète individuellement
        planets_to_remove = []
        for i, planet in enumerate(self.planets):
            # Utiliser self.speed pour que les planètes se figent en même temps que les étoiles
            planet['y'] += self.speed * planet['speed_factor']

            # Marquer pour suppression si complètement hors de l'écran
            if planet['y'] > SCREEN_HEIGHT + planet['radius'] * 2:
                planets_to_remove.append(i)

        # Supprimer les planètes qui sont sorties de l'écran
        for i in reversed(planets_to_remove):
            self.planets.pop(i)

        # Générer aléatoirement une nouvelle planète seulement s'il n'y en a aucune (maximum 1)
        if self.stars_layer and len(self.planets) == 0 and random.random() < 0.005:
            self._spawn_new_planet()

    def draw(self, surface):
        # 1. Dessiner le fond sombre (nébuleuses)
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))

        # 2. Dessiner les couches d'étoiles avec parallaxe (de la plus lointaine à la plus proche)
        if hasattr(self, 'star_layers'):
            for layer_idx, layer in enumerate(self.star_layers):
                surface.blit(layer['surface'], (0, layer['y1']))
                surface.blit(layer['surface'], (0, layer['y2']))

            # Dessiner le scintillement des étoiles par-dessus
            self._draw_twinkling_stars(surface)

        # 3. Dessiner les planètes - triées par taille (plus grosses d'abord = plus loin)
        sorted_planets = sorted(self.planets, key=lambda p: p['radius'], reverse=True)
        for planet in sorted_planets:
            surface.blit(planet['surface'], (planet['x'], planet['y']))

        # 4. Dessiner les étoiles filantes
        self._draw_shooting_stars(surface)

    def _draw_twinkling_stars(self, surface):
        """Dessine l'effet de scintillement sur les étoiles sélectionnées."""
        t = self.time * 0.1
        for star in self.twinkling_stars:
            # Superposer deux sinusoïdes pour un effet organique et irrégulier
            twinkle1 = np.sin(t * star['frequency'] + star['phase'])
            twinkle2 = np.sin(t * star['frequency2'] + star['phase2'])
            twinkle = twinkle1 * 0.6 + twinkle2 * 0.4
            # Normaliser twinkle de [-1, 1] vers [0, 1] avec courbe douce (smoothstep)
            norm = (twinkle + 1.0) * 0.5  # 0.0 à 1.0
            norm = norm * norm * (3.0 - 2.0 * norm)  # smoothstep pour transition fluide

            # Obtenir la position Y de la couche correspondante
            if hasattr(self, 'star_layers') and star['layer'] < len(self.star_layers):
                layer = self.star_layers[star['layer']]
                y_offset1 = layer['y1']
                y_offset2 = layer['y2']

                # Halo toujours présent, alpha varie en continu de 5 à 25
                glow_alpha = int(5 + 20 * norm)
                glow_size = star['size'] + 1
                glow_color = (star['base_color'][0], star['base_color'][1], star['base_color'][2], glow_alpha)

                # Position 1
                y1 = star['y'] + y_offset1
                if 0 <= y1 <= SCREEN_HEIGHT:
                    pygame.draw.circle(surface, glow_color, (star['x'], int(y1)), glow_size)

                # Position 2
                y2 = star['y'] + y_offset2
                if 0 <= y2 <= SCREEN_HEIGHT:
                    pygame.draw.circle(surface, glow_color, (star['x'], int(y2)), glow_size)

    def _draw_shooting_stars(self, surface):
        """Dessine les étoiles filantes avec traînée."""
        for star in self.shooting_stars:
            if star['life'] <= 0:
                continue

            # Calculer les points de la traînée
            length = star['length'] * star['life']
            end_x = star['x'] - star['vx'] / np.sqrt(star['vx']**2 + star['vy']**2) * length
            end_y = star['y'] - star['vy'] / np.sqrt(star['vx']**2 + star['vy']**2) * length

            # Dessiner la traînée avec dégradé
            num_segments = 8
            for i in range(num_segments):
                t1 = i / num_segments
                t2 = (i + 1) / num_segments

                x1 = star['x'] * (1 - t1) + end_x * t1
                y1 = star['y'] * (1 - t1) + end_y * t1
                x2 = star['x'] * (1 - t2) + end_x * t2
                y2 = star['y'] * (1 - t2) + end_y * t2

                # Alpha décroissant vers la queue
                alpha = int(255 * star['life'] * (1 - t1))
                color = (star['color'][0], star['color'][1], star['color'][2], alpha)

                # Épaisseur décroissante
                thickness = max(1, int(3 * (1 - t1) * star['life']))

                # Créer une surface temporaire pour l'alpha
                if alpha > 0:
                    pygame.draw.line(surface, color[:3], (int(x1), int(y1)), (int(x2), int(y2)), thickness)

            # Point brillant à la tête
            head_alpha = int(255 * star['life'])
            pygame.draw.circle(surface, star['color'], (int(star['x']), int(star['y'])), 2)


class SpiralNebulaBackground:
    """Background spatial avec une nébuleuse spirale lointaine qui reste immobile,
    pendant que les étoiles et planètes défilent normalement."""

    def __init__(self, speed=2):
        self.speed = speed
        self.default_speed = speed
        self.planets = []
        self.shooting_stars = []
        self.twinkling_stars = []
        self.time = 0
        self.planet_colors = [
            (50, 35, 65),
            (35, 50, 65),
            (65, 45, 30),
            (45, 60, 45),
            (60, 35, 35),
            (50, 50, 35),
        ]

        # Fond statique : espace sombre + nébuleuse spirale (ne défile pas)
        self.static_bg = self._generate_spiral_background()

        # Couche de poussière/gaz qui défile lentement (très lent pour l'effet de profondeur)
        self.dust_layer = self._generate_dust_layer()
        self.dust_y1 = 0
        self.dust_y2 = -SCREEN_HEIGHT

        # Générer les planètes initiales
        self._generate_initial_planets()

        # Couches d'étoiles avec parallaxe
        self.star_layers = []
        layer_configs = [
            (0.3, 40, 1),
            (0.6, 60, 2),
            (1.0, 50, 3),
        ]

        star_types = [
            ((200, 220, 255), 5, [2, 2, 3, 3], [20, 30, 30, 20]),
            ((255, 255, 255), 15, [1, 2, 2, 3], [30, 35, 25, 10]),
            ((255, 255, 200), 20, [1, 1, 2, 2], [40, 30, 20, 10]),
            ((255, 220, 180), 30, [1, 1, 1, 2], [50, 30, 15, 5]),
            ((255, 200, 180), 30, [1, 1, 1, 1], [60, 25, 10, 5]),
        ]

        for layer_idx, (speed_factor, num_stars, max_size) in enumerate(layer_configs):
            layer_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

            for _ in range(num_stars):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)

                base_color, _, sizes, size_weights = random.choices(
                    star_types,
                    weights=[t[1] for t in star_types]
                )[0]

                size = min(random.choices(sizes, weights=size_weights)[0], max_size)

                brightness_factor = random.uniform(0.5, 0.9) * (0.6 + speed_factor * 0.4)
                star_color = (
                    int(base_color[0] * brightness_factor),
                    int(base_color[1] * brightness_factor),
                    int(base_color[2] * brightness_factor)
                )

                pygame.draw.circle(layer_surface, star_color, (x, y), size)

                if size >= 2 and random.random() < 0.3:
                    self.twinkling_stars.append({
                        'x': x,
                        'y': y,
                        'base_color': base_color,
                        'size': size,
                        'phase': random.uniform(0, 2 * np.pi),
                        'phase2': random.uniform(0, 2 * np.pi),
                        'frequency': random.uniform(0.4, 1.2),
                        'frequency2': random.uniform(0.7, 2.0),
                        'layer': layer_idx
                    })

            self.star_layers.append({
                'surface': layer_surface,
                'speed_factor': speed_factor,
                'y1': 0,
                'y2': -SCREEN_HEIGHT
            })

        self.stars_layer = self.star_layers[-1]['surface'] if self.star_layers else None

        # Pas de scrolling pour le fond statique (la nébuleuse est immobile)
        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

    def _generate_spiral_background(self):
        """Génère un fond avec une nébuleuse spirale tournante, comme vue de très loin."""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Base : espace très sombre, légèrement teinté
        base_r = np.full((SCREEN_HEIGHT, SCREEN_WIDTH), 5, dtype=np.float64)
        base_g = np.full((SCREEN_HEIGHT, SCREEN_WIDTH), 5, dtype=np.float64)
        base_b = np.full((SCREEN_HEIGHT, SCREEN_WIDTH), 12, dtype=np.float64)

        # Centre de la spirale (légèrement décentré pour un look naturel)
        cx = SCREEN_WIDTH * 0.55
        cy = SCREEN_HEIGHT * 0.4

        # Grille de coordonnées
        yy, xx = np.mgrid[0:SCREEN_HEIGHT, 0:SCREEN_WIDTH]
        dx = xx - cx
        dy = yy - cy

        # Coordonnées polaires
        dist = np.sqrt(dx * dx + dy * dy)
        angle = np.arctan2(dy, dx)

        # Rayon max de la spirale
        max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45

        # Normaliser la distance
        r_norm = dist / max_radius

        # Bruit de Perlin pour les perturbations
        shape = (SCREEN_HEIGHT, SCREEN_WIDTH)
        noise1 = generate_perlin_noise_2d(shape, scale=0.02, octaves=5, persistence=0.6,
                                          seed=random.randint(0, 10000), tileable_y=False)
        noise2 = generate_perlin_noise_2d(shape, scale=0.04, octaves=4, persistence=0.5,
                                          seed=random.randint(0, 10000), tileable_y=False)

        # --- Bras spiraux (spirale logarithmique à 2 bras) ---
        num_arms = 2
        tightness = 0.4  # Serrage de la spirale (plus petit = plus serré)
        arm_width = 0.6  # Largeur angulaire des bras

        # Perturbation de l'angle avec du bruit
        angle_perturbed = angle + noise1 * 0.8

        # Pour chaque bras spiral
        spiral_intensity = np.zeros(shape, dtype=np.float64)

        for arm in range(num_arms):
            arm_offset = arm * (2 * np.pi / num_arms)

            # Spirale logarithmique : angle_spirale = tightness * ln(r)
            # Distance angulaire au bras
            spiral_angle = tightness * np.log(np.maximum(r_norm, 0.01)) + arm_offset
            delta_angle = angle_perturbed - spiral_angle

            # Normaliser entre -pi et pi
            delta_angle = (delta_angle + np.pi) % (2 * np.pi) - np.pi

            # Intensité gaussienne autour du bras
            arm_factor = np.exp(-(delta_angle ** 2) / (2 * (arm_width ** 2)))

            # Atténuation radiale (plus faible au centre et aux bords)
            radial_falloff = np.exp(-((r_norm - 0.5) ** 2) / 0.18)

            # Atténuation douce au-delà du rayon max
            outer_fade = np.clip(1.0 - (r_norm - 1.0) * 2, 0, 1)

            spiral_intensity += arm_factor * radial_falloff * outer_fade

        # Normaliser
        spiral_intensity = np.clip(spiral_intensity, 0, 1)

        # Ajouter des perturbations de bruit aux bras
        spiral_intensity *= (0.7 + noise2 * 0.3)

        # --- Noyau central lumineux ---
        core_intensity = np.exp(-(dist ** 2) / (2 * (max_radius * 0.12) ** 2))

        # Halo autour du noyau
        halo_intensity = np.exp(-(dist ** 2) / (2 * (max_radius * 0.3) ** 2)) * 0.3

        # --- Colorisation ---
        # Bras : dégradé du violet/bleu au cyan selon la distance
        # Proche du centre : plus chaud (violet/magenta)
        # Loin du centre : plus froid (bleu/cyan)

        color_blend = np.clip(r_norm, 0, 1)

        # Couleurs des bras
        arm_r = spiral_intensity * (50 * (1 - color_blend) + 20 * color_blend)
        arm_g = spiral_intensity * (15 * (1 - color_blend) + 45 * color_blend)
        arm_b = spiral_intensity * (70 * (1 - color_blend) + 65 * color_blend)

        # Noyau (blanc-jaune chaud)
        core_r = core_intensity * 120 + halo_intensity * 40
        core_g = core_intensity * 100 + halo_intensity * 30
        core_b = core_intensity * 80 + halo_intensity * 45

        # Touches de rose/magenta dans les bras intérieurs
        inner_glow = spiral_intensity * np.exp(-(r_norm ** 2) / 0.15) * 0.5
        arm_r += inner_glow * 60
        arm_g += inner_glow * 10
        arm_b += inner_glow * 35

        # Combiner
        base_r += arm_r + core_r
        base_g += arm_g + core_g
        base_b += arm_b + core_b

        # Limiter et convertir
        final_r = np.clip(base_r, 0, 255).astype(np.uint8)
        final_g = np.clip(base_g, 0, 255).astype(np.uint8)
        final_b = np.clip(base_b, 0, 255).astype(np.uint8)

        rgb_array = np.stack([final_r, final_g, final_b], axis=-1)
        surface = pygame.surfarray.make_surface(rgb_array.swapaxes(0, 1))

        return surface

    def _generate_dust_layer(self):
        """Génère une couche de poussière cosmique semi-transparente qui défile lentement."""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        shape = (SCREEN_HEIGHT, SCREEN_WIDTH)
        noise = generate_perlin_noise_2d(shape, scale=0.03, octaves=4, persistence=0.5,
                                         seed=random.randint(0, 10000))

        # Convertir en poussière semi-transparente
        intensity = np.clip((noise - 0.4) / 0.6, 0, 1)
        intensity = intensity ** 2

        pixel_array = pygame.surfarray.pixels3d(surface)
        alpha_array = pygame.surfarray.pixels_alpha(surface)

        # Poussière bleutée/violette très subtile
        pixel_array[:, :, 0] = (intensity * 30).astype(np.uint8).T
        pixel_array[:, :, 1] = (intensity * 20).astype(np.uint8).T
        pixel_array[:, :, 2] = (intensity * 45).astype(np.uint8).T
        alpha_array[:, :] = (intensity * 40).astype(np.uint8).T

        del pixel_array
        del alpha_array

        return surface

    def _generate_initial_planets(self):
        """Génère une planète initiale (maximum 1 à l'écran)."""
        if random.random() < 0.5:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2)
            radius = random.randint(20, 50)

            planet_type = random.choice(['standard', 'jupiter'])

            if planet_type == 'standard':
                base_color = random.choice(self.planet_colors)
            else:
                base_color = None

            speed_factor = 0.5 - (radius / 50) * 0.35

            if planet_type == 'standard':
                planet_surface = self._create_planet_surface(radius, base_color)
            elif planet_type == 'jupiter':
                planet_surface = self._create_jupiter_planet(radius)

            self.planets.append({
                'surface': planet_surface,
                'x': x - radius - 2,
                'speed_factor': speed_factor,
                'y': y,
                'radius': radius
            })

    def _spawn_new_planet(self):
        """Génère une nouvelle planète en haut de l'écran."""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(-200, -50)
        radius = random.randint(20, 50)

        planet_type = random.choice(['standard', 'jupiter'])

        if planet_type == 'standard':
            base_color = random.choice(self.planet_colors)
        else:
            base_color = None

        speed_factor = 0.5 - (radius / 50) * 0.35

        if planet_type == 'standard':
            planet_surface = self._create_planet_surface(radius, base_color)
        elif planet_type == 'jupiter':
            planet_surface = self._create_jupiter_planet(radius)

        self.planets.append({
            'surface': planet_surface,
            'x': x - radius - 2,
            'speed_factor': speed_factor,
            'y': y,
            'radius': radius
        })

    # Réutiliser les méthodes de création de planètes de Background
    _create_planet_surface = Background._create_planet_surface
    _create_jupiter_planet = Background._create_jupiter_planet
    _spawn_shooting_star = Background._spawn_shooting_star
    _draw_twinkling_stars = Background._draw_twinkling_stars
    _draw_shooting_stars = Background._draw_shooting_stars

    def update(self):
        self.time += 1

        # La couche de poussière défile très lentement
        dust_speed = self.speed * 0.15
        self.dust_y1 += dust_speed
        self.dust_y2 += dust_speed
        if self.dust_y1 >= SCREEN_HEIGHT:
            self.dust_y1 = -SCREEN_HEIGHT
        if self.dust_y2 >= SCREEN_HEIGHT:
            self.dust_y2 = -SCREEN_HEIGHT

        # Mise à jour des couches d'étoiles avec parallaxe
        for layer in self.star_layers:
            layer['y1'] += self.speed * layer['speed_factor']
            layer['y2'] += self.speed * layer['speed_factor']
            if layer['y1'] >= SCREEN_HEIGHT:
                layer['y1'] = -SCREEN_HEIGHT
            if layer['y2'] >= SCREEN_HEIGHT:
                layer['y2'] = -SCREEN_HEIGHT

        # Spawn aléatoire d'étoiles filantes
        if self.speed > 0 and random.random() < 0.008:
            self._spawn_shooting_star()

        # Mise à jour des étoiles filantes
        stars_to_remove = []
        for i, star in enumerate(self.shooting_stars):
            star['x'] += star['vx']
            star['y'] += star['vy']
            star['life'] -= star['decay']
            if star['life'] <= 0 or star['y'] > SCREEN_HEIGHT + 50:
                stars_to_remove.append(i)
        for i in reversed(stars_to_remove):
            self.shooting_stars.pop(i)

        # Mise à jour des planètes
        planets_to_remove = []
        for i, planet in enumerate(self.planets):
            planet['y'] += self.speed * planet['speed_factor']
            if planet['y'] > SCREEN_HEIGHT + planet['radius'] * 2:
                planets_to_remove.append(i)
        for i in reversed(planets_to_remove):
            self.planets.pop(i)

        if self.stars_layer and len(self.planets) == 0 and random.random() < 0.005:
            self._spawn_new_planet()

    def draw(self, surface):
        # 1. Fond statique (nébuleuse spirale immobile)
        surface.blit(self.static_bg, (0, 0))

        # 2. Couche de poussière (défile très lentement)
        surface.blit(self.dust_layer, (0, int(self.dust_y1)))
        surface.blit(self.dust_layer, (0, int(self.dust_y2)))

        # 3. Couches d'étoiles avec parallaxe
        for layer in self.star_layers:
            surface.blit(layer['surface'], (0, int(layer['y1'])))
            surface.blit(layer['surface'], (0, int(layer['y2'])))

        # Scintillement
        self._draw_twinkling_stars(surface)

        # 4. Planètes
        sorted_planets = sorted(self.planets, key=lambda p: p['radius'], reverse=True)
        for planet in sorted_planets:
            surface.blit(planet['surface'], (planet['x'], planet['y']))

        # 5. Étoiles filantes
        self._draw_shooting_stars(surface)


class AuroraBackground:
    """Background spatial avec des aurores cosmiques - de magnifiques rideaux de lumière
    colorés ondulant à travers l'espace profond, avec des amas galactiques lointains
    et des particules cosmiques lumineuses."""

    def __init__(self, speed=2):
        self.speed = speed
        self.default_speed = speed
        self.planets = []
        self.shooting_stars = []
        self.twinkling_stars = []
        self.time = 0
        self.planet_colors = [
            (50, 35, 65),
            (35, 50, 65),
            (65, 45, 30),
            (45, 60, 45),
            (60, 35, 35),
            (50, 50, 35),
        ]

        # Fond statique : espace profond avec amas galactiques lointains
        self.static_bg = self._generate_deep_space()

        # Couche d'aurore cosmique (défile lentement)
        self.aurora_layer = self._generate_aurora_layer()
        self.aurora_y1 = 0
        self.aurora_y2 = -SCREEN_HEIGHT

        # Particules cosmiques lumineuses flottantes
        self.cosmic_particles = []
        for _ in range(25):
            self.cosmic_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.uniform(1.0, 2.5),
                'color': random.choice([
                    (100, 255, 150),
                    (80, 220, 255),
                    (180, 120, 255),
                    (255, 255, 200),
                ]),
                'drift_x': random.uniform(-0.2, 0.2),
                'phase': random.uniform(0, 2 * np.pi),
                'pulse_speed': random.uniform(0.03, 0.07),
            })

        # Planètes
        self._generate_initial_planets()

        # Couches d'étoiles avec parallaxe
        self.star_layers = []
        layer_configs = [
            (0.3, 40, 1),
            (0.6, 60, 2),
            (1.0, 50, 3),
        ]

        star_types = [
            ((200, 220, 255), 5, [2, 2, 3, 3], [20, 30, 30, 20]),
            ((255, 255, 255), 15, [1, 2, 2, 3], [30, 35, 25, 10]),
            ((255, 255, 200), 20, [1, 1, 2, 2], [40, 30, 20, 10]),
            ((255, 220, 180), 30, [1, 1, 1, 2], [50, 30, 15, 5]),
            ((255, 200, 180), 30, [1, 1, 1, 1], [60, 25, 10, 5]),
        ]

        for layer_idx, (speed_factor, num_stars, max_size) in enumerate(layer_configs):
            layer_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

            for _ in range(num_stars):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)

                base_color, _, sizes, size_weights = random.choices(
                    star_types,
                    weights=[t[1] for t in star_types]
                )[0]

                size = min(random.choices(sizes, weights=size_weights)[0], max_size)

                brightness_factor = random.uniform(0.5, 0.9) * (0.6 + speed_factor * 0.4)
                star_color = (
                    int(base_color[0] * brightness_factor),
                    int(base_color[1] * brightness_factor),
                    int(base_color[2] * brightness_factor)
                )

                pygame.draw.circle(layer_surface, star_color, (x, y), size)

                if size >= 2 and random.random() < 0.3:
                    self.twinkling_stars.append({
                        'x': x,
                        'y': y,
                        'base_color': base_color,
                        'size': size,
                        'phase': random.uniform(0, 2 * np.pi),
                        'phase2': random.uniform(0, 2 * np.pi),
                        'frequency': random.uniform(0.4, 1.2),
                        'frequency2': random.uniform(0.7, 2.0),
                        'layer': layer_idx
                    })

            self.star_layers.append({
                'surface': layer_surface,
                'speed_factor': speed_factor,
                'y1': 0,
                'y2': -SCREEN_HEIGHT
            })

        self.stars_layer = self.star_layers[-1]['surface'] if self.star_layers else None
        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

    def _generate_deep_space(self):
        """Génère un fond d'espace très profond avec de subtils amas galactiques lointains."""
        shape = (SCREEN_HEIGHT, SCREEN_WIDTH)

        # Base très sombre avec teinte bleu-violet profond
        base_r = np.full(shape, 3, dtype=np.float64)
        base_g = np.full(shape, 3, dtype=np.float64)
        base_b = np.full(shape, 8, dtype=np.float64)

        # Bruit subtil pour variation de fond
        noise = generate_perlin_noise_2d(shape, scale=0.012, octaves=3, persistence=0.5,
                                          seed=random.randint(0, 10000), tileable_y=False)

        base_r += np.clip(noise * 5, 0, 8)
        base_g += np.clip(noise * 3, 0, 6)
        base_b += np.clip(noise * 8, 0, 12)

        # Amas galactiques lointains (petites taches elliptiques diffuses)
        yy, xx = np.mgrid[0:SCREEN_HEIGHT, 0:SCREEN_WIDTH]
        num_clusters = random.randint(4, 7)
        for _ in range(num_clusters):
            cx = random.randint(0, SCREEN_WIDTH)
            cy = random.randint(0, SCREEN_HEIGHT)
            radius_x = random.randint(15, 50)
            radius_y = random.randint(10, 35)
            angle = random.uniform(0, np.pi)

            cluster_colors = [
                (20, 15, 30),
                (15, 20, 30),
                (25, 15, 20),
                (20, 20, 15),
            ]
            cc = random.choice(cluster_colors)

            dx = xx - cx
            dy = yy - cy
            rx = dx * np.cos(angle) + dy * np.sin(angle)
            ry = -dx * np.sin(angle) + dy * np.cos(angle)
            dist = np.sqrt((rx / max(radius_x, 1)) ** 2 + (ry / max(radius_y, 1)) ** 2)
            intensity = np.exp(-(dist ** 2) / 0.6) * 0.5

            base_r += cc[0] * intensity
            base_g += cc[1] * intensity
            base_b += cc[2] * intensity

        # Flou pour adoucir les amas et le fond
        base_r = self._blur_2d(base_r, radius=12, passes=2)
        base_g = self._blur_2d(base_g, radius=12, passes=2)
        base_b = self._blur_2d(base_b, radius=12, passes=2)

        final_r = np.clip(base_r, 0, 255).astype(np.uint8)
        final_g = np.clip(base_g, 0, 255).astype(np.uint8)
        final_b = np.clip(base_b, 0, 255).astype(np.uint8)

        rgb_array = np.stack([final_r, final_g, final_b], axis=-1)
        surface = pygame.surfarray.make_surface(rgb_array.swapaxes(0, 1))
        return surface

    @staticmethod
    def _blur_2d(arr, radius=8, passes=2):
        """Applique un flou rapide (box blur via sommes cumulées), multi-passes."""
        result = arr.astype(np.float64)
        k = 2 * radius + 1
        h, w = arr.shape
        for _ in range(passes):
            # Flou vertical
            padded = np.pad(result, ((radius, radius), (0, 0)), mode='edge')
            cs = np.vstack([np.zeros((1, w)), np.cumsum(padded, axis=0)])
            result = (cs[k:k + h, :] - cs[:h, :]) / k
            # Flou horizontal
            padded = np.pad(result, ((0, 0), (radius, radius)), mode='edge')
            cs = np.hstack([np.zeros((h, 1)), np.cumsum(padded, axis=1)])
            result = (cs[:, k:k + w] - cs[:, :w]) / k
        return result

    def _generate_aurora_layer(self):
        """Génère les rideaux d'aurore cosmique, tileable verticalement pour le scroll."""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shape = (SCREEN_HEIGHT, SCREEN_WIDTH)

        seed = random.randint(0, 10000)
        noise1 = generate_perlin_noise_2d(shape, scale=0.015, octaves=5, persistence=0.6,
                                           seed=seed, tileable_y=True)
        noise2 = generate_perlin_noise_2d(shape, scale=0.04, octaves=4, persistence=0.5,
                                           seed=seed + 1, tileable_y=True)
        noise3 = generate_perlin_noise_2d(shape, scale=0.008, octaves=3, persistence=0.7,
                                           seed=seed + 2, tileable_y=True)

        _, xx = np.mgrid[0:SCREEN_HEIGHT, 0:SCREEN_WIDTH]
        x_norm = xx / SCREEN_WIDTH

        # Rideau 1 : Vert émeraude brillant (le plus visible)
        curtain1 = np.sin(x_norm * np.pi * 7 + noise1 * 4) * 0.5 + 0.5
        curtain1 = np.clip((curtain1 - 0.40) / 0.60, 0, 1) ** 1.0
        curtain1 *= np.clip(0.6 + noise2 * 0.25 + noise3 * 0.15, 0, 1)

        # Rideau 2 : Cyan / turquoise
        curtain2 = np.sin(x_norm * np.pi * 11 + noise2 * 3.5 + 1.8) * 0.5 + 0.5
        curtain2 = np.clip((curtain2 - 0.45) / 0.55, 0, 1) ** 1.2
        curtain2 *= np.clip(0.5 + noise1 * 0.3 + noise3 * 0.2, 0, 1)

        # Rideau 3 : Violet / magenta (plus subtil)
        curtain3 = np.sin(x_norm * np.pi * 5 + noise3 * 5 + 3.2) * 0.5 + 0.5
        curtain3 = np.clip((curtain3 - 0.35) / 0.65, 0, 1) ** 0.8
        curtain3 *= np.clip(0.4 + noise1 * 0.2 + noise2 * 0.2, 0, 1)

        # Rideau 4 : Rose pâle (touches délicates)
        curtain4 = np.sin(x_norm * np.pi * 9 + noise1 * 3 + noise2 * 2 + 5.0) * 0.5 + 0.5
        curtain4 = np.clip((curtain4 - 0.50) / 0.50, 0, 1) ** 1.2
        curtain4 *= np.clip(0.3 + noise3 * 0.25, 0, 1)

        # Couleurs des rideaux
        r = curtain1 * 25 + curtain2 * 15 + curtain3 * 130 + curtain4 * 200
        g = curtain1 * 230 + curtain2 * 190 + curtain3 * 30 + curtain4 * 80
        b = curtain1 * 100 + curtain2 * 210 + curtain3 * 160 + curtain4 * 120

        # Coeur brillant des rideaux les plus intenses (blanc chaud)
        bright_core = np.clip(curtain1 - 0.65, 0, 1) / 0.35
        r += bright_core * 80
        g += bright_core * 50
        b += bright_core * 30

        # Alpha basé sur l'intensité totale
        total = curtain1 * 1.3 + curtain2 * 0.9 + curtain3 * 0.7 + curtain4 * 0.5
        alpha = np.clip(total * 150, 0, 200)

        # Flou pour des rideaux doux et diffus
        r = self._blur_2d(r, radius=10, passes=2)
        g = self._blur_2d(g, radius=10, passes=2)
        b = self._blur_2d(b, radius=10, passes=2)
        alpha = self._blur_2d(alpha, radius=10, passes=2)

        r = np.clip(r, 0, 255).astype(np.uint8)
        g = np.clip(g, 0, 255).astype(np.uint8)
        b = np.clip(b, 0, 255).astype(np.uint8)
        alpha = np.clip(alpha, 0, 200).astype(np.uint8)

        pixel_array = pygame.surfarray.pixels3d(surface)
        alpha_array = pygame.surfarray.pixels_alpha(surface)

        pixel_array[:, :, 0] = r.T
        pixel_array[:, :, 1] = g.T
        pixel_array[:, :, 2] = b.T
        alpha_array[:, :] = alpha.T

        del pixel_array
        del alpha_array

        return surface

    # Réutiliser les méthodes de Background / SpiralNebulaBackground
    _generate_initial_planets = SpiralNebulaBackground._generate_initial_planets
    _spawn_new_planet = SpiralNebulaBackground._spawn_new_planet
    _create_planet_surface = Background._create_planet_surface
    _create_jupiter_planet = Background._create_jupiter_planet
    _spawn_shooting_star = Background._spawn_shooting_star
    _draw_twinkling_stars = Background._draw_twinkling_stars
    _draw_shooting_stars = Background._draw_shooting_stars

    def update(self):
        self.time += 1

        # Aurore défile lentement
        aurora_speed = self.speed * 0.2
        self.aurora_y1 += aurora_speed
        self.aurora_y2 += aurora_speed
        if self.aurora_y1 >= SCREEN_HEIGHT:
            self.aurora_y1 = -SCREEN_HEIGHT
        if self.aurora_y2 >= SCREEN_HEIGHT:
            self.aurora_y2 = -SCREEN_HEIGHT

        # Particules cosmiques
        for p in self.cosmic_particles:
            p['x'] += p['drift_x'] + np.sin(self.time * 0.02 + p['phase']) * 0.2
            p['y'] += self.speed * 0.25
            if p['y'] > SCREEN_HEIGHT + 5:
                p['y'] = -5
                p['x'] = random.randint(0, SCREEN_WIDTH)
            if p['x'] < -5:
                p['x'] = SCREEN_WIDTH + 4
            elif p['x'] > SCREEN_WIDTH + 5:
                p['x'] = -4

        # Couches d'étoiles avec parallaxe
        for layer in self.star_layers:
            layer['y1'] += self.speed * layer['speed_factor']
            layer['y2'] += self.speed * layer['speed_factor']
            if layer['y1'] >= SCREEN_HEIGHT:
                layer['y1'] = -SCREEN_HEIGHT
            if layer['y2'] >= SCREEN_HEIGHT:
                layer['y2'] = -SCREEN_HEIGHT

        # Étoiles filantes
        if self.speed > 0 and random.random() < 0.008:
            self._spawn_shooting_star()

        stars_to_remove = []
        for i, star in enumerate(self.shooting_stars):
            star['x'] += star['vx']
            star['y'] += star['vy']
            star['life'] -= star['decay']
            if star['life'] <= 0 or star['y'] > SCREEN_HEIGHT + 50:
                stars_to_remove.append(i)
        for i in reversed(stars_to_remove):
            self.shooting_stars.pop(i)

        # Planètes
        planets_to_remove = []
        for i, planet in enumerate(self.planets):
            planet['y'] += self.speed * planet['speed_factor']
            if planet['y'] > SCREEN_HEIGHT + planet['radius'] * 2:
                planets_to_remove.append(i)
        for i in reversed(planets_to_remove):
            self.planets.pop(i)

        if self.stars_layer and len(self.planets) == 0 and random.random() < 0.005:
            self._spawn_new_planet()

    def _draw_cosmic_particles(self, surface):
        """Dessine les particules cosmiques lumineuses flottantes."""
        for p in self.cosmic_particles:
            pulse = 0.5 + 0.5 * np.sin(self.time * p['pulse_speed'] + p['phase'])
            size = max(1, int(p['size'] * (0.7 + 0.3 * pulse)))

            # Halo lumineux quand la particule pulse
            if pulse > 0.6 and size >= 2:
                glow_alpha = int(40 * (pulse - 0.6) / 0.4)
                glow_color = (p['color'][0], p['color'][1], p['color'][2], glow_alpha)
                pygame.draw.circle(surface, glow_color, (int(p['x']), int(p['y'])), size + 2)

            # Point central
            pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), size)

    def draw(self, surface):
        # 1. Fond statique (espace profond avec amas lointains)
        surface.blit(self.static_bg, (0, 0))

        # 2. Couche d'aurore (défile lentement)
        surface.blit(self.aurora_layer, (0, int(self.aurora_y1)))
        surface.blit(self.aurora_layer, (0, int(self.aurora_y2)))

        # 3. Particules cosmiques
        self._draw_cosmic_particles(surface)

        # 4. Couches d'étoiles avec parallaxe
        for layer in self.star_layers:
            surface.blit(layer['surface'], (0, int(layer['y1'])))
            surface.blit(layer['surface'], (0, int(layer['y2'])))

        # Scintillement
        self._draw_twinkling_stars(surface)

        # 5. Planètes
        sorted_planets = sorted(self.planets, key=lambda p: p['radius'], reverse=True)
        for planet in sorted_planets:
            surface.blit(planet['surface'], (planet['x'], planet['y']))

        # 6. Étoiles filantes
        self._draw_shooting_stars(surface)


class GalaxyBackground:
    """Background spatial avec une galaxie 3D en rotation composée de particules,
    des nébuleuses colorées flottantes et des effets de lumière dynamiques.
    Basé sur un rendu Three.js converti en projection 3D avec NumPy."""

    def __init__(self, speed=2):
        self.speed = speed
        self.default_speed = speed
        self.time = 0.0

        # Camera (matching Three.js: position.z=80, position.y=30, fov=75)
        fov = 75
        self.cam_y = 30.0
        self.cam_z = 80.0
        self.focal = (SCREEN_HEIGHT / 2) / math.tan(math.radians(fov / 2))
        self.cx = SCREEN_WIDTH / 2
        self.cy = SCREEN_HEIGHT / 2

        self._init_galaxy()
        self._init_nebulas()

    def _init_galaxy(self):
        """Generate galaxy particles in spiral arms (matching Three.js parameters)."""
        count = 12000
        r_max = 50.0
        branches = 4
        spin = 1.0
        rand_factor = 0.2
        rand_power = 3

        inside_color = np.array([255.0, 96.0, 48.0])   # #ff6030
        outside_color = np.array([27.0, 57.0, 132.0])   # #1b3984

        radii = np.random.random(count) * r_max
        spin_angles = radii * spin
        branch_angles = (np.arange(count) % branches) / branches * 2 * np.pi

        def rand_offset():
            sign = np.where(np.random.random(count) < 0.5, 1.0, -1.0)
            return np.power(np.random.random(count), rand_power) * sign * rand_factor * radii

        self.gx = np.cos(branch_angles + spin_angles) * radii + rand_offset()
        self.gy = rand_offset()
        self.gz = np.sin(branch_angles + spin_angles) * radii + rand_offset()

        # Color gradient from inside to outside
        t = (radii / r_max).reshape(-1, 1)
        self.g_colors = inside_color * (1 - t) + outside_color * t  # (count, 3)

    def _init_nebulas(self):
        """Generate three nebula particle clouds (matching Three.js)."""
        self.nebulas = []
        configs = [
            # (color, spread_size, particle_count, world_position)
            ((255, 0, 255), 100, 800, (30.0, -10.0, 0.0)),    # Magenta
            ((0, 255, 255), 80, 600, (-40.0, 20.0, -20.0)),   # Cyan
            ((255, 170, 0), 120, 1000, (0.0, 0.0, 40.0)),     # Orange
        ]
        for color, size, n, pos in configs:
            lx = (np.random.random(n) - 0.5) * size
            ly = (np.random.random(n) - 0.5) * size
            lz = (np.random.random(n) - 0.5) * size
            # Simulate opacity 0.4 with additive blending
            c = np.array(color, dtype=np.float64) * 0.4
            self.nebulas.append({
                'lx': lx, 'ly': ly, 'lz': lz,
                'color': c, 'pos': list(pos)
            })

    def _project(self, x, y, z):
        """Perspective projection from 3D world space to 2D screen space."""
        depth = self.cam_z - z
        valid = depth > 0.1
        safe_depth = np.where(valid, depth, 1.0)
        sx = self.focal * x / safe_depth + self.cx
        sy = self.focal * (self.cam_y - y) / safe_depth + self.cy
        return sx, sy, depth, valid

    def update(self):
        self.time += 1.0 / 60.0

    def draw(self, surface):
        t = self.time
        W, H = SCREEN_WIDTH, SCREEN_HEIGHT
        pixels = np.zeros((W, H, 3), dtype=np.int32)

        # --- Galaxy: rotate around Y axis ---
        angle = t * 0.05
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        rx = self.gx * cos_a + self.gz * sin_a
        rz = -self.gx * sin_a + self.gz * cos_a

        sx, sy, depth, valid = self._project(rx, self.gy, rz)
        sx_i = sx.astype(np.int32)
        sy_i = sy.astype(np.int32)
        vis = valid & (sx_i >= 0) & (sx_i < W) & (sy_i >= 0) & (sy_i < H)

        ix, iy = sx_i[vis], sy_i[vis]
        d = depth[vis]
        bright = np.clip(80.0 / d, 0.3, 2.0).reshape(-1, 1)
        colors = np.clip(self.g_colors[vis] * bright, 0, 255).astype(np.int32)

        np.add.at(pixels[:, :, 0], (ix, iy), colors[:, 0])
        np.add.at(pixels[:, :, 1], (ix, iy), colors[:, 1])
        np.add.at(pixels[:, :, 2], (ix, iy), colors[:, 2])

        # --- Nebulas ---
        for i, neb in enumerate(self.nebulas):
            lx, ly, lz = neb['lx'], neb['ly'], neb['lz']
            px, py, pz = neb['pos']

            if i == 0:
                # Rotate Y, then rotate X, then position with bobbing
                a = t * 0.02
                c, s = math.cos(a), math.sin(a)
                nx = lx * c + lz * s
                nz_tmp = -lx * s + lz * c
                a2 = t * 0.01
                c2, s2 = math.cos(a2), math.sin(a2)
                ny = ly * c2 - nz_tmp * s2
                nz = ly * s2 + nz_tmp * c2
                nx += px
                ny += math.sin(t * 0.3) * 5 - 10  # bobbing y (replaces base py=-10)
                nz += pz
            elif i == 1:
                # Rotate Y, then position with x drift
                a = -t * 0.03
                c, s = math.cos(a), math.sin(a)
                nx = lx * c + lz * s
                nz = -lx * s + lz * c
                ny = ly
                nx += math.cos(t * 0.2) * 5 - 40  # drifting x (replaces base px=-40)
                ny += py
                nz += pz
            else:
                # Rotate Z, then position
                a = t * 0.015
                c, s = math.cos(a), math.sin(a)
                nx = lx * c - ly * s
                ny = lx * s + ly * c
                nz = lz
                nx += px
                ny += py
                nz += pz

            sx, sy, depth, valid = self._project(nx, ny, nz)
            sx_i = sx.astype(np.int32)
            sy_i = sy.astype(np.int32)
            vis = valid & (sx_i >= 0) & (sx_i < W) & (sy_i >= 0) & (sy_i < H)

            ix, iy = sx_i[vis], sy_i[vis]
            d = depth[vis]
            bright = np.clip(60.0 / d, 0.1, 1.0)
            nc = neb['color']
            nr = np.clip(nc[0] * bright, 0, 255).astype(np.int32)
            ng = np.clip(nc[1] * bright, 0, 255).astype(np.int32)
            nb = np.clip(nc[2] * bright, 0, 255).astype(np.int32)

            np.add.at(pixels[:, :, 0], (ix, iy), nr)
            np.add.at(pixels[:, :, 1], (ix, iy), ng)
            np.add.at(pixels[:, :, 2], (ix, iy), nb)

        # --- Core glow (pulsating light at galaxy center) ---
        core_intensity = 2.5 + math.sin(t * 2) * 0.5
        _, core_sy, _, _ = self._project(
            np.array([0.0]), np.array([0.0]), np.array([0.0])
        )
        csx = int(self.cx)
        csy = int(core_sy[0])
        gr = 40
        x0, x1 = max(0, csx - gr), min(W, csx + gr)
        y0, y1 = max(0, csy - gr), min(H, csy + gr)
        if x1 > x0 and y1 > y0:
            xx, yy = np.meshgrid(
                np.arange(x0, x1), np.arange(y0, y1), indexing='ij'
            )
            dist = np.sqrt((xx - csx) ** 2 + (yy - csy) ** 2)
            glow = np.clip(1.0 - dist / gr, 0, 1) ** 2 * core_intensity * 25
            gi = glow.astype(np.int32)
            pixels[x0:x1, y0:y1, 0] += gi
            pixels[x0:x1, y0:y1, 1] += gi
            pixels[x0:x1, y0:y1, 2] += gi

        # --- Orbiting spotlight glows ---
        spot_r = 25
        for spot_idx in range(2):
            phase = t * 0.4 + spot_idx * math.pi
            spot_wx = math.sin(phase) * 70
            spot_wz = math.cos(phase) * 70
            spot_sx, spot_sy, sd, sv = self._project(
                np.array([spot_wx]), np.array([50.0]), np.array([spot_wz])
            )
            if sv[0] and sd[0] > 0.1:
                ssx = int(spot_sx[0])
                ssy = int(spot_sy[0])
                sx0 = max(0, ssx - spot_r)
                sx1 = min(W, ssx + spot_r)
                sy0 = max(0, ssy - spot_r)
                sy1 = min(H, ssy + spot_r)
                if sx1 > sx0 and sy1 > sy0:
                    sxx, syy = np.meshgrid(
                        np.arange(sx0, sx1), np.arange(sy0, sy1), indexing='ij'
                    )
                    sdist = np.sqrt((sxx - ssx) ** 2 + (syy - ssy) ** 2)
                    sglow = np.clip(1.0 - sdist / spot_r, 0, 1) ** 2 * 15
                    sgi = sglow.astype(np.int32)
                    if spot_idx == 0:
                        # Magenta spotlight
                        pixels[sx0:sx1, sy0:sy1, 0] += sgi
                        pixels[sx0:sx1, sy0:sy1, 2] += sgi
                    else:
                        # Cyan spotlight
                        pixels[sx0:sx1, sy0:sy1, 1] += sgi
                        pixels[sx0:sx1, sy0:sy1, 2] += sgi

        # Clamp and render
        pixels = np.clip(pixels, 0, 255).astype(np.uint8)
        pygame.surfarray.blit_array(surface, pixels)
