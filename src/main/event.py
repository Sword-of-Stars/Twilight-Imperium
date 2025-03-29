from simulation import Simulation
from tile import Tile
from player import Player

game_map = Simulation.game_map

class Event():
    def __init__(self, player: Player):
        self.player = player

class TacticalAction(Event):
    def __init__(self, player, active_system: Tile, ships):
        super.__init__(self, player)

        self.active_system = active_system

        self.components = [
            Activation(),
            Movement(ships),
        ]

class Activation(TacticalAction):
    def __init__(self):
        super.__init__(self)

    def execute(self):
        self.player.activate(self.active_system)

    def __str__(self):
        return f"[ACTIVATION] {self.player} activated {str(self.active_system)}"
    
class Movement(TacticalAction):
    def __init__(self, ships):
        super.__init__(self)

        self.ships = ships

    def execute(self):
        for ship in self.ships:
            ship.move(self.active_system)

    def __str__(self):
        if len(self.ships) == 0:
            return f"[MOVEMENT] {self.player} skipped the movement step"
        return f"[MOVEMENT] {self.player} moved {self.ships} into {str(self.active_system)}"
    
class SpaceCombat(TacticalAction):
    def __init__(self):
        super.__init__(self)

    def execute(self):
        # do combat
        pass

    def __str__(self):
        return f"[SPACE COMBAT] {self.player} moved {self.ships} into {str(self.active_system)}"
    
class Invasion(TacticalAction):
    def __init__(self):
        super.__init__(self)

    def execute(self):
        # do combat
        pass

    def __str__(self):
        return f"[INVASION] {self.player} moved {self.ships} into {str(self.active_system)}"
    
class Production(TacticalAction):
    def __init__(self):
        super.__init__(self)

    def execute(self):
        # do produce
        pass

    def __str__(self):
        return f"[PRODUCTION] {self.player} moved {self.ships} into {str(self.active_system)}"
    

class StrategicAction(Event):
    def __init__(self, player: Player):
        super.__init__(self, player)

class Leadership(StrategicAction):
    def __init__(self, player: Player):
        super.__init__(self, player)

    def execute(self):
        self.player.gain_command_counters(3)

        # offer other players the chance to take secondary

    def secondary(self):
        pass

class Diplomacy(StrategicAction):
    def __init__(self, player: Player, chosen_system: Tile):
        super.__init__(self, player)

        self.chosen_system = chosen_system

    def execute(self):
        for player in filter(lambda x: x != self.player, Simulation.players):
            player.activate(self.chosen_system)

        self.chosen_system.deactivate() # this doesn't remove ccs

        # players

    def secondary(self):
        pass

class Construction(StrategicAction):
    def __init__(self, player: Player, chosen_system: Tile, placement={}):
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
    def __init__(self, player: Player, chosen_system: Tile):
        super.__init__(self, player)

        self.chosen_system = chosen_system

    def execute(self):
       self.chosen_system.remove_command_counter(self.player)

    def secondary(self):
        pass