import pygame
import sys

from map import Map

# Initialize Pygame
pygame.init()

# Set up the screen dimensions
screen_width = 1600
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Twilight Imperium")

# Initialize font for hover details
hover_font = pygame.font.Font(None, 24)

game_display = pygame.surface.Surface((screen_width, screen_height))

map = Map(map_string="42 30 41 38 29 34 23 28 27 46 20 21 37 50 32 22 31 25 0 0 39 15 24 0 0 0 36 16 33 0 0 0 40 6 26 0")

# Game loop
running = True
clock = pygame.time.Clock()

# Panning variables
pan_offset = pygame.Vector2(0, 0)
is_panning = False
last_mouse_pos = None

# Zooming variables
zoom_level = 0.4
MIN_ZOOM = 0.4
MAX_ZOOM = 1.0

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Panning controls
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  # Middle mouse button
                is_panning = True
                last_mouse_pos = pygame.Vector2(event.pos)
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:  # Middle mouse button
                is_panning = False
        
        # Zooming controls
        if event.type == pygame.MOUSEWHEEL:
            # Adjust zoom level
            zoom_level = max(MIN_ZOOM, min(MAX_ZOOM, zoom_level + event.y * 0.1))
    
    # Panning logic
    if is_panning and last_mouse_pos:
        current_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        pan_offset += current_mouse_pos - last_mouse_pos
        last_mouse_pos = current_mouse_pos

    # Clear the screen
    screen.fill((0, 0, 0))  # Black background
    
    # Drawing code
    mouse_pos = pygame.mouse.get_pos()
    
    # Update map with panning, zooming, and mouse position
    hover_tile = map.update(mouse_pos, pan_offset, zoom_level)
    
    # Draw the map
    screen.blit(game_display, (0,0))
    map.draw(screen)
    
    # Draw hover details if a tile is selected
    if hover_tile:
        # Render hover text
        hover_text = str(hover_tile)
        
        # Split the text into lines
        text_lines = hover_text.split('\n')
        
        # Render each line
        text_surfaces = []
        for line in text_lines:
            text_surface = hover_font.render(line, True, (255, 255, 255))
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
        text_box_pos = (mouse_pos[0] + 10, mouse_pos[1] + 10)
        screen.blit(text_box, text_box_pos)
    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()