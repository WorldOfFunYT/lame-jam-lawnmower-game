import pygame
import sys
import os
import math

from scripts.utils import loadImage, distance
from scripts.progressBar import Progressbar
from scripts.player import Player
from scripts.minimap import Minimap
from scripts.fertilizerBomb import Bomb

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
      'keyboard': loadImage('buttons/keyboard'),
      'controller': loadImage('buttons/controller'),
      'keyboardPressed': loadImage('buttons/keyboardPressed'),
      'controllerPressed': loadImage('buttons/controllerPressed'),
      'blueLawnmowers': [pygame.transform.scale_by(pygame.transform.rotate(loadImage('lawnmowers/' + img.strip('.png'), (215, 123, 186)), 90), 2) for img in os.listdir('assets/lawnmowers') if 'blue' in img],
      'redLawnmowers': [pygame.transform.scale_by(pygame.transform.rotate(loadImage('lawnmowers/' + img.strip('.png'), (215, 123, 186)), 90), 2) for img in os.listdir('assets/lawnmowers') if 'red' in img],
      'neutralGrass': loadImage('tiles/grass'),
      'redGrass': loadImage('tiles/redGrass'),
      'blueGrass': loadImage('tiles/blueGrass'),
      'fertilizer': loadImage('fertilizer'),
      'menuGrass': loadImage('menuSprites/grassPlatform'),
      'menuBlueLawnmower': loadImage('menuSprites/blueLawnmower'),
      'menuRedLawnmower': loadImage('menuSprites/redLawnmower'),
      'playersTitle': loadImage('menuSprites/playersTitle', (0, 0, 0))
    }

    self.timer = 60 * 1000 # seconds * 1000

    self.fonts = {
      'timer': pygame.font.SysFont('roboto', 20),
      'bigWinText': pygame.font.SysFont('roboto', 80, bold=True),
      'smallWinText': pygame.font.SysFont('roboto', 60, bold=True),
      }
    
    self.sounds = {
      'motor': pygame.mixer.Sound('assets/audio/sfx/motor.ogg'),
      'bomb': pygame.mixer.Sound('assets/audio/sfx/explosion.ogg')
    }

    self.sounds['bomb'].set_volume(0.5)
    

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

    self.fertBombCooldown = 1000
    self.bombs = []

  def regrowGrass(self, coordinate=(0, 0), radius=5):
    minX = max(coordinate[0] - radius, 0)
    maxX = min(coordinate[0] + radius + 1, self.gridWidth - 1)
    minY = max(coordinate[1] - radius, 0)
    maxY = min(coordinate[1] + radius + 1, self.gridHeight - 1)

    for y in range(minY, maxY):
      for x in range(minX, maxX):
        if distance(coordinate, (x, y)) <= radius:
          self.grid[y][x] = 0

  def fertilizerBomb(self, playerCoordinates):
    gridPos = (int(playerCoordinates[0] // self.cellSize), int(playerCoordinates[1] // self.cellSize))
    self.bombs.append(Bomb(gridPos, self.assets['fertilizer']))
    self.fertBombCooldown = 5000

  def createPlayers(self, players):
    self.players = players
    
    cameraSize = [
      self.width if self.playerCount == 1 else self.width / 2,
      self.height if self.playerCount <= 2 else self.height / 2
    ]
    self.cameras = [pygame.Surface(cameraSize) for _ in range(self.playerCount)]

    self.camOffsets = [[0, 0]] * self.playerCount
  def run(self):

    selected = 0
    playerControllerIds = []
    allControllerIds = []
    lastFrame = pygame.Surface(self.display.get_size())
    lastFrame.fill((0, 0, 0))
    winScreen = pygame.Surface(self.display.get_size()).convert_alpha()
    for key, item in self.joysticks.items():
      allControllerIds.append(key)
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

          scaledBlueLawnmower = pygame.transform.scale_by(self.assets['menuBlueLawnmower'], 2)
          scaledRedLawnmower = pygame.transform.scale_by(self.assets['menuRedLawnmower'], 2)

          self.display.blit(pygame.transform.scale_by(self.assets['playersTitle'], 2), (self.display.get_width() // 2 - self.assets['playersTitle'].get_width(), int(self.display.get_height() * 0.3)))
          self.display.blit(pygame.transform.scale_by(self.assets['menuGrass'], 2), (self.display.get_width() // 2 - self.assets['menuGrass'].get_width(), int(self.display.get_height() * 0.7)))
          self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 2, int(self.display.get_height() * 0.7) - scaledBlueLawnmower.get_height()))
          self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width(), int(self.display.get_height() * 0.7) - scaledRedLawnmower.get_height()))
          
          for i in range(2):
            if selected > i:
              scaledBlueLawnmower.set_alpha(255)
              scaledRedLawnmower.set_alpha(255)
            else:
              scaledBlueLawnmower.set_alpha(63)
              scaledRedLawnmower.set_alpha(63)

            if i == 0:
              self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 4, int(self.display.get_height() * 0.7) - scaledBlueLawnmower.get_height()))
            else:
              self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width() * 3, int(self.display.get_height() * 0.7) - scaledRedLawnmower.get_height()))

        case 1:
          pluggedInControllers = len(self.joysticks)
          for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
              match event.key:
                case pygame.K_z:
                  self.currentMenu = 2
                  players = []
                  for i in range(self.playerCount):

                    players.append(Player(sprites=self.assets['blueLawnmowers' if i % 2 + 1 == 1 else 'redLawnmowers'], team = i % 2 + 1, 
                                          controllerType = "keyboard" if playerControllerIds[i] < 0 else "controller", 
                                          controllerInfo=[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]))
                    
                  self.createPlayers(players)
                  self.sounds['motor'].play(loops=-1)
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
                    self.joysticks[playerControllerIds[selected]].rumble(1, 1, 100)
                  break
                case pygame.K_DOWN:
                  playerControllerIds[selected] -= 1
                  if playerControllerIds[selected] < -1:
                    playerControllerIds[selected] = pluggedInControllers - 1
                  if playerControllerIds[selected] != -1:
                    self.joysticks[playerControllerIds[selected]].rumble(1, 1, 100)

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
              if keys[player.controlScheme[4]] and self.fertBombCooldown <= 0:
                self.fertilizerBomb(player.position)
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
                  if i == 3 and self.fertBombCooldown <= 0 and button == 1:
                    
                    self.fertilizerBomb(player.position)
          renderScrolls = [[0, 0]] * len(self.players)
          
          for i, player in enumerate(self.players):
            player.update(self.gridWidth * self.cellSize, self.gridHeight * self.cellSize) #Position rotation 

            

            team = player.team # Set team colour for grid mapping
            gridX, gridY = int(player.position[0]) // self.cellSize, int(player.position[1]) // self.cellSize
            if 0 <= gridX < self.gridWidth and 0 <= gridY < self.gridHeight and self.grid[gridY][gridX] == 0:
              if self.grid[gridY][gridX] == team:
                player.speed = 1.2
              else:
                player.speed = 1
              if self.grid[gridY][gridX] == 0:
                self.grid[gridY][gridX] = team # Set grid colour

            
            self.camOffsets[i][0] = player.getCenter()[0] - self.cameras[i].get_width() / 2 # 
            self.camOffsets[i][1] = player.getCenter()[1] - self.cameras[i].get_height() / 2
            renderScrolls[i] = (int(self.camOffsets[i][0]), int(self.camOffsets[i][1]))

          self.sounds['motor'].set_volume(abs(self.players[0].velocity) / 10)
          for bomb in self.bombs:
            if bomb.update(self.clock.get_time()):
              self.regrowGrass(bomb.position, 3)
              self.bombs.remove(bomb)
              self.sounds['bomb'].play()
              del bomb
              

          for i, camera in enumerate(self.cameras):
            
            camera.fill((0, 10, 0))
            for y in range(max(renderScrolls[i][1] // self.cellSize, 0), min((renderScrolls[i][1] + camera.get_height()) // self.cellSize + 1, len(self.grid))):
              for x in range(max(renderScrolls[i][0] // self.cellSize, 0), min((renderScrolls[i][0] + camera.get_width()) // self.cellSize + 1, len(self.grid[y]))):
                asset = "neutralGrass"
                if self.grid[y][x] == 1:
                  asset = "blueGrass"
                if self.grid[y][x] == 2:
                  asset = "redGrass"
                camera.blit(pygame.transform.scale(self.assets[asset], (self.cellSize, self.cellSize)), 
                            (x * self.cellSize - renderScrolls[i][0], 
                             y * self.cellSize - renderScrolls[i][1], self.cellSize, self.cellSize))

            for bomb in self.bombs:
              bomb.render(camera, offset=renderScrolls[i], tileSize=self.cellSize)

            for player in self.players:
              player.render(surf=self.cameras[i], offset=renderScrolls[i], spread=1)
            
            self.display.blit(camera, (self.display.get_width() // 2 if (i + 1) % 2 == 0 else 0, self.display.get_height() // 2 if (i + 1) > 2 else 0))

          playerGridCoordinates = [[player.team, (int(player.position[0]) // self.cellSize, int(player.position[1]) // self.cellSize)] for player in self.players]

          self.minimap.render(self.display, playerGridCoordinates)

          team1Percent = len([item for row in self.grid for item in row if item == 1]) / (self.gridWidth * self.gridHeight)
          team2Percent = len([item for row in self.grid for item in row if item == 2]) / (self.gridWidth * self.gridHeight)
          
          self.progressbar.render(self.display, team1Percent, team2Percent)
          self.display.blit(self.fonts['timer'].render(str(self.timer // 1000 + 1), False, (255, 255, 255)), (0, 0))
          self.timer -= self.clock.get_time()
          self.fertBombCooldown -= self.clock.get_time()
          lastFrame.fill((0, 0, 0))
          lastFrame.blit(self.display, (0, 0))
          if self.timer <= 0:
            self.currentMenu = 3
            self.sounds['motor'].stop()
        case 3: # End screen
          winScreen.fill((0, 0, 0, 128))

          if team1Percent > team2Percent:
            winScreen.fill((160, 10, 10), (int(winScreen.get_width() * 0.68), 0, winScreen.get_width(), winScreen.get_height()))
            winScreen.fill((10, 10, 150), (0, 0, int(winScreen.get_width() * 0.72), winScreen.get_height()))

            bigWinText = self.fonts['bigWinText'].render(f'{round(team1Percent * 100, 2)}%', False, (255, 255, 255))
            smallWinText = self.fonts['smallWinText'].render(f'{round(team2Percent * 100, 2)}%', False, (255, 255, 255))
            winScreen.blit(bigWinText, (int(winScreen.get_width() * 0.6) - bigWinText.get_width(), winScreen.get_height() // 2 - bigWinText.get_height() // 2))
            winScreen.blit(smallWinText, (int(winScreen.get_width() * 0.8), winScreen.get_height() // 2 - smallWinText.get_height() // 2))
          else:
            winScreen.fill((160, 10, 10), (int(winScreen.get_width() * 0.28), 0, winScreen.get_width(), winScreen.get_height()))
            winScreen.fill((10, 10, 150), (0, 0, int(winScreen.get_width() * 0.32), winScreen.get_height()))

            bigWinText = self.fonts['bigWinText'].render(f'{round(team2Percent * 100, 2)}%', False, (255, 255, 255))
            smallWinText = self.fonts['smallWinText'].render(f'{round(team1Percent * 100, 2)}%', False, (255, 255, 255))
            winScreen.blit(smallWinText, (int(winScreen.get_width() * 0.2) - smallWinText.get_width(), winScreen.get_height() // 2 - smallWinText.get_height() // 2))
            winScreen.blit(bigWinText, (int(winScreen.get_width() * 0.4), winScreen.get_height() // 2 - bigWinText.get_height() // 2))


          self.display.blit(lastFrame, (0, 0))
          self.display.blit(winScreen, (0, 0))

      
      self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
      pygame.display.update()
      # print(self.clock.get_fps())
      self.clock.tick(60)

Game().run()