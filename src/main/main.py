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
map = Map(game_display, map_string="33 24 49 26 30 40 27 48 35 39 31 45 34 41 37 46 36 44 0 28 22 0 42 25 0 29 21 0 50 47 0 23 43 0 20 32 0")

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
    map.update()
    screen.blit(game_display, (0,0))
    pygame.draw.circle(screen, (0,255,255), (screen_width//2, screen_height//2), 10)
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()