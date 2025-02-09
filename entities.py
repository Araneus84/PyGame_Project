import pygame
from constants import TILE_SIZE

class Unit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def move(self, dx, dy, walls):
        new_x = self.x + dx
        new_y = self.y + dy
        new_rect = pygame.Rect(new_x * TILE_SIZE, new_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        
        if not any(wall.colliderect(new_rect) for wall in walls):
            self.x = new_x
            self.y = new_y
            self.rect.x = self.x * TILE_SIZE
            self.rect.y = self.y * TILE_SIZE