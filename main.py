import pygame
import sys
import math

from scripts.utils import loadImage
from scripts.progressBar import Progressbar
from scripts.player import Player
from scripts.minimap import Minimap

SCREEN_SIZE_MULT = 2


# Menu ids
PLAYER_SELECT = 0
CONTROLLER_SELECT = 1
GAME = 2

class Game:
  def __init__(self):
    self.width = 640
    self.height = 480
    pygame.init()

    self.currentMenu = 0

    self.screen = pygame.display.set_mode((self.width * SCREEN_SIZE_MULT, self.height * SCREEN_SIZE_MULT))
    self.display = pygame.Surface((self.width, self.height))

    self.clock = pygame.time.Clock()

    self.cellSize = 20
    self.gridWidth, self.gridHeight = 32, 32
    self.grid = [[0] * self.gridWidth for _ in range(self.gridHeight)]

    self.assets = {
      '2players': loadImage('buttons/button2'),
      '3players': loadImage('buttons/button3'),
      '4players': loadImage('buttons/button4'),
      '2playersPressed': loadImage('buttons/button2pressed'),
      '3playersPressed': loadImage('buttons/button3pressed'),
      '4playersPressed': loadImage('buttons/button4pressed'),
      'keyboard': loadImage('buttons/keyboard'),
      'controller': loadImage('buttons/controller'),
      'keyboardPressed': loadImage('buttons/keyboardPressed'),
      'controllerPressed': loadImage('buttons/controllerPressed'),
    }

    pygame.joystick.init()
    self.joysticks = {}
    for x in range(pygame.joystick.get_count()):
      joy = pygame.joystick.Joystick(x)
      joy.init()
      self.joysticks[joy.get_instance_id()] = joy

    self.playerCount = 0
    self.players = [
      ]
    # self.players = [Player()]
    cameraSize = ()
    self.cameras = []
    self.camOffsets = []

    self.minimap = Minimap(self.grid, (self.display.get_width() / 2, self.display.get_height() / 2))
    self.progressbar = Progressbar([320, 24], 320, 10)

  def createPlayers(self, players):
    self.players = players
    
    cameraSize = [
      self.width if self.playerCount == 1 else self.width / 2,
      self.height if self.playerCount <= 2 else self.height / 2
    ]
    self.cameras = [pygame.Surface(cameraSize) for _ in range(self.playerCount)]

    self.camOffsets = [[0, 0]] * self.playerCount

    print(self.cameras, self.camOffsets)
  def run(self):
    selected = 0
    playerControllerIds = []
    allControllerIds = []
    while True:
      self.display.fill((0, 0, 10))
      for event in pygame.event.get(eventtype=(pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED, pygame.QUIT, pygame.JOYBUTTONDOWN)):
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            self.joysticks[joy.get_instance_id()] = joy
            allControllerIds.append(joy.get_instance_id())
            break
        if event.type == pygame.JOYDEVICEREMOVED:
          del self.joysticks[event.instance_id]
          allControllerIds.remove(event.instance_id)
          break
        if event.type == pygame.JOYBUTTONDOWN:
          print(event)
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      match self.currentMenu:
        case 0:        
          for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
              match event.key:
                case pygame.K_z:
                  self.currentMenu = 1
                  self.playerCount = playerCount
                  playerControllerIds = [-1] * self.playerCount
                  selected = 0
                  break
                case pygame.K_RIGHT:
                  selected = (selected + 1) % 3
                  break
                case pygame.K_LEFT:
                  selected -= 1
                  if selected < 0:
                    selected = 2
                  break
          playerCount = selected + 2
          for i in range(3):
            if selected == i:
              self.display.blit(self.assets[f'{i+2}playersPressed'], (i * 72, 0))
            else:
              self.display.blit(self.assets[f'{i+2}players'], (i * 72, 0))
        case 1:
          pluggedInControllers = len(self.joysticks)
          for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
              match event.key:
                case pygame.K_z:
                  self.currentMenu = 2
                  players = []
                  for i in range(self.playerCount):

                    players.append(Player(team = i % 2 + 1, 
                                          controllerType = "keyboard" if playerControllerIds[i] < 0 else "controller", 
                                          controllerInfo=[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]))
                  self.createPlayers(players)
                  print(self.players)
                  break
                case pygame.K_RIGHT:
                  selected = (selected + 1) % self.playerCount
                  break
                case pygame.K_LEFT:
                  selected -= 1
                  if selected < 0:
                    selected = self.playerCount - 1
                case pygame.K_UP:
                  playerControllerIds[selected] = (playerControllerIds[selected] + 2) % (pluggedInControllers + 1) - 1
                  if playerControllerIds[selected] != -1:
                    print(self.joysticks)
                    print(playerControllerIds[selected])
                    self.joysticks[playerControllerIds[selected]].rumble(1, 1, 100)
                  break
                case pygame.K_DOWN:
                  playerControllerIds[selected] -= 1
                  if playerControllerIds[selected] < -1:
                    playerControllerIds[selected] = pluggedInControllers - 1

          for i, controller in enumerate(playerControllerIds):
            textureName = 'keyboard' if controller == -1 else 'controller'
            if selected == i:
              self.display.blit(self.assets[f'{textureName}Pressed'], (i * 72, 0))
            else:
              self.display.blit(self.assets[f'{textureName}'], (i * 72, 0))


        case 2:
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
          print(f'{round(team1Percent * 100, 2)}%-{round(team2Percent * 100, 2)}%') 

      self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
      pygame.display.update()
      # print(self.clock.get_fps())
      self.clock.tick(60)

Game().run()