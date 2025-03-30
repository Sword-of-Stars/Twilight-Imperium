from typing import List
from .ship import Ship

class SpaceDock():
    """
    a class to represent a ship in the game

    NOTE: later, this should inherit from UNIT
    """
    def __init__(self, owner="Player 1", **kwargs):

        #===== Immutable Properties =====#
        self.capacity = 3
        self.production_modifier = 3 # a spack dock can produce 3 more units than the resource value of a planet

        #===== Mutable Properties =====#
        self.owner = owner
        self.in_cargo : List[Ship] = []

    def set_ownership(self, owner):
        self.owner = owner

    def place_on_planet(self, planet):
        self.planet = planet
        planet.place_space_dock()

    def get_production_capacity(self):
        return self.production_modifier + self.planet.resources

    def destroy(self):
        """
        destroys the ship
        """
        self.owner = None
      
        for unit in self.in_cargo:
            unit.destroy()
        self.in_cargo = []

    def __str__(self):
        return f"[{self.owner.name}] {self.name} with {self.health} health carrying {len(self.in_cargo)} ships"
    

