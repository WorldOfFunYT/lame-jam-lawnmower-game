import pygame
import sys
import math

from scripts.player import Player

SCREEN_SIZE_MULT = 2

class Game:
  def __init__(self):
    self.width = 640
    self.height = 480
    pygame.init()

    self.screen = pygame.display.set_mode((self.width * SCREEN_SIZE_MULT, self.height * SCREEN_SIZE_MULT))
    self.display = pygame.Surface((self.width, self.height))

    self.clock = pygame.time.Clock()

    self.cellSize = 20
    self.gridWidth, self.gridHeight = self.width // self.cellSize, self.height // self.cellSize
    self.grid = [[0] * self.gridWidth for _ in range(self.gridHeight)]

    self.joysticks = {}

    self.player1 = Player()

  def run(self):
    while True:
      self.display.fill((0, 0, 10))

      for event in pygame.event.get():
        match event.type:
          case pygame.QUIT:
            pygame.quit()
            sys.exit()
            break
          case pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            self.joysticks[joy.get_instance_id()] = joy
            break
          case pygame.JOYDEVICEREMOVED:
            del self.joysticks[event.instance_id]
            break

      for joystick in self.joysticks.values():
        jid = joystick.get_instance_id()

        for i in range(joystick.get_numaxes()):
          axis = joystick.get_axis(i)
          if abs(axis) <= 0.1:
            axis = 0
          if i == 0:
            self.player1.rotationDirection = axis
      
        for i in range(joystick.get_numbuttons()):
          button = joystick.get_button(i)
          if i == 0:
            self.player1.movement += button
          if i == 1:
            self.player1.movement += button * -1
      
      self.player1.update()

      gridX, gridY = int(self.player1.position[0]) // self.cellSize, int(self.player1.position[1]) // self.cellSize
      if 0 <= gridX < self.gridWidth and 0 <= gridY < self.gridHeight:
        self.grid[gridY][gridX] = 1

      for y in range(self.gridHeight):
        for x in range(self.gridWidth):
          colour = (0, 0, 0)
          if self.grid[y][x] == 1:
            colour = (0, 0, 128)
          if self.grid[y][x] == 2:
            colour = (128, 0, 0)
          pygame.draw.rect(self.display, colour, (x * self.cellSize, y * self.cellSize, self.cellSize, self.cellSize))

      self.player1.render(self.display)

      self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
      pygame.display.update()
      self.clock.tick(60)

Game().run()