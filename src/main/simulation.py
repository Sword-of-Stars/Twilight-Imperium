import json
import pygame, sys

from map import Map
from log import EventLog
from player import Player
from player_tracker import PlayerTracker

from utils import load_json

class Simulation:
    def __init__(self, screen, clock):
        #self.config = load_json("")
        # Muatt, Jord, Mol Primus
        self.event_log = EventLog()

        self.initialize_game()

        self.player_tracker = PlayerTracker(self.players)

        self.clock = clock
        self.screen = screen

        self.running = True
        self.visible = True


    def initialize_game(self):
        self.game_map = Map(map_string="42 30 41 38 29 34 23 28 27 46 20 21 37 50 32 22 31 25 0 0 39 2 24 0 0 0 36 4 33 0 0 0 40 1 26 0")

        for system in (starting_systems := self.game_map.get_start_tiles()):
            for planet in system.planets:
                planet.ready()

        self.players = [
            Player("Player 1", starting_system=starting_systems[0]),
            Player("Player 2", starting_system=starting_systems[1]),
            Player("Player 3", starting_system=starting_systems[2])
        ]

        self.event_log.clear()

        self.player_tracker = PlayerTracker(self.players)

        self.running = True
        

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            # Panning controls
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.game_map.start_pan(mouse_pos, event)
                self.player_tracker.handle_mouse_click(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONUP:
                self.game_map.end_pan(event)
            
            # Zooming controls
            if event.type == pygame.MOUSEWHEEL:
                self.game_map.zoom(mouse_pos, event)
                self.event_log.handle_mouse_wheel(mouse_pos, event)
                self.player_tracker.handle_mouse_wheel(mouse_pos, event)

    def update(self):
        # get mouse pos
        mouse_pos = pygame.mouse.get_pos()

        # Drawing code
        
        # Clear the screen
        self.screen.fill((0, 0, 0))  # Black background
        
        # Update map with panning, zooming, and mouse position
        self.game_map.update(mouse_pos)
        
        # Draw the map
        self.game_map.draw(self.screen)

        self.event_log.update()
        self.event_log.draw(self.screen)

        self.player_tracker.update()
        self.player_tracker.draw(self.screen)

        self.game_map.draw_hover(self.screen, mouse_pos)

         # Update the display
        pygame.display.flip()
        
        # Control frame rate
        self.clock.tick(60)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()