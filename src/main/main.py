import pygame
import sys

from simulation import Simulation

if __name__ == "__main__":
        
    # Initialize Pygame
    pygame.init()

    # Set up the screen dimensions
    screen_width = 1600
    screen_height = 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Twilight Imperium")

    clock = pygame.time.Clock()

    sim = Simulation(screen, clock)

    # main loop
    sim.run()

    # Quit Pygame
    pygame.quit()
    sys.exit()