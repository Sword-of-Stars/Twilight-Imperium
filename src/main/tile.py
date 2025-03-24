import pygame
import math
import json

from planet import Planet

class Tile():
    def __init__(self, q, r, s, _id, scale=0.5, offset=(100,100), spacing=5, data=dict()):
        """
        Defines a hexagonal tile
        """
        self.q = q
        self.r = r
        self.s = s

        self.offset_x, self.offset_y = offset
        self.scale = scale
        self.spacing = spacing

        self._id = _id
        self.get_img()

        self.planets = []
        self.initialize_planets(data)

    def get_img(self):
        self.img = pygame.image.load(f"src/data/tiles/ST_{self._id}.png").convert_alpha()

        self.img = pygame.transform.scale_by(self.img, self.scale)
        self.rect = self.img.get_rect()
        self.width = self.rect.width//2 + self.spacing

    def initialize_planets(self, data):
        for planet_data in data["planets"]:
            self.planets.append(Planet(planet_data))


    def get_pixel_position(self):
        x = self.width * (3./2 * self.q) + self.offset_x - self.width//2
        y = self.width * (math.sqrt(3)/2 * self.q  +  math.sqrt(3) * self.r) + self.offset_y - self.width//2
        return (x, y)

    def draw(self, screen):
        #pygame.draw.circle(screen, (255,0,0), self.get_pixel_position(), self.width / 2)
        screen.blit(self.img, self.get_pixel_position())

    def __str__(self):
        msg = f"System {self._id}\n"
        for planet in self.planets:
            msg += str(planet)
        return msg