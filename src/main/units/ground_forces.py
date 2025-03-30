from random import randint

class GroundForce():
    def __init__(self, owner="NONE", **kwargs):
         #===== Immutable Properties =====#
        self.name = "infantry"
        self.combat = 6
        self.cost = 0.5
        self.capacity = 0

        #===== Mutable Properties =====#
        self.owner = owner
        self.in_cargo = False
        #self.planet = kwargs["planet"]

    def set_ownership(self, owner):
        self.owner = owner

    def make_attack_roll(self):
        """
        returns the result of a single attack roll
        """
        return randint(1, 10) >= self.combat
    
    def move_to_planet(self, planet):
        self.planet = planet
        planet.place_ground_forces(1)

    def destroy(self):
        """
        destroys the infantry
        """
        self.owner = None
        self.health = 0

    def __str__(self):
        return f"[{self.owner.name}] {self.name} on the planet {self.planet.name}"
    