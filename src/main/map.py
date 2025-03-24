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

        self.disp = pygame.surface.Surface((1600,1000), pygame.SRCALPHA)
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

        # get tile size
        self.tile_size = self.tiles[(0,0,0)].rect.width // 2 + self.spacing

    def pixel_to_tile(self, pos, pan_offset, zoom_level):
        # Adjust mouse position for panning and zooming
        adjusted_pos = pygame.Vector2(pos) - pan_offset * zoom_level
        
        # Adjust for scaled tile size
        scaled_tile_size = self.tile_size * zoom_level
        
        # Convert to hex coordinates
        x, y = pygame.Vector2(adjusted_pos) - pygame.Vector2(self.center)
        q = round((2/3*x) / scaled_tile_size)
        r = round((-1/3*x + math.sqrt(3)/3*y) / scaled_tile_size)
        s = -(q+r)

        if (q,r,s) in self.tiles:
            return self.tiles[(q,r,s)]
        return None

    def get_zoomed_tile_position(self, tile, pan_offset, zoom_level):
        """
        Calculate tile position considering zoom and pan
        """
        
        # Calculate zoomed tile size
        scaled_tile_size = self.tile_size * zoom_level
        
        # Adjust hex grid calculation for zooming
        x = scaled_tile_size * (3./2 * tile.q)
        y = scaled_tile_size * (math.sqrt(3)/2 * tile.q + math.sqrt(3) * tile.r)
        
        # Center adjustment
        zoomed_pos = (
            x + self.center[0] - scaled_tile_size//2, 
            y + self.center[1] - scaled_tile_size//2
        )
        
        # Apply panning
        pan_vec = pygame.Vector2(pan_offset)
        final_pos = pygame.Vector2(zoomed_pos) + pan_vec
        
        return final_pos

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

        # Check for hover tile
        hover_tile = self.pixel_to_tile(pos, pan_offset, zoom_level)
        
        return hover_tile
    
    def draw(self, screen):
        # Draw the surface to the screen
        screen.blit(self.disp, (0,0))