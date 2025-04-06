import pygame, sys
import math
import json
import numpy as np

from tile import Tile
from utils import generate_concentric_rings, round_cubic

class Map():
    def __init__(self, map_string="", zoom_level=0.4):
        """
        Initialized the map 

        Attributes:
            screen (pygame.Surface): The screen to draw the map on.
            map_string (str): The string representation of the map, radially generated from https://keeganw.github.io/ti4/
        """

        self.disp = pygame.surface.Surface((1000,850), pygame.SRCALPHA)
        self.rect = self.disp.get_rect()
        self.rect.topleft = [20,20] # offset
        self.center = self.rect.center

        self.background_color = (17, 21, 36)

        self.tiles = dict() # instant tile lookup
        self.base_scale = 0.4
        self.spacing = 5
        self.tile_size = 0

        self.map_string = list(map(lambda x: int(x), map_string.split(" ")))

        # Preload high-quality tiles
        self.preloaded_tiles = {}
        self.generate_map()
        self.get_tile_size()

        # get start tiles


        # text hovering
        self.hover_font = pygame.font.Font(None, 24)
        self.hover_tile = None

        # panning and zoom
        self.is_panning = False
        self.last_mouse_pos = (0,0)
        self.max_pan_vertical = 800
        self.max_pan_horizontal = 800
        self.pan_offset = pygame.Vector2((0,0))

        self.is_zoom = False
        self.zoom_level = zoom_level
        self.MIN_ZOOM = 0.4
        self.MAX_ZOOM = 1.0

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

        # initialize neighbors
        for tile in self.tiles.values():
            tile.initialize_neighbors(self.tiles)
        

    def get_tile_size(self):
        self.tile_size = self.tiles[(0,0,0)].rect.width // 2 + self.spacing

    def pixel_to_tile(self, pos, pan_offset):
        """
        Convert pixel coordinates to hex coordinates with improved precision.
        
        Args:
            pos (tuple): Pixel coordinates
            pan_offset (pygame.Vector2): Panning offset
            zoom_level (float): Current zoom level
        
        Returns:
            Tile object or None
        """
        # Recalculate tile size based on current zoom
        base_tile_size = self.tiles[(0,0,0)].width + self.tiles[(0,0,0)].spacing # Use the base tile width
        scaled_tile_size = base_tile_size

        # Adjust mouse position for panning and zooming
        adjusted_pos = pygame.Vector2(pos) - pan_offset - pygame.Vector2(100 + self.rect.left,75+ self.rect.top)*self.zoom_level

        # Translate to center-relative coordinates
        center_relative_pos = adjusted_pos - pygame.Vector2(self.center)

        # Precise hex coordinate conversion
        # Twilight Imperium hex grid uses a specific coordinate system
        x = center_relative_pos.x / scaled_tile_size
        y = center_relative_pos.y / scaled_tile_size

        # Cube coordinate conversion (for pointy-top hexes)
        q = 2/3*x
        r = (-1/3)*x + math.sqrt(3)/3*y

        # Use the round_cubic function from utils to get the nearest hex
        q, r, s = round_cubic(q, r, -(q+r))

        # Check if the calculated coordinate exists in tiles
        if (q, r, s) in self.tiles:
            return self.tiles[(q, r, s)]
        
        return None
    
    def get_pixel_position(self, q, r, s):
        x = self.tile_size * (3./2 * q) - self.tile_size//2
        y = self.tile_size * (math.sqrt(3)/2 * q  +  math.sqrt(3) * r) - self.tile_size//2
        return (x, y)
    
    def get_distance(self, tile1, tile2):
        """Calculate the distance between two tiles."""
        dx = tile1[0] - tile2[0]
        dy = tile1[1] - tile2[1]
        dz = tile1[2] - tile2[2]
        return (abs(dx) + abs(dy) + abs(dz)) / 2

    def update(self, pos):
        self.do_pan(pos)
        # Clear the display
        self.disp.fill(self.background_color)  # Clear with transparent black

        # Draw all the tiles with panning and zooming
        for (q,r,s), tile in self.tiles.items():
            # Get the zoomed and panned position
            tile.get_zoomed_tile_position(self.pan_offset, self.center)
            
            # Use high-quality original image and scale
            tile.scale_img(self.zoom_level)
            tile.draw(self.disp)

        # Check for hover tile
        if self.is_over(pos):
            self.hover_tile = self.pixel_to_tile(pos, self.pan_offset)
        else:
            self.hover_tile = None
    
    def draw(self, screen):
        # Draw the surface to the screen
        screen.blit(self.disp, self.rect.topleft)

    def is_over(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw_hover(self, screen, pos):
        # Draw hover details if a tile is selected
        if self.hover_tile:
            #print(self.hover_tile)
            # Render hover text
            hover_text = str(self.hover_tile)
            
            # Split the text into lines
            text_lines = hover_text.split('\n')
            
            # Render each line
            text_surfaces = []
            for line in text_lines:
                text_surface = self.hover_font.render(line, True, (255, 255, 255))
                text_surfaces.append(text_surface)
            
            # Create a surface for the text box
            max_width = max(surface.get_width() for surface in text_surfaces)
            text_box_height = sum(surface.get_height() for surface in text_surfaces)
            
            text_box = pygame.Surface((max_width + 20, text_box_height + 20), pygame.SRCALPHA)
            text_box.fill((0, 0, 0, 180))  # Semi-transparent black background
            
            # Blit text onto the text box
            for i, surface in enumerate(text_surfaces):
                text_box.blit(surface, (10, 10 + i * surface.get_height()))
            
            # Position the text box near the mouse
            text_box_pos = (pos[0] + 10, pos[1] + 10)
            screen.blit(text_box, text_box_pos)

    def start_pan(self, pos, event):
        if event.button == 2 and self.is_over(pos):  # Middle mouse button
            self.is_panning = True
            self.last_mouse_pos = pygame.Vector2(event.pos)

    def end_pan(self, event):
        if event.button == 2:  # Middle mouse button
            self.is_panning = False

    def check_pan(self, pos):
        if not self.is_over(pos):
            self.is_panning = False

    def do_pan(self, pos):
        if self.is_panning and self.last_mouse_pos:
            current_mouse_pos = pygame.Vector2(pos)
            self.pan_offset += current_mouse_pos - self.last_mouse_pos
            
            self.pan_offset[0] = max(min(self.pan_offset[0], self.max_pan_horizontal), 
                                -self.max_pan_horizontal)
            self.pan_offset[1] = max(min(self.pan_offset[1], self.max_pan_vertical), 
                                -self.max_pan_vertical)

            self.last_mouse_pos = current_mouse_pos

    def get_start_tiles(self):
        start_coords = [(0,-3,3), (3,0,-3), (-3,3,0)]
        return [self.tiles[coords] for coords in start_coords]

    def zoom(self, pos, event):
        if self.is_over(pos):
            # Adjust zoom level
            self.zoom_level = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom_level + event.y * 0.1))

    def encode_board_state(self):
        """
        Encodes the board state as a tensor for use in a graph convolutional neural network.
        
        Returns:
            node_features (np.ndarray): A 2D array where each row represents a tile's features.
            adjacency_matrix (np.ndarray): A 2D adjacency matrix representing tile connectivity.
        """
        num_tiles = len(self.tiles)
        max_planet_features = 12
        max_space_area = 7

        feature_dim = max_planet_features + max_space_area  # Adjust based on the number of features you want to include
        node_features = np.zeros((num_tiles, feature_dim))
        adjacency_matrix = np.zeros((num_tiles, num_tiles))

        # Map tile coordinates to indices for adjacency matrix
        tile_indices = {tile: idx for idx, tile in enumerate(self.tiles.keys())}

        for idx, (coords, tile) in enumerate(self.tiles.items()):
            tile_encoding = tile.get_encoding()

            # Flatten planet encodings into a fixed-size vector
            planet_features = []
            for planet in tile_encoding["planets"]:
                planet_features.extend(planet)  # Flatten planet features into a single list

            # Pad or truncate planet features to a fixed size (e.g., 10 values)
            planet_features = planet_features[:max_planet_features] + [0] * (max_planet_features - len(planet_features))

            # Encode ships as a count of each ship type (e.g., [fighters, carriers, dreadnoughts, etc.])
            ship_types = ["fighter", "carrier", "dreadnought", "cruiser", "destroyer", "warsun"]
            ship_counts = [tile_encoding["ships"].count(ship_type) for ship_type in ship_types]
            space_area_owner = [tile_encoding["space_area_owner"]]

            # Combine all features into a single feature vector
            feature_vector = planet_features + ship_counts + space_area_owner

            # Pad or truncate the feature vector to match the feature_dim
            feature_vector = feature_vector[:feature_dim] + [0] * (feature_dim - len(feature_vector))
            node_features[idx] = feature_vector

            # Encode adjacency relationships
            for neighbor_coords in tile.neighbors:
                if neighbor_coords in tile_indices:
                    neighbor_idx = tile_indices[neighbor_coords]
                    adjacency_matrix[idx, neighbor_idx] = 1  # Mark as connected

        return node_features, adjacency_matrix

