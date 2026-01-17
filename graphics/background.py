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
        """Génère les planètes initiales réparties sur tout l'écran."""
        for _ in range(random.randint(3, 6)):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT)  # Réparties sur tout l'écran
            radius = random.randint(20, 50)
            base_color = random.choice(self.planet_colors)

            # La vitesse dépend de la taille: plus c'est gros, plus c'est lent (effet de profondeur)
            speed_factor = 0.5 - (radius / 50) * 0.35

            # Créer la surface de la planète
            planet_surface = self._create_planet_surface(radius, base_color)

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
        base_color = random.choice(self.planet_colors)

        # La vitesse dépend de la taille
        speed_factor = 0.5 - (radius / 50) * 0.35

        # Créer la surface de la planète
        planet_surface = self._create_planet_surface(radius, base_color)

        # Ajouter la nouvelle planète
        self.planets.append({
            'surface': planet_surface,
            'x': x - radius - 2,
            'speed_factor': speed_factor,  # Facteur relatif à self.speed
            'y': y,
            'radius': radius
        })

    def _create_planet_surface(self, radius, base_color):
        """Crée une surface de planète avec un effet de sphère 3D."""
        # Créer une surface temporaire pour la planète
        planet_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        cx, cy = radius + 2, radius + 2  # Centre de la surface

        # Dessiner des cercles concentriques pour créer un dégradé radial
        for i in range(radius, 0, -1):
            # Ratio de distance du centre (0 au centre, 1 au bord)
            ratio = i / radius

            # Décalage pour simuler la lumière venant du haut-gauche
            light_offset_x = (1 - ratio) * radius * 0.3
            light_offset_y = (1 - ratio) * radius * 0.3

            # Interpoler la couleur: plus clair au centre-haut-gauche, plus sombre au bord
            # La partie éclairée est plus claire
            light_factor = 1.3 - ratio * 0.8  # De 1.3 (centre) à 0.5 (bord)
            color = tuple(
                max(0, min(255, int(c * light_factor)))
                for c in base_color
            )

            pygame.draw.circle(planet_surface, color,
                             (int(cx - light_offset_x), int(cy - light_offset_y)), i)

        # Ajouter un reflet brillant (petite tache lumineuse)
        highlight_x = cx - radius * 0.4
        highlight_y = cy - radius * 0.4
        highlight_radius = max(2, radius // 5)
        highlight_color = tuple(min(c + 80, 255) for c in base_color)
        pygame.draw.circle(planet_surface, highlight_color,
                         (int(highlight_x), int(highlight_y)), highlight_radius)

        # Ajouter un contour subtil pour définir le bord
        edge_color = tuple(max(0, c - 40) for c in base_color)
        pygame.draw.circle(planet_surface, edge_color, (cx, cy), radius, 1)

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

        # Générer aléatoirement de nouvelles planètes (environ 1% de chance par frame)
        if self.stars_layer and random.random() < 0.01 and len(self.planets) < 8:
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
