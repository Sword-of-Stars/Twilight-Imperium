import pygame
import math

class Tile():
    def __init__(self, q, r, s, _id, scale=0.5, offset=(100,100)):
        """
        Defines a hexagonal tile
        """
        self.q = q
        self.r = r
        self.s = s

        self.offset_x, self.offset_y = offset
        self.scale = scale
        self.spacing = 5

        self.id_to_img(_id)

    def id_to_img(self, _id):
        self.img = pygame.image.load(f"src/data/tiles/ST_{_id}.png").convert_alpha()

        self.img = pygame.transform.scale_by(self.img, self.scale)
        self.rect = self.img.get_rect()
        self.width = self.rect.width//2 + self.spacing



    def get_pixel_position(self):
        x = self.width * (3./2 * self.q) + self.offset_x - self.width
        y = self.width * (math.sqrt(3)/2 * self.q  +  math.sqrt(3) * self.r) + self.offset_y - self.width
        return (x, y)

    def draw(self, screen):
        #pygame.draw.circle(screen, (255,0,0), self.get_pixel_position(), self.width / 2)
        screen.blit(self.img, self.get_pixel_position())