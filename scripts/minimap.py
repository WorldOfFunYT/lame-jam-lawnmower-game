import pygame

class Minimap:
  def __init__(self, grid, centerCoords):
    self.grid = grid
    self.gridHeight = len(grid)
    self.gridWidth = len(grid[0])
    self.centerCoords = centerCoords

    self.mapWidth, self.mapHeight = 128, 128

    self.colours = {
      'default': (32, 32, 32, 127),
      'team1': (10, 10, 230, 180),
      'team2': (230, 10, 10, 180),
      'team1player': (0, 0, 255),
      'team2player': (255, 0, 0)
    }

    self.map = pygame.Surface((self.gridWidth, self.gridHeight)).convert_alpha()

  def render(self, surf, playerCoordinates):
    self.map.fill(self.colours['default'])

    for y in range(self.gridHeight):
      for x in range(self.gridWidth):
        if self.grid[y][x] != 0:
          self.map.fill(self.colours[f'team{self.grid[y][x]}'], (x, y, 1, 1))
    
    for coordinate in playerCoordinates:
      self.map.fill(self.colours[f'team{coordinate[0]}player'], (coordinate[1], (1, 1)))

    surf.blit(pygame.transform.scale(self.map, (self.mapWidth, self.mapHeight)), (self.centerCoords[0] - self.mapWidth // 2, self.centerCoords[1] - self.mapHeight // 2))