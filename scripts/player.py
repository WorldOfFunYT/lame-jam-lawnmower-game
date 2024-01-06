import pygame
import math

class Player:
  def __init__(self, sprites, spawnCoords=[100, 100], team=1, rotation=0, controllerType="controller", controllerInfo=[0]):
    self.spawnCoords = list(spawnCoords)
    self.position = list(spawnCoords)
    self.team = team

    self.images = sprites

    self.controllerType = controllerType
    if controllerType == "controller":
      self.controllerId = controllerInfo[0]
    elif controllerType == "keyboard":
      self.controlScheme = controllerInfo[:4]
    match team:
      case 1:
        self.colour = (30, 150, 220)
      case 2:
        self.colour = (220, 30, 30)
    
    self.rotation = rotation
    self.rotationDirection = 0
    self.rotationVelocity = 0

    self.movement = 0
    self.velocity = 0
    self.speed = 1

    self.sprite = pygame.Surface((20, 20)).convert_alpha()
    self.sprite.fill(self.colour)

  def getCenter(self):
    return (self.position[0] + self.sprite.get_width() / 2, self.position[1] + self.sprite.get_height() / 2)

  def update(self, maxX, maxY):
    self.movement *= -1
    self.velocity += self.movement * 0.1
    self.velocity = max(min(self.velocity, 3), -3)

    self.rotationVelocity += self.rotationDirection * 0.1 * abs(self.velocity / 3)
    self.rotationVelocity = max(min(self.rotationVelocity, 4), -4)
    self.rotation -= self.rotationVelocity * 2

    theta = math.radians(self.rotation) * -1

    dx = self.speed * math.cos(theta) * self.velocity
    dy = self.speed * math.sin(theta) * self.velocity
    self.position[0] = self.position[0] + dx
    if self.position[0] < 0 + self.sprite.get_width() / 2:
      self.position[0] = 0 + self.sprite.get_width() / 2
    if self.position[0] > maxX - self.sprite.get_width() / 2:
      self.position[0] = maxX - self.sprite.get_width() / 2

    self.position[1] = self.position[1] + dy
    if self.position[1] < 0 + self.sprite.get_height() / 2:
      self.position[1] = 0 + self.sprite.get_height() / 2
    if self.position[1] > maxY - self.sprite.get_height() / 2:
      self.position[1] = maxY - self.sprite.get_height() / 2

    if self.movement == 0:
      if abs(self.velocity) > 0.00001:
        self.velocity *= 0.98
      else:
        self.velocity = 0
    self.movement = 0

    if self.rotationDirection == 0:
      if abs(self.rotationVelocity > 0.01):
        self.rotationVelocity *= 0.90
      else:
        self.rotationVelocity = 0
    self.rotationDirection = 0
  
  def render(self, surf, spread=1, offset=(0, 0)):
    for i, img in enumerate(self.images):
      rotated_img = pygame.transform.rotate(img, self.rotation)
      surf.blit(rotated_img, (self.position[0] - rotated_img.get_width() // 2 - offset[0],
                self.position[1] - rotated_img.get_height() // 2 - i * spread - offset[1]))