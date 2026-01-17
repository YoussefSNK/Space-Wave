import pygame
import random
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

            # Couche des étoiles (devant les planètes) avec variation de taille et luminosité
            self.stars_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for _ in range(150):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                # Variation de taille et luminosité pour plus de réalisme
                size = random.choices([1, 1, 1, 2, 2, 3], weights=[40, 30, 15, 10, 4, 1])[0]
                brightness = random.randint(150, 255)
                star_color = (brightness, brightness, brightness)
                pygame.draw.circle(self.stars_layer, star_color, (x, y), size)

        self.y1 = 0
        self.y2 = -SCREEN_HEIGHT

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
            # Grande nébuleuse violette diffuse (très zoomée)
            ((60, 20, 80), 0.02, 0.35, 0.5),
            # Nébuleuse bleue moyenne
            ((20, 50, 90), 0.035, 0.4, 0.45),
            # Nébuleuse magenta/rose plus petite
            ((80, 25, 50), 0.05, 0.45, 0.4),
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
        # Mise à jour des étoiles
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = -SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = -SCREEN_HEIGHT

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
        # 1. Dessiner le fond sombre
        surface.blit(self.image, (0, self.y1))
        surface.blit(self.image, (0, self.y2))

        # 2. Dessiner les planètes (arrière-plan) - triées par taille (plus grosses d'abord = plus loin)
        sorted_planets = sorted(self.planets, key=lambda p: p['radius'], reverse=True)
        for planet in sorted_planets:
            surface.blit(planet['surface'], (planet['x'], planet['y']))

        # 3. Dessiner les étoiles (devant les planètes)
        if self.stars_layer:
            surface.blit(self.stars_layer, (0, self.y1))
            surface.blit(self.stars_layer, (0, self.y2))
