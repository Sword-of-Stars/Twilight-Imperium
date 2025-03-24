import pygame, sys
import math
import json

from tile import Tile
from utils import generate_concentric_rings, round_cubic

class Map():
    def __init__(self, map_string=""):
        """
        Initialized the map 

        Attributes:
            screen (pygame.Surface): The screen to draw the map on.
            map_string (str): The string representation of the map, radially generated from https://keeganw.github.io/ti4/
        """

        self.disp = pygame.surface.Surface((1000,1000), pygame.SRCALPHA)
        self.rect = self.disp.get_rect()
        self.center = self.rect.center

        self.tiles = dict() # instant tile lookup
        self.base_scale = 0.4
        self.spacing = 5
        self.tile_size = 0

        self.map_string = list(map(lambda x: int(x), map_string.split(" ")))

        # Preload high-quality tiles
        self.preloaded_tiles = {}
        self.generate_map()
        self.get_tile_size()

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
                # Preload high-quality tile image
                tile_obj = Tile(*tile, _id=_id, scale=self.base_scale, 
                                offset=self.center, spacing=self.spacing,
                                data=planet_data[str(_id)])
                self.tiles[tile] = tile_obj
        

    def get_tile_size(self):
        self.tile_size = self.tiles[(0,0,0)].rect.width // 2 + self.spacing

    def pixel_to_tile(self, pos, pan_offset, zoom_level):
        # Adjust mouse position for panning and zooming
        adjusted_pos = pygame.Vector2(pos) - pan_offset
        
        # Adjust for scaled tile size
        self.get_tile_size()
        
        # Convert to hex coordinates
        x, y = pygame.Vector2(adjusted_pos) - pygame.Vector2(self.center)
        q = (2/3*x) / self.tile_size
        r = (-1/3*x + math.sqrt(3)/3*y) / self.tile_size
        s = -(q+r)

        q, r, s = round_cubic(q, r, s)

        if (q,r,s) in self.tiles:
            return self.tiles[(q,r,s)]
        return None
    
    def get_pixel_position(self, q, r, s):
        x = self.tile_size * (3./2 * q) - self.tile_size//2
        y = self.tile_size * (math.sqrt(3)/2 * q  +  math.sqrt(3) * r) - self.tile_size//2
        return (x, y)

    def update(self, pos, pan_offset=(0,0), zoom_level=1.0):
        # Clear the display
        self.disp.fill((0,0,0,0))  # Clear with transparent black

        # Draw all the tiles with panning and zooming
        for (q,r,s), tile in self.tiles.items():
            # Get the zoomed and panned position
            tile.get_zoomed_tile_position(pan_offset, zoom_level, self.center)
            
            # Use high-quality original image and scale
            tile.scale_img(zoom_level)
            tile.draw(self.disp)

        if (tile := self.pixel_to_tile(pos, pan_offset, zoom_level)) != None:
            x, y = tile.get_pixel_position()
            self.disp.blit(self.tiles[(0,0,0)].img, (x+self.center[0]+pan_offset[0], y+self.center[1]+pan_offset[1]))

        # Check for hover tile
        hover_tile = self.pixel_to_tile(pos, pan_offset, zoom_level)
        
        return hover_tile
    
    def draw(self, screen):
        # Draw the surface to the screen
        screen.blit(self.disp, (0,0))