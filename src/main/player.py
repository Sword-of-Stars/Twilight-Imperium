from units import Carrier, Cruiser, Destroyer, Dreadnought, WarSun, Fighter, SpaceDock, GroundForce, Ship

class Player:
    def __init__(self, name, starting_system, starting_units=[]):
        self.name = name
        
        self.points = 0
        self.planets = []

        self.command_counters = {
            "tactic": 3,
            "fleet": 3,
            "strategy": 2
        }

        for planet in starting_system.planets:
            self.add_planet(planet)

        self.initialize_units(starting_units, starting_system)
        self.info = str(self)

    def initialize_units(self, starting_units, starting_system):
        # place starting units in the home system
        for unit in starting_units:
            unit.set_ownership(self)
            if isinstance(unit, SpaceDock):
                unit.place_on_planet(self.planets[0])
            elif isinstance(unit, Ship):
                unit.move_to_system(starting_system)
            elif isinstance(unit, GroundForce):
                unit.move_to_planet(self.planets[0])

    def take_action(self):
        '''
        The meat and potatoes of this simulation
        '''
        pass

    def gain_command_counters(self, n):
        # MAKE DECISION
        #self.command_counters += n
        pass

    def activate(self, system):
        system.activate(self)

        self.info = str(self)

    def add_planet(self, planet):
        self.planets.append(planet)
        planet.change_ownership(self)

        self.info = str(self)

    def lose_planet(self, planet):
        if planet in self.planets:
            self.planets.remove(planet)

        self.info = str(self)

    def __str__(self):
        
        msg = f"{self.name}\n{'='*len(self.name)}\n"

        msg += f"Points: {self.points}\n"

        msg += "Command Counters\n"
        for key, item in self.command_counters.items():
            msg += f"{key}: {item}\n"

        msg += "\nPlanets\n"
        for planet in self.planets:
            print(str(planet))
            msg += str(planet)

        return msg
        

        