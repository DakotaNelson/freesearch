import pygame
import tiles

class View:
    def __init__(self, size, grid):
        self.size = size
        h = size
        w = size
        self.squareHeight = h / grid.h # how big to make each square on the map
        self.squareWidth = w / grid.w
        self.maxH = grid.h - 1
        self.maxW = grid.w - 1
        self.screen = pygame.display.set_mode((w,h))
        pygame.display.set_caption("Alcatraz - Challenge 3")

    def update(self, data):
        self.screen.fill((255,255,255))

        #draw tiles for map
        for row in data.grid:
            for tile in row:
                rect = (tile.x * self.squareWidth,
                        tile.y * self.squareHeight,
                        self.squareWidth,
                        self.squareHeight)
                pygame.draw.rect(self.screen, tile.color(), rect, 0)

        # and make a screen refresh happen
        pygame.display.update()

