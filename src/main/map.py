import pygame, sys

from tile import Tile
from utils import generate_concentric_rings

class Map():
    def __init__(self, screen, map_string=""):
        """
        Initialized the map 

        Attributes:
            screen (pygame.Surface): The screen to draw the map on.
            map_string (str): The string representation of the map, radially generated from https://keeganw.github.io/ti4/
        """

        self.screen = screen
        self.rect = screen.get_rect()
        self.center = self.rect.center

        self.tiles = []

        self.map_string = list(map(lambda x: int(x), map_string.split(" ")))

        self.generate_map()

    def generate_map(self):
        radius = 3 # the number of rings to create
        hex_coords = generate_concentric_rings((0,0,0), radius)
        
        flattened_coordinates = [x for xs in hex_coords for x in xs]

        for i, tile in enumerate(flattened_coordinates):
            if i == 0: # place Mecatol Rex
                _id = 18
            else:
                _id = self.map_string[i-1]

            if _id != 0: # don't draw empty tiles
                self.tiles.append(Tile(*tile, _id=_id, scale=0.4, offset=self.center))

    def update(self):
        for tile in self.tiles:
            tile.draw(self.screen)
        


