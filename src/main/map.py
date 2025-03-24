import pygame, sys
import math
import json

from tile import Tile
from utils import generate_concentric_rings

class Map():
    def __init__(self, map_string=""):
        """
        Initialized the map 

        Attributes:
            screen (pygame.Surface): The screen to draw the map on.
            map_string (str): The string representation of the map, radially generated from https://keeganw.github.io/ti4/
        """

        self.disp = pygame.surface.Surface((1000,1000))
        self.rect = self.disp.get_rect()
        self.center = self.rect.center

        self.tiles = dict() # instant tile lookup
        self.scale = 0.4
        self.spacing = 5
        self.tile_size = 0

        self.map_string = list(map(lambda x: int(x), map_string.split(" ")))

        self.generate_map()

    def generate_map(self):
        radius = 3 # the number of rings to create
        hex_coords = generate_concentric_rings((0,0,0), radius)
        flattened_coordinates = [x for xs in hex_coords for x in xs]

        # planet tile data
        with open("src/data/tile_data.json", "r") as data:
            planet_data = json.load(data)

        for i, tile in enumerate(flattened_coordinates):
            if i == 0: # place Mecatol Rex
                _id = 18
            else:
                _id = self.map_string[i-1]

            if _id != 0: # don't draw empty tiles
                self.tiles[tile] = Tile(*tile, _id=_id, scale=self.scale, 
                                        offset=self.center, spacing=self.spacing,
                                        data=planet_data[str(_id)])

        # get tile size
        self.tile_size = self.tiles[(0,0,0)].rect.width // 2 + self.spacing

    def pixel_to_tile(self, pos):
        x, y = pygame.Vector2(pos) - pygame.Vector2(self.center)
        q = round((2/3*x) / self.tile_size)
        r = round((-1/3*x + math.sqrt(3)/3*y) / self.tile_size)
        s = -(q+r)

        if (q,r,s) in self.tiles:
            return self.tiles[(q,r,s)]
        return None

    def update(self, pos):
        #
        self.disp.fill((0,0,0))

        # draw all the tiles
        for tile in self.tiles.values():
            tile.draw(self.disp)

        pygame.draw.circle(self.disp, (255,0,0), self.center, 10)

        # if the mouse is over the game area,
        if self.rect.collidepoint(pos):

            # nx = 3/2*q * self.tile_size + self.center[0] - self.tile_size/2
            # ny = (math.sqrt(3)/2 * q + math.sqrt(3)*r) * self.tile_size + self.center[1] - self.tile_size/  2

            # self.disp.blit(self.tiles[(0,0,0)].img, (nx, ny))

            if (tile := self.pixel_to_tile(pos)) != None:
                print(tile)
    
    def draw(self, screen):
        # draw the surface to the screen
        screen.blit(self.disp, (0,0))
        


