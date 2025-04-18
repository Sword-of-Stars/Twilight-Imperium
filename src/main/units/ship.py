from random import randint
import copy

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
        self.special_combat = kwargs.get("special_combat", None)
        self.special = kwargs.get("special", None)

        self.MAXHEALTH = 2 if kwargs["sustain"] else 1

        #===== Mutable Properties =====#
        self.owner = owner
        self.health = self.MAXHEALTH
        self.in_cargo = []
        self.system = kwargs.get("system", None)

    def set_ownership(self, owner):
        self.owner = owner

    def make_attack_roll(self):
        """
        returns the result of a single attack roll
        """
        return randint(1, 10) >= self.combat
    
    def move_to_system(self, system):
        if self.system != None:
            self.system.remove_from_space_area(self)
        self.system = system
        system.place_in_space_area(self)

        for unit in self.in_cargo:
            unit.move_to_system(system)

    def assign_hit(self, hit: int = 1):
        """
        reduces the health of the ship by the given amount
        """
        for _ in range(hit):
            self.health -= 1
            if self.health <= 0:
                self.destroy()
                break

    def add_to_cargo(self, unit):
        """
        adds a unit to the ship's cargo
        """
        if self.capacity != 0 and len(self.in_cargo) < self.capacity:
            self.in_cargo.append(unit)
            return True
        return False

    def destroy(self):
        """
        destroys the ship
        """
        self.owner = None
        self.health = 0

        for unit in self.in_cargo:
            unit.destroy()
        self.in_cargo = []

    def do_status_phase(self):
        self.health = self.MAXHEALTH

    def get_reachable_tiles(self):
        """
        returns a list of tiles the ship can reach
        """
        if self.move == 0:
            return []
        if self.move == 1:
            return self.system.neighbors
        elif self.move == 2:
            return list(set([tile for tile in self.system.neighbors]))
        
    def __deepcopy__(self, memo):
        # Create a new Ship with the same properties, skipping deepcopy of 'owner'
        copied = Ship(
            name=self.name,
            combat=self.combat,
            move=self.move,
            capacity=self.capacity,
            cost=self.cost,
            special_combat=self.special_combat,
            special=self.special,
            sustain=(self.MAXHEALTH == 2),
        )
        copied.health = self.health
        copied.in_cargo = ["fighter" for f in self.in_cargo if f.name == "fighter"]
        memo[id(self)] = copied
        return copied


    def __str__(self):
        msg = f"[{self.owner.name}] {self.name} "
        msg += "is sustaining damage " if (self.MAXHEALTH == 2 and self.health == 1) else ""
        msg += f"carrying {len(self.in_cargo)} ships" if self.capacity != 0 else ""

        return msg
    

