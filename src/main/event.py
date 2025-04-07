from combat_sim import simulate_space_combat
from production import produce

from units.ground_forces import GroundForce
from units.unit_types import Fighter, Destroyer, Cruiser, Carrier, Dreadnought, WarSun

class Event():
    def __init__(self, player):
        self.player = player

class Pass(Event):
    def __init__(self, player):
        super().__init__(player)

    def execute(self):
        self.player.pass_turn()
        return [self.__str__()]

    def __str__(self):
        return f"[SYSTEM] {self.player.name} passed"

class TacticalAction(Event):
    def __init__(self, player, active_system, ships):
        super().__init__(player)

        self.active_system = active_system

        self.components = [
            Activation(player, active_system),
            Movement(ships, active_system, player),
            SpaceCombat(active_system, player),
            Invasion(active_system, player),
            Production(active_system, player)
        ]

    def execute(self):
        out = []
        for component in self.components:
            component.execute()
            out.append(str(component))
        return out

class Activation():
    def __init__(self, player, active_system):
        self.player = player
        self.active_system = active_system

    def execute(self):
        self.player.activate(self.active_system)

    def __str__(self):
        return f"[ACTIVATION] {self.player.name} activated system {self.active_system._id}"
    
class Movement():
    def __init__(self, ships, active_system, player):

        self.ships = ships
        self.active_system = active_system
        self.player = player

    def execute(self):
        for ship in self.ships:
            ship.move_to_system(self.active_system)

    def __str__(self):
        if len(self.ships) == 0:
            return f"[MOVEMENT] {self.player.name} skipped the movement step"
        return f"[MOVEMENT] {self.player.name} moved {[x.name for x in self.ships]} into system {str(self.active_system._id)}"
    
class SpaceCombat():
    def __init__(self, active_system, player):
        self.active_system = active_system
        self.player = player

        self.winner = None

    def execute(self):
        # sort ships in the space area by owner
        ships = sorted(self.active_system.space_area, key=lambda x: x.owner._id)

        fleet_1 = [ship for ship in ships if ship.owner == self.player]
        fleet_2 = [ship for ship in ships if ship.owner != self.player]

        if fleet_2 == []:
            return

        self.winner, fleet_1, fleet_2 = simulate_space_combat(fleet_1, fleet_2)


        '''for ship in self.active_system.space_area:
            if ship not in fleet_1 and ship not in fleet_2:
                ship.destroy()'''

    def __str__(self):
        if self.winner == None:
            return f"[SPACE COMBAT] {self.player.name} skipped the space combat step"
        return f"[SPACE COMBAT] {self.player.name} {'won' if self.winner == 1 else "lost"} the space combat in {str(self.active_system._id)}"
    
class Invasion():
    def __init__(self, active_system, player):
        self.active_system = active_system
        self.player = player

        self.success = []

    def execute(self):
        planets = sorted(self.active_system.planets, key=lambda planet: self.player.calculate_planet_value(planet), reverse=True)
        # get the number of ground forces in the system
        ground_forces = sum([
            len([x for x in ship.in_cargo if x.name == "infantry"]) for ship in self.active_system.space_area if ship.owner == self.player
        ])

        available_bombardment = []
        for ship in self.active_system.space_area:
            if ship.special_combat != None and "bombardment" in ship.special_combat:
                available_bombardment.append(ship)

        # bombard the planets
        for bombardment in available_bombardment:
            for planet in planets:
                if planet.owner != self.player:
                    if planet.num_ground_forces > 0 and ((planet.num_pds == 0) or (planet.num_pds > 0 and bombardment.name == "warsun")): # only bombard if there are ground forces
                        hits = bombardment.bombard()
                        planet.remove_n_ground_forces(hits)
                        break

        # invade the planets
        available_soldiers = []
        for ship in self.active_system.space_area:
            if ship.owner == self.player:
                if ship.in_cargo != []:
                    for unit in reversed(ship.in_cargo):
                        if unit.name == "infantry":
                            available_soldiers.append(unit)
                            ship.in_cargo.remove(unit)


        for i, planet in enumerate(planets):
            if planet.owner != self.player:
                if planet.num_ground_forces == 0:
                    # invade the planet with a single infantry
                    if len(available_soldiers) > 0:
                        available_soldiers.pop().move_to_planet(planet)
                        self.player.add_planet(planet)
                        planet.change_ownership(self.player)
                        self.success.append(planet.name)
                else:
                    # invade the planet with the remaining ground forces
                    if len(available_soldiers) > 0:
                        if len(available_soldiers) > planet.num_ground_forces:
                            planet.remove_ground_forces(planet.num_ground_forces)
                            for _ in range(planet.num_ground_forces):
                                available_soldiers.pop()
                            for i in available_soldiers:
                                i.move_to_planet(planet)
                               
                            self.player.add_planet(planet)
                            planet.change_ownership(self.player)
                            self.success.append(planet.name)
                        else: # the invasion fails
                            planet.remove_ground_forces(len(available_soldiers))
                            del available_soldiers[:]
                            
        # return the remaining ground forces while there's enough capacoty
        for ship in self.active_system.space_area:
            if ship.owner == self.player:
                while len(ship.in_cargo) < ship.capacity and len(available_soldiers) > 0:
                    ship.add_to_cargo(available_soldiers.pop())


    def __str__(self):
        if self.success == []:
            return f"[INVASION] {self.player.name} failed to invade any planets in {str(self.active_system._id)}"
        return f"[INVASION] {self.player.name} successfully invaded {self.success} in {str(self.active_system._id)}"
    
class Production():
    def __init__(self, active_system, player):
        self.active_system = active_system
        self.player = player

        self.produced = []

    def execute(self):
        for planet in self.active_system.planets:
            if not planet.has_space_dock:
                break
        else:
            units, planets_exhausted = produce(self.player, self.active_system)
            for planet in planets_exhausted:
                planet.exhaust()

            def create_and_place(ship):
                x = ship(system=self.active_system)
                x.set_ownership(self.player)
                self.player.ships.append(x)
                x.move_to_system(self.active_system)

            for unit, num in units.items():
                if num == None:
                    continue
                if unit == "infantry":
                    for planet in self.active_system.planets:
                        if planet.has_space_dock:
                            for i in range(int(num)):
                                x = GroundForce()
                                x.move_to_planet(planet)

                elif unit == "fighter":
                    for ship in self.active_system.space_area:
                        if ship.capacity - len(ship.in_cargo) > 0:
                            if num > 0:
                                x = Fighter()
                                x.move_to_system(ship)
                                num -= 1
                elif unit == "destroyer":
                    create_and_place(Destroyer)
                elif unit == "cruiser":
                    create_and_place(Cruiser)
                elif unit == "carrier":
                    create_and_place(Carrier)
                elif unit == "dreadnought":
                    create_and_place(Dreadnought)
                elif unit == "warsun":
                    create_and_place(WarSun)
                else:
                    print(f"Reject: {unit}")


            

            self.produced = units

    def __str__(self):
        return f"[PRODUCTION] {self.player.name} produced the following units: {self.produced}"
    

class StrategicAction(Event):
    def __init__(self, player):
        super.__init__(player)

class Leadership(StrategicAction):
    def __init__(self, player):
        super.__init__(player)

    def execute(self):
        self.player.gain_command_counters(3)

        # offer other players the chance to take secondary

    def secondary(self):
        pass

class Diplomacy(StrategicAction):
    def __init__(self, player, chosen_system, all_players=[]):
        super().__init__(self, player)

        self.chosen_system = chosen_system
        self.all_players = all_players

    def execute(self):
        for player in filter(lambda x: x != self.player, self.all_players):
            player.activate(self.chosen_system)

        self.chosen_system.deactivate() # this doesn't remove ccs

        # players

    def secondary(self):
        pass

class Construction(StrategicAction):
    def __init__(self, player, chosen_system, placement={}):
        super.__init__(self, player)

        self.chosen_system = chosen_system
        self.placement = placement

    def execute(self):
        for planet, structure in self.placement.items():
            planet.add_structure(structure)

        # players

    def secondary(self):
        pass

class Warfare(StrategicAction):
    def __init__(self, player, chosen_system):
        super.__init__(self, player)

        self.chosen_system = chosen_system

    def execute(self):
       self.chosen_system.remove_command_counter(self.player)

    def secondary(self):
        pass