from random import randint
from typing import List

class Ship():
    """
    a class to represent a ship in the game

    NOTE: later, this should inherit from UNIT
    """
    def __init__(self, owner=None, **kwargs):
        #===== Immutable Properties =====#
        self.name = kwargs["name"]
        self.combat = kwargs["combat"]
        self.move = kwargs["move"]
        self.capacity = kwargs["capacity"]
        self.cost = kwargs["cost"]

        self.MAXHEALTH = 2 if kwargs["sustain"] else 1

        #===== Mutable Properties =====#
        self.owner = owner
        self.health = self.MAXHEALTH
        self.in_cargo : List[Ship] = []
        self.system = kwargs["system"]

    def set_ownership(self, owner):
        self.owner = owner

    def make_attack_roll(self):
        """
        returns the result of a single attack roll
        """
        return randint(1, 10) >= self.combat
    
    def move_to_system(self, system):
        self.system = system
        system.place_in_space_area(self)

    def assign_hit(self, hit: int = 1):
        """
        reduces the health of the ship by the given amount
        """
        for _ in range(hit):
            self.health -= 1
            if self.health <= 0:
                self.destroy()
                break

    def destroy(self):
        """
        destroys the ship
        """
        self.owner = None
        self.health = 0

        for unit in self.in_cargo:
            unit.destroy()
        self.in_cargo = []

    def __str__(self):
        msg = f"[{self.owner.name}] {self.name} "
        msg += "is sustaining damage " if (self.MAXHEALTH == 2 and self.health == 1) else ""
        msg += f"carrying {len(self.in_cargo)} ships" if self.capacity != 0 else ""

        return msg
    

