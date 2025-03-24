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

game_display = pygame.surface.Surface((screen_width, screen_height))

#map = Map(game_display, map_string="21 38 29 34 46 31 23 28 35 41 32 25 27 50 22 19 37 49 0 0 40 0 24 0 0 0 39 0 26 0 0 0 36 0 30 0")terwafrv b
map = Map(map_string="42 30 41 38 29 34 23 28 27 46 20 21 37 50 32 22 31 25 0 0 39 15 24 0 0 0 36 16 33 0 0 0 40 6 26 0")

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic goes here
    
    # Clear the screen
    screen.fill((0, 0, 0))  # Black background
    
    # Drawing code goes here
    map.update(pygame.mouse.get_pos())
    screen.blit(game_display, (0,0))
    map.draw(screen)
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()