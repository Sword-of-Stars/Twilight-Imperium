from typing import List
from ship import Ship

class SpaceDock():
    """
    a class to represent a ship in the game

    NOTE: later, this should inherit from UNIT
    """
    def __init__(self, owner="Player 1", **kwargs):

        #===== Immutable Properties =====#
        self.name = kwargs["name"]
        self.move = kwargs["movement"]
        self.capacity = kwargs["capacity"]

        #===== Mutable Properties =====#
        self.owner = owner
        self.in_cargo : List[Ship] = []
        self.planet = kwargs["planet"]

    def destroy(self):
        """
        destroys the ship
        """
        self.owner = None
      
        for unit in self.in_cargo:
            unit.destroy()
        self.in_cargo = []

    def __str__(self):
        return f"[{self.owner}] {self.name} with {self.health} health carrying {len(self.in_cargo)} ships"
    

