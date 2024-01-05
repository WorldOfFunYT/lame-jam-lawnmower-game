import pygame
import math

class Player:
  def __init__(self, spawnCoords=(100, 100), team="blue", rotation=0):
    self.spawnCoords = spawnCoords
    self.position = spawnCoords
    self.team = team
    match team:
      case "blue":
        self.colour = (30, 150, 220)
      case "red":
        self.colour = (220, 30, 30)
    
    self.rotation = rotation
    self.rotationDirection = 0
    self.rotationVelocity = 0

    self.movement = 0
    self.velocity = 0
    self.speed = 1

    self.sprite = pygame.Surface((20, 20)).convert_alpha()
    self.sprite.fill(self.colour)

  def update(self):
    self.rotationVelocity += self.rotationDirection * 0.1
    self.rotationVelocity = max(min(self.rotationVelocity, 4), -4)
    self.rotation -= self.rotationVelocity * 2

    self.movement *= -1
    self.velocity += self.movement * 0.1
    self.velocity = max(min(self.velocity, 3), -3)

    theta = math.radians(self.rotation) * -1

    dx = self.speed * math.cos(theta) * self.velocity
    dy = self.speed * math.sin(theta) * self.velocity
    self.position = (self.position[0] + dx, self.position[1] + dy)

    if self.movement == 0:
      if self.velocity > 0.01:
        self.velocity *= 0.95
      else:
        self.velocity = 0
    self.movement = 0

    if self.rotationDirection == 0:
      self.rotationVelocity *= 0.90
    self.rotationDirection = 0

    print(self.velocity, self.rotationVelocity)
  
  def render(self, surf):
    rotated_surf = pygame.transform.rotate(self.sprite, self.rotation)
    surf.blit(rotated_surf, (self.position[0] - rotated_surf.get_width() / 2, self.position[1] - rotated_surf.get_height() / 2))