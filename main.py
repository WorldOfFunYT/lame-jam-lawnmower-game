import pygame
import sys
import math

from scripts.progressBar import Progressbar
from scripts.player import Player
from scripts.minimap import Minimap

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
    self.gridWidth, self.gridHeight = 32, 32
    self.grid = [[0] * self.gridWidth for _ in range(self.gridHeight)]

    self.joysticks = {}

    self.players = [
      Player(controllerType="keyboard", team=1, controllerInfo=[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT], spawnCoords=[0, 0]), 
      Player(controllerType="keyboard", team=2, controllerInfo=[pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d], spawnCoords=[100, 100])
      ]
    # self.players = [Player()]
    cameraSize = (
      self.width if len(self.players) == 1 else self.width/2, 
      self.height if len(self.players) <= 2 else self.height / 2 
      )
    self.cameras = [pygame.Surface(cameraSize) for _ in self.players]
    self.camOffsets = [[0, 0]] * len(self.players)

    self.minimap = Minimap(self.grid, (self.display.get_width() / 2, self.display.get_height() / 2))
    self.progressbar = Progressbar([320, 24], 320, 10)

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

      
      for player in self.players:
        if player.controllerType == "keyboard":
          keys = pygame.key.get_pressed()
          rotationV = 0
          movement = 0
          if keys[player.controlScheme[2]]:
            rotationV = -1
          if keys[player.controlScheme[3]]:
            rotationV = 1
          if keys[player.controlScheme[0]]:
            movement = 1
          if keys[player.controlScheme[1]]:
            movement = -1
          player.movement += movement
          player.rotationDirection += rotationV

      for joystick in self.joysticks.values():
        jid = joystick.get_instance_id()

        for i in range(joystick.get_numaxes()):
          axis = joystick.get_axis(i)
          if abs(axis) <= 0.1:
            axis = 0
          if i == 0:
            for player in self.players:
              if player.controllerType == "controller" and player.controllerId == jid:
                player.rotationDirection = axis
      
        for i in range(joystick.get_numbuttons()):
          button = joystick.get_button(i)
          for player in self.players:
            if player.controllerType == "controller" and player.controllerId == jid:
              if i == 0:
                player.movement += button
              if i == 1:
                player.movement += button * -1
      renderScrolls = [[0, 0]] * len(self.players)
      
      for i, player in enumerate(self.players):
        player.update(self.gridWidth * self.cellSize, self.gridHeight * self.cellSize) #Position rotation 

        team = player.team # Set team colour for grid mapping
        gridX, gridY = int(player.position[0]) // self.cellSize, int(player.position[1]) // self.cellSize
        if 0 <= gridX < self.gridWidth and 0 <= gridY < self.gridHeight and self.grid[gridY][gridX] == 0:
          self.grid[gridY][gridX] = team # Set grid colour

        
        self.camOffsets[i][0] = player.getCenter()[0] - self.cameras[i].get_width() / 2 # 
        self.camOffsets[i][1] = player.getCenter()[1] - self.cameras[i].get_height() / 2
        renderScrolls[i] = (int(self.camOffsets[i][0]), int(self.camOffsets[i][1]))

      for i, camera in enumerate(self.cameras):
        
        camera.fill((0, 10, 0))
        for y in range(max(renderScrolls[i][1] // self.cellSize, 0), min((renderScrolls[i][1] + camera.get_height()) // self.cellSize + 1, len(self.grid))):
          for x in range(max(renderScrolls[i][0] // self.cellSize, 0), min((renderScrolls[i][0] + camera.get_width()) // self.cellSize + 1, len(self.grid[y]))):
            colour = (0, 0, 0)
            if self.grid[y][x] == 1:
              colour = (0, 0, 128)
            if self.grid[y][x] == 2:
              colour = (128, 0, 0)
            pygame.draw.rect(camera, colour, (x * self.cellSize - renderScrolls[i][0], y * self.cellSize - renderScrolls[i][1], self.cellSize, self.cellSize))


        for player in self.players:
          player.render(self.cameras[i], renderScrolls[i])
        
        self.display.blit(camera, (self.display.get_width() // 2 if (i + 1) % 2 == 0 else 0, self.display.get_height() // 2 if (i + 1) > 2 else 0))

      playerGridCoordinates = [[player.team, (int(player.position[0]) // self.cellSize, int(player.position[1]) // self.cellSize)] for player in self.players]

      self.minimap.render(self.display, playerGridCoordinates)

      team1Percent = len([item for row in self.grid for item in row if item == 1]) / (self.gridWidth * self.gridHeight)
      team2Percent = len([item for row in self.grid for item in row if item == 2]) / (self.gridWidth * self.gridHeight)
      
      self.progressbar.render(self.display, team1Percent, team2Percent)

      self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
      pygame.display.update()
      print(f'{round(team1Percent * 100, 2)}%-{round(team2Percent * 100, 2)}%') 
      # print(self.clock.get_fps())
      self.clock.tick(60)

Game().run()