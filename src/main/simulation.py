import json
import pygame, sys
from random import randint
from copy import deepcopy
from typing import List

from map import Map
from log import EventLog
from event import Event, TacticalAction
from player import Player
from player_tracker import PlayerTracker
from units import Carrier, Cruiser, Destroyer, Dreadnought, WarSun, Fighter, SpaceDock, GroundForce
from ti4_model import TwilightImperiumRL

from attack import attack

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
        self.game_over = False
        self.visible = True

        #===== Game Attributes =====#
        self.game_phase = "strategy"

    def initialize_game(self):
        self.game_map = Map(map_string="42 30 41 38 29 34 23 28 27 46 20 21 37 50 32 22 31 25 0 0 39 2 24 0 0 0 36 4 33 0 0 0 40 1 26 0")

        for system in (starting_systems := self.game_map.get_start_tiles()):
            for planet in system.planets:
                planet.ready()

        self.players: list[Player] = []
        for i, player in enumerate(["Player 1", "Player 2", "Player 3"]):
            self.players.append(
                Player(player, 
                   _id=i,
                   starting_system=starting_systems[i],
                   starting_units=[
                       Carrier(), 
                       Carrier(),
                       GroundForce(),
                       GroundForce(),
                       GroundForce(),
                       GroundForce(),
                       Destroyer(),
                       SpaceDock()
                       ]))
         
        self.event_log.clear()

        self.player_tracker = PlayerTracker(self.players)
        self.first_player = randint(0, len(self.players)-1)
        self.player_turn = self.first_player

        self.strategy_cards = [
            "leadership",
            "diplomacy",
            "construction",
            "warfare"
        ]

        self.running = True
        self.phase = "strategy"

        self.event_log.add_event("[SYSTEM] Beginning the game!")

        #features, adjacency = self.game_map.encode_board_state()

    def strategy_phase(self):
        '''available_cards = deepcopy(self.strategy_cards)
        for i in range(len(self.players)):
            idx = (i + self.first_player)%len(self.players)
            chosen_card = self.players[idx].take_action(self.game_map, available_cards, self.phase)
            available_cards.remove(chosen_card)
            self.event_log.add_event(f"[STRATEGY] Player {idx} has chosen {chosen_card}")'''
        for i in range(len(self.players)):
            idx = (i + self.first_player)%len(self.players)
            for event in self.players[idx].take_action(self.game_map, phase = self.phase):
                self.event_log.add_event(event)

        
        self.phase = "action"
        self.event_log.add_event(f"[SYSTEM] Beginning the action phase!")


    def status_phase(self):
        for tile in self.game_map.tiles.values():
            tile.clear()
        for player in self.players:
            player.do_status_phase()
        self.phase = "strategy"
        
    def take_turn(self):
        if sum([p.passed for p in self.players]) == len(self.players):
            self.first_player += 1
            self.first_player %= len(self.players)
            self.phase = "status"
            return
        
        else:
            self.player_turn = (self.player_turn + 1) % len(self.players)
        
        
        current_player = self.players[self.player_turn]

        print(f"======================== ACTION [{current_player.name}]==========================")

        action = current_player.take_action(self.game_map)
        res = action.execute() # updates the board
        for r in res:
            print(r)
        self.event_log.add_event(str(res))

        
    def handle_user_input(self):
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
        self.game_round = 1
        while self.running:
            self.handle_user_input()

            if not self.game_over:
                if self.phase == "strategy":
                    print(f"[SYSTEM] ============ Round {self.game_round} ================")
                    for player in self.players:
                        print(f"{player.name} has {player.points} points")
                    print("\n\n")

                    self.strategy_phase()
                elif self.phase == "action":
                    self.take_turn()
                elif self.phase == "status":
                    self.status_phase()
                    self.game_round += 1

                victors = [p for p in self.players if p.points >= 50]
                if victors != []:
                    victor = max(victors, key=lambda x: x.points)
                    print(f"{victor.name} won the game!")
                    self.game_over = True

                    print(f"[SYSTEM] ============ GAME OVER (Round {self.game_round}) ================")
                    for player in self.players:
                        print(f"{player.name} has {player.points} points")
                    print("\n\n")
            
            self.update()

