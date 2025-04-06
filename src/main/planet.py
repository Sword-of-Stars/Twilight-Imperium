import pygame, sys

class Planet():
    def __init__(self, data, system):
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
        self.ground_forces = []
        self.owner = None # string
        self.is_ready = False

        self.system = system # tile

    def change_ownership(self, player):
        self.owner = player

    def ready(self):
        self.is_ready = True

    def exhaust(self):
        self.is_ready = False

    def place_space_dock(self):
        self.has_space_dock = True

    def place_pds(self):
        self.num_pds += 1

    def place_ground_forces(self, infantry):
        self.num_ground_forces += 1
        self.ground_forces.append(infantry)

    def remove_ground_forces(self, infantry):
        self.num_ground_forces -= 1
        self.ground_forces = [x for x in self.ground_forces if x != infantry]

    def get_encoding(self):
        """
        Encodes the planet's state as a feature vector.
        Returns:
            list: [resource, influence, has_space_dock, has_pds, infantry]
        """
        return [
            self.resources,
            self.influence,
            int(self.has_space_dock),
            int(self.num_pds),
            self.num_ground_forces,
            self.owner._id if self.owner != None else -1
        ]

    def __str__(self):
        msg = f"{self.name}\n{'='*len(self.name)}\n"
        msg += f"> Influence: {self.influence}\n"
        msg += f"> Resources: {self.resources}\n"
        msg += f"> Controlled By: {self.owner.name if self.owner != None else None}\n"
        msg += f"> Ground Forces: {self.num_ground_forces}\n"
        msg += f"> Has Space Dock\n" if self.has_space_dock else ""
        msg += f"> Has {self.num_pds} PDS\n" if self.num_pds != 0 else ""
        return msg