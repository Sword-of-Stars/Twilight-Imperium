import json
from utils import load_json
import random

from attack import attack
from reinforce import reinforce

from ti4_model import TwilightImperiumRL
from event import Leadership, Diplomacy, Construction, Warfare, TacticalAction, Pass
from leadership import get_command_counters
from construction import construction
from production import produce

from units import Carrier, Cruiser, Destroyer, Dreadnought, WarSun, Fighter, SpaceDock, GroundForce, Ship

class Player:
    def __init__(self, name, _id, starting_system, starting_units=[], shared_model=None, disposition="base"):
        self.name = name
        self._id = _id

        self.disposition = load_json(f"src/training/dispositions/{disposition}.json")

        self.model = TwilightImperiumRL() if shared_model == None else shared_model

        self.points = 0
        self.planets = []
        self.ships = []

        self.command_counters = {
            "tactic": 3,
            "fleet": 3,
        }

        for planet in starting_system.planets:
            self.add_planet(planet)

        self.initialize_units(starting_units, starting_system)
        self.info = str(self)

        self.passed = False
        self.strategy_card = None

        self.score = 0

    def initialize_units(self, starting_units, starting_system):
        # place starting units in the home system
        for unit in starting_units:
            unit.set_ownership(self)
            if isinstance(unit, SpaceDock):
                unit.place_on_planet(self.planets[0])
            elif isinstance(unit, Ship):
                unit.move_to_system(starting_system)
                self.ships.append(unit)

            elif isinstance(unit, GroundForce):
                unit.move_to_planet(self.planets[0])

    def get_encoding(self):
        out = [self.points,
               self.command_counters["tactic"], 
               self.command_counters["fleet"],
        ]
        out.extend(self.disposition.values())

        return out

    def take_action(self, game_map, valid_actions=["reinforce", "produce", "attack"], phase="action"):
        '''
        The meat and potatoes of this simulation
        '''
        if phase == "strategy":
            out = []
            # leadership
            n_purchased, planets_to_exhaust = get_command_counters(self)
            for planet in planets_to_exhaust:
                planet.exhaust()

            self.gain_command_counters(n_purchased + 3)
            out.append(f"{self.name} purchased {n_purchased} command counters for a total gain of {n_purchased+3}")
            print(f"{self.name} purchased {n_purchased} command counters for a total gain of {n_purchased+3}")


            
            # construction
            if (res := construction(self)) != "failed":
                unit, planet = res
                if unit == "pds":
                    planet.place_pds()
                    out.append(f"{self.name} placed a PDS on {planet.name}")
                    print(f"{self.name} placed a PDS on {planet.name}")

                elif unit == "space dock":
                    planet.place_space_dock()
                    out.append(f"{self.name} placed a space dock on {planet.name}")
                    f"{self.name} placed a space dock on {planet.name}"
            else:
                print(f"{self.name} attempted to build a structure, but could not")

            return out


        features, adjacency = game_map.encode_board_state()
        player_inputs = self.get_encoding()
        player_inputs.extend([
            phase == "strategy",
            phase == "action",
        ])


        # no decisions made in the status phase
        decision = self.model.choose_action(state=(features, adjacency, player_inputs), 
                                            valid_actions=valid_actions)          
        if phase == "action":
            print(f"{self.name} Action priorities: {decision}")
            return self.tactical_model(decision)

        return decision

    def tactical_model(self, decisions):
        if len(decisions) == 0 or self.command_counters["tactic"] == 0:
            print(f"{self.name} passed")
            return Pass(self)
        
        action = decisions.pop(0)
        if action == "attack":
            if (res := attack(self)) == "failed":
                # the action failed, perform the next one
                print(f"{self.name} had no viable targets to attack")
                return self.tactical_model(decisions)
                
            system, ships = res
            print(f"{self.name} attacked {system._id} with {[s.name for s in ships]}")

            return TacticalAction(self, system, ships)

        elif action == "reinforce":
            if (res := attack(self)) == "failed":
                # the action failed, perform the next one
                return self.tactical_model(decisions)
                
            system, ships = res
            print(f"{self.name} reinforced {system._id} with {[s.name for s in ships]}")

            return TacticalAction(self, system, ships)
        
        elif action == "produce":
            if (system_to_use := self.select_production_system()) == "failed":
                print(f"{self.name} attempted to produce, but failed")
                return self.tactical_model(decisions)
            
            return TacticalAction(self, system_to_use, [])

      
    def gain_command_counters(self, n):
        for i in range(n):
            if random.random() > self.disposition["tactic"]:
                self.command_counters["fleet"] += 1
            else:
                self.command_counters["tactic"] += 1

    def activate(self, system):
        self.command_counters["tactic"] -= 1
        system.activate(self)

        self.info = str(self)

    def get_readied_planets(self):
        return [p for p in self.planets if p.is_ready]

    def add_planet(self, planet):
        self.planets.append(planet)
        planet.change_ownership(self)

        self.info = str(self)

    def lose_planet(self, planet):
        if planet in self.planets:
            self.planets.remove(planet)

        self.info = str(self)

    def select_production_system(self):
        candidate_systems = set()
        for planet in self.planets:
            if self.name not in planet.system.command_counters and len([ship for ship in planet.system.space_area if ship.owner != self]) == 0 and planet.has_space_dock: # not blockaded
                candidate_systems.add(planet.system)

        if len(candidate_systems) == 0:
            return "failed"
        return random.choice(list(candidate_systems))
        

    def calculate_planet_value(self, planet):
        resource_value = planet.resources * self.disposition["resources"]
        influence_value = planet.influence * self.disposition["influence"]

        pain = 0
        if planet.owner != self:
            pain += planet.has_space_dock * self.disposition["space dock"]
            pain += planet.num_pds * self.disposition["pds"]
            pain += planet.num_ground_forces * self.disposition["infantry"]
        return resource_value + influence_value + pain

    def pass_turn(self):
        self.passed = True

    def do_status_phase(self):
        self.passed = False
        for planet in self.planets:
            planet.ready()

        self.strategy_card = None
        for ship in self.ships:
            ship.do_status_phase()
        self.score_points() 

    def score_points(self):
        for planet in self.planets:
            self.points += 1
            if planet.name == "Mecatol Rex":
                self.points += 4
        


    def __str__(self):
        
        msg = f"{self.name}\n{'='*len(self.name)}\n"

        msg += f"Points: {self.points}\n"

        msg += "Command Counters\n"
        for key, item in self.command_counters.items():
            msg += f"{key}: {item}\n"

        msg += "\nPlanets\n"
        for planet in self.planets:
            msg += str(planet)

        return msg
        

        