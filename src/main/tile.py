import pygame
import math
import json

from planet import Planet
from player import Player

class Tile():
    def __init__(self, q, r, s, _id, scale=0.5, offset=(100,100), spacing=5, data=dict()):
        """
        Defines a hexagonal tile
        """
        self.q = q
        self.r = r
        self.s = s
        self.coords = (q,r,s)

        self.offset_x, self.offset_y = offset
        self.scale = scale
        self.spacing = spacing

        self._id = _id
        self.get_img()

        self.planets = []
        self.initialize_planets(data)

        self.wormhole = None if not data["wormhole"] else data["wormhole"]

        self.space_area = []

        # activations
        self.is_active = False
        self.command_counters = []

        self.neighbors = set()

    def get_img(self):
        self.orig_img = pygame.image.load(f"src/data/tiles/ST_{self._id}.png").convert_alpha()

        self.scale_img(self.scale)

    def scale_img(self, factor):
        self.img = pygame.transform.scale_by(self.orig_img, factor)
        self.rect = self.img.get_rect()
        self.width = self.rect.width//2 + self.spacing

    def initialize_planets(self, data):
        for planet_data in data["planets"]:
            self.planets.append(Planet(planet_data, self))

    def hexagonal_distance_to(self, other_tile):
        return max(abs(self.q - other_tile.q), abs(self.r - other_tile.r), abs(self.s - other_tile.s))

    def get_pixel_position(self):
        x = self.width * (3./2 * self.q) - self.width//2
        y = self.width * (math.sqrt(3)/2 * self.q  +  math.sqrt(3) * self.r) - self.width//2
        return (x, y)
    
    def get_zoomed_tile_position(self, pan_offset, center):
        """
        Calculate tile position considering zoom and pan
        """
        
        # Adjust hex grid calculation for zooming
        x = self.width * (3./2 * self.q)
        y = self.width * (math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r)
        
        # Center adjustment
        zoomed_pos = (
            x + center[0] - self.width//2, 
            y + center[1] - self.width//2
        )
        
        # Apply panning
        pan_vec = pygame.Vector2(pan_offset)
        final_pos = pygame.Vector2(zoomed_pos) + pan_vec
        
        self.draw_pos = final_pos

    def draw(self, screen):
        #pygame.draw.circle(screen, (255,0,0), self.get_pixel_position(), self.width / 2)
        screen.blit(self.img, self.draw_pos)

    def activate(self, player: Player):
        self.is_active = True        
        self.command_counters.append(player.name)

    def deactivate(self):
        self.is_active = False

    def clear(self):
        self.deactivate()
        self.command_counters.clear()

    def remove_command_counter(self, player):
        if player.name in self.command_counters:
            self.command_counters.remove(player.name)

    def place_in_space_area(self, ship):
        self.space_area.append(ship)

    def remove_from_space_area(self, ship):
        if ship in self.space_area:
            self.space_area.remove(ship)

    def initialize_neighbors(self, game_map):
        # add neighbors to the tile
        cube_direction_vectors = [
            (1, 0, -1), (0, 1, -1), (-1, 1, 0), 
            (-1, 0, 1), (0, -1, 1), (1, -1, 0)
        ]
        for dx, dy, dz in cube_direction_vectors:
            neighbor = (self.q + dx, self.r + dy, self.s + dz)
            if neighbor in game_map:
                self.neighbors.add(game_map[neighbor])

        # consider neighbors via wormhole
        if self.wormhole != None:
            for coord, tile in game_map.items():
                if tile.wormhole == self.wormhole:
                    self.neighbors.add(game_map[coord])
        
        if self in self.neighbors:
            self.neighbors.remove(self)

    def get_neighbors(self, n=1):
        """
        Get neighbors of the tile
        """
        if n == 1:
            return self.neighbors
        else:
            neighbors = set()
            for neighbor in self.neighbors:
                neighbors.update(neighbor.get_neighbors(n-1))
            return neighbors

    def get_encoding(self):
        """
        Encodes the tile's state as a feature vector.
        Returns:
            dict: {
                "planets": list of planet encodings,
                "ships": list of ship types in the space area,
                "adjacency": list of neighbor tile IDs
            }
        """
        # Encode planets
        planet_encodings = [planet.get_encoding() for planet in self.planets]

        # Encode ships in the space area
        ship_types = [ship.name for ship in self.space_area]

        return {
            "planets": planet_encodings,
            "ships": ship_types,
            "space_area_owner": self.space_area[0].owner._id if len(self.space_area) > 0 else -1,
        }


    def __str__(self):
        msg = f"System {self._id} ({self.q, self.r, self.s})\n"
        
        for i, ship in enumerate(self.space_area):
            if i == 0: msg += f"\nSpace Area\n"
            msg += f"{str(ship)}\n"

        msg += "\n"

        for planet in self.planets:
            msg += str(planet)

        for neighbor in self.neighbors:
            msg += f"\nNeighbor: {neighbor._id}"

        return msg