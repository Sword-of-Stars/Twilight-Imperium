import pygame, sys

class Planet():
    def __init__(self, data):
        # immutable characteristics
        self.name = data["name"]
        self.resources = data["resources"]
        self.influence = data["influence"]

        # every planet is worth 1 point, but Mecatol is worth 5
        self.points = 1
        if self.name == "Mecatol Rex":
            self.points = 5

        # mutable characteristics
        self.has_space_dock = False
        self.num_pds = 0
        self.num_ground_forces = 0
        self.owner = None # string
        self.is_ready = False

    def change_ownership(self, player):
        self.owner = player

    def ready(self):
        self.is_ready = True

    def exhaust(self):
        self.is_ready = False

    def place_space_dock(self):
        self.has_space_dock = True
        print("placed a space dock")

    def place_ground_forces(self, n):
        self.num_ground_forces += n

    def __str__(self):
        msg = f"{self.name}\n{'='*len(self.name)}\n"
        msg += f"> Influence: {self.influence}\n"
        msg += f"> Resources: {self.resources}\n"
        msg += f"> Controlled By: {self.owner.name if self.owner != None else None}\n"
        msg += f"> Ground Forces: {self.num_ground_forces}\n"
        msg += f"> Has Space Dock" if self.has_space_dock else ""
        return msg