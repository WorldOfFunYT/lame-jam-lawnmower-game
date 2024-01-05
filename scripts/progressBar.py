import pygame

class Progressbar:
  def __init__(self, size=[100, 10], centerX=320, topY=0):
    self.size = [size[0] + 2, size[1] + 2]
    self.coords = (centerX - size[0] // 2 + 1, topY)

    self.colours = {
      'empty': (32, 32, 32, 128),
      'left': (10, 10, 210),
      'right': (210, 10, 10),
      'outline': (255, 255, 255)
    }
    self.bar = pygame.Surface(size).convert_alpha()

  def render(self, surf, left=0.25, right=0.25):
    self.bar.fill(self.colours['outline'])
    self.bar.fill(self.colours['empty'], (1, 1, self.size[0] - 4, self.size[1] - 4))

    self.bar.fill(self.colours['left'], (1, 1, int((self.size[0] - 4) * left), (self.size[1] - 4)))
    self.bar.fill(self.colours['right'], ((self.size[0] - 4) - int((self.size[0] - 4) * right), 1, int((self.size[0] - 4) * right), (self.size[1] - 4)))

    surf.blit(self.bar, self.coords)