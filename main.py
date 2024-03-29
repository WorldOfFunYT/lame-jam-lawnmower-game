import pygame
import sys
import os
import math

from scripts.utils import loadImage, distance, lerp, easeOutExpo
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
    pygame.display
    self.display = pygame.Surface((self.width, self.height))

    self.clock = pygame.time.Clock()

    self.cellSize = 20
    self.gridWidth, self.gridHeight = 32, 32
    self.grid = [[0] * self.gridWidth for _ in range(self.gridHeight)]

    self.assets = {
      'keyboard': loadImage('menuSprites/keyboard', (0, 0, 0)),
      'controller': loadImage('menuSprites/controller', (0, 0, 0)),
      'keyboardPressed': loadImage('buttons/keyboardPressed'),
      'controllerPressed': loadImage('buttons/controllerPressed'),
      'blueLawnmowers': [pygame.transform.scale_by(pygame.transform.rotate(loadImage('lawnmowers/' + img.strip('.png'), (215, 123, 186)), 90), 2) for img in os.listdir('assets/lawnmowers') if 'blue' in img],
      'redLawnmowers': [pygame.transform.scale_by(pygame.transform.rotate(loadImage('lawnmowers/' + img.strip('.png'), (215, 123, 186)), 90), 2) for img in os.listdir('assets/lawnmowers') if 'red' in img],
      'neutralGrass': pygame.transform.scale(loadImage('tiles/grass'), (self.cellSize, self.cellSize)),
      'redGrass': pygame.transform.scale(loadImage('tiles/redGrass'), (self.cellSize, self.cellSize)),
      'blueGrass': pygame.transform.scale(loadImage('tiles/blueGrass'), (self.cellSize, self.cellSize)),
      'fertilizer': loadImage('fertilizer'),
      'menuGrass': loadImage('menuSprites/grassPlatform'),
      'menuBlueLawnmower': loadImage('menuSprites/blueLawnmower'),
      'menuRedLawnmower': loadImage('menuSprites/redLawnmower'),
      'playersTitle': loadImage('menuSprites/playersTitle', (0, 0, 0)),
      'tooltipNext': loadImage('menuSprites/next', (0, 0, 0))
    }

    pygame.display.set_icon(self.assets['menuRedLawnmower'])
    pygame.display.set_caption('Lawnmowing Lunacy')


    self.timer = 3 * 60 * 1000 # seconds * 1000

    self.fonts = {
      'timer': pygame.font.SysFont('roboto', 20),
      'bigWinText': pygame.font.SysFont('roboto', 100, bold=True),
      'smallWinText': pygame.font.SysFont('roboto', 50, bold=True),
      }
    
    self.sounds = {
      'motor': pygame.mixer.Sound('assets/audio/sfx/motor.ogg'),
      'bomb': pygame.mixer.Sound('assets/audio/sfx/explosion.ogg')
    }

    self.sounds['bomb'].set_volume(0.5)

    self.channels = []
    

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

  def fertilizerBomb(self, player):
    playerCoordinates = player.position
    gridPos = (int(playerCoordinates[0] // self.cellSize), int(playerCoordinates[1] // self.cellSize))
    self.bombs.append(Bomb(gridPos, self.assets['fertilizer']))
    player.fertBombCooldown = 5000

  def createPlayers(self, players):
    self.players = players
    
    cameraSize = [
      self.width if self.playerCount == 1 else self.width / 2,
      self.height if self.playerCount <= 2 else self.height / 2
    ]
    self.cameras = [pygame.Surface(cameraSize) for _ in range(self.playerCount)]

    self.camOffsets = [[0, 0]] * self.playerCount

    self.channels = [pygame.mixer.Channel(i) for i in range(self.playerCount)]
  def run(self):

    moved = False

    animFrames = 0

    selected = 0
    playerControllerIds = []
    allControllerIds = []
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
            if event.type == pygame.JOYAXISMOTION and event.axis == 0:
              if event.value >= 0.5:
                if not moved:
                  selected = (selected + 1) % 3
                  moved = True
              elif event.value <= -0.5:
                if not moved:
                  selected -= 1
                  if selected < 0:
                    selected = 2
                  moved = True
              else:
                moved = False

            if event.type == pygame.JOYHATMOTION:
              if event.value[0] == -1:
                selected -= 1
                if selected < 0:
                  selected = 2
              elif event.value[0] == 1:
                selected = (selected + 1) % 3
            if event.type == pygame.JOYBUTTONUP:
              if event.button == 0:
                animFrames = 0
                self.currentMenu = 1
                self.playerCount = playerCount
                playerControllerIds = [-1] * self.playerCount
                selected = 0
            if event.type == pygame.KEYDOWN:
              match event.key:
                case pygame.K_z:
                  animFrames = 0
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

          offset = (easeOutExpo(animFrames / 1000) * -1 + 1) * 20
          print(offset)

          scaledBlueLawnmower = pygame.transform.scale_by(self.assets['menuBlueLawnmower'], 2)
          scaledRedLawnmower = pygame.transform.scale_by(self.assets['menuRedLawnmower'], 2)

          self.display.blit(pygame.transform.scale_by(self.assets['playersTitle'], 2), (self.display.get_width() // 2 - self.assets['playersTitle'].get_width(), int(self.display.get_height() * 0.3)))
          self.display.blit(pygame.transform.scale_by(self.assets['menuGrass'], 2), (self.display.get_width() // 2 - self.assets['menuGrass'].get_width(), int(self.display.get_height() * 0.7)))
          self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 2, int(self.display.get_height() * 0.7) - scaledBlueLawnmower.get_height() - offset))
          self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width(), int(self.display.get_height() * 0.7) - scaledRedLawnmower.get_height() - offset))
          
          for i in range(2):
            if selected > i:
              scaledBlueLawnmower.set_alpha(255)
              scaledRedLawnmower.set_alpha(255)
            else:
              scaledBlueLawnmower.set_alpha(63)
              scaledRedLawnmower.set_alpha(63)

            if i == 0:
              self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 4, int(self.display.get_height() * 0.7) - scaledBlueLawnmower.get_height() - offset))
            else:
              self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width() * 3, int(self.display.get_height() * 0.7) - scaledRedLawnmower.get_height() - offset))

        case 1:
          pluggedInControllers = len(self.joysticks)
          for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
              if event.axis == 0:
                if event.value <= -0.5:
                  if not moved:
                    selected -=  1
                    if selected < 0:
                      selected = self.playerCount - 1
                    moved = True
                elif event.value >= 0.5:
                  if not moved:
                    selected = (selected + 1) % self.playerCount
                    moved = True
                else:
                  moved = False
              elif event.axis == 1:
                if event.value <= -0.5:
                  if not moved:
                    playerControllerIds[selected] = (playerControllerIds[selected] + 2) % (pluggedInControllers + 1) - 1
                    if playerControllerIds[selected] != -1:
                      self.joysticks[playerControllerIds[selected]].rumble(1, 1, 100)
                    moved = True
                elif event.value >= 0.5:
                  if not moved:
                    playerControllerIds[selected] -= 1
                    if playerControllerIds[selected] < -1:
                      playerControllerIds[selected] = pluggedInControllers - 1
                      if playerControllerIds[selected] != -1:
                        self.joysticks[playerControllerIds[selected]].rumble(1, 1, 100)
                    moved = True
                else:
                  moved = False
            if event.type == pygame.JOYBUTTONUP:
              if event.button == 0:
                self.currentMenu = 2
                players = []
                if self.playerCount <=2:
                  for i in range(self.playerCount):
                    players.append(Player(sprites=self.assets['blueLawnmowers' if i % 2 + 1 == 1 else 'redLawnmowers'], team = i % 2 + 1, 
                                          controllerType = "keyboard" if playerControllerIds[i] < 0 else "controller", 
                                          controllerInfo=[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]))
                else:
                  for i in range(self.playerCount):
                    if i == 0:
                      newTeam = 1
                      newSprites = self.assets['blueLawnmowers']
                      newControllerType = 'keyboard' if playerControllerIds[1] < 0 else "controller"
                      newPos = [100, 100]
                      newRotation = 225
                      newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[1] < 0 else [ allControllerIds[playerControllerIds[1]] ]
                    elif i == 1:
                      newTeam = 1
                      newSprites = self.assets['blueLawnmowers']
                      newControllerType = 'keyboard' if playerControllerIds[0] < 0 else "controller"
                      newPos = [100, self.cellSize * self.gridHeight - 100]
                      newRotation = 145
                      newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[0] < 0 else [ allControllerIds[playerControllerIds[0]] ]
                    elif i == 2:
                      newTeam = 2
                      newSprites = self.assets['redLawnmowers']
                      newControllerType = 'keyboard' if playerControllerIds[i] < 0 else "controller"
                      newPos = [self.cellSize * self.gridWidth - 100, 100]
                      newRotation = 315
                      newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]
                    elif i == 3:
                      newTeam = 2
                      newSprites = self.assets['redLawnmowers']
                      newControllerType = 'keyboard' if playerControllerIds[i] < 0 else "controller"
                      newPos = [self.cellSize * self.gridWidth - 100, self.cellSize * self.gridHeight - 100]
                      newRotation = 45
                      newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]
                    
                    players.append(Player(newSprites, team=newTeam, controllerType=newControllerType, controllerInfo=newControllerInfo, spawnCoords=newPos, rotation=newRotation))
                self.createPlayers(players)
                for channel in self.channels:
                  channel.play(self.sounds['motor'], loops=-1)

            if event.type == pygame.KEYDOWN:
              match event.key:
                case pygame.K_z:
                  self.currentMenu = 2
                  players = []
                  if self.playerCount <=2:
                    for i in range(self.playerCount):
                      players.append(Player(sprites=self.assets['blueLawnmowers' if i % 2 + 1 == 1 else 'redLawnmowers'], team = i % 2 + 1, 
                                            controllerType = "keyboard" if playerControllerIds[i] < 0 else "controller", 
                                            controllerInfo=[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]))
                  else:
                    for i in range(self.playerCount):
                      if i == 0:
                        newTeam = 1
                        newSprites = self.assets['blueLawnmowers']
                        newControllerType = 'keyboard' if playerControllerIds[1] < 0 else "controller"
                        newPos = [100, 100]
                        newRotation = 225
                        newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[1] < 0 else [ allControllerIds[playerControllerIds[1]] ]
                      elif i == 1:
                        newTeam = 1
                        newSprites = self.assets['blueLawnmowers']
                        newControllerType = 'keyboard' if playerControllerIds[0] < 0 else "controller"
                        newPos = [100, self.cellSize * self.gridHeight - 100]
                        newRotation = 145
                        newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[0] < 0 else [ allControllerIds[playerControllerIds[0]] ]
                      elif i == 2:
                        newTeam = 2
                        newSprites = self.assets['redLawnmowers']
                        newControllerType = 'keyboard' if playerControllerIds[i] < 0 else "controller"
                        newPos = [self.cellSize * self.gridWidth - 100, 100]
                        newRotation = 315
                        newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]
                      elif i == 3:
                        newTeam = 2
                        newSprites = self.assets['redLawnmowers']
                        newControllerType = 'keyboard' if playerControllerIds[i] < 0 else "controller"
                        newPos = [self.cellSize * self.gridWidth - 100, self.cellSize * self.gridHeight - 100]
                        newRotation = 45
                        newControllerInfo = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z] if playerControllerIds[i] < 0 else [ allControllerIds[playerControllerIds[i]] ]
                      
                      players.append(Player(newSprites, team=newTeam, controllerType=newControllerType, controllerInfo=newControllerInfo, spawnCoords=newPos, rotation=newRotation))
                  self.createPlayers(players)
                  for channel in self.channels:
                    channel.play(self.sounds['motor'], loops=-1)
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
                  print(playerControllerIds)

          oldY = int(self.display.get_height() * 0.7) - scaledBlueLawnmower.get_height()
          newY = self.display.get_height() // 2 - scaledBlueLawnmower.get_height() // 2
          offset = lerp(oldY, newY, easeOutExpo(animFrames / 1000))

          scaledBlueLawnmower.set_alpha(255)
          scaledRedLawnmower.set_alpha(255)

          textures = [pygame.transform.scale_by(self.assets['keyboard' if playerControllerIds[0] == -1 else 'controller'], 2),
                      pygame.transform.scale_by(self.assets['keyboard' if playerControllerIds[1] == -1 else 'controller'], 2)]


          if self.playerCount > 2:
            self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 2, offset))
            texture = pygame.transform.scale_by(self.assets['keyboard' if playerControllerIds[2] == -1 else 'controller'], 2)
            self.display.blit(textures[1], (self.display.get_width() // 2 - textures[1].get_width() * 1.5, offset + int(self.display.get_height() * 0.2)))

            self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 4, offset))
            self.display.blit(textures[0], (self.display.get_width() // 2 - textures[0].get_width()  * 3.5, offset + int(self.display.get_height() * 0.2)))

            self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width(), offset))
            self.display.blit(texture, (self.display.get_width() // 2 + texture.get_width() // 2, offset + int(self.display.get_height() * 0.2)))
          else:
            self.display.blit(scaledBlueLawnmower, (self.display.get_width() // 2 - scaledBlueLawnmower.get_width() * 2, offset))
            self.display.blit(textures[0], (self.display.get_width() // 2 - textures[0].get_width()  * 1.5, offset + int(self.display.get_height() * 0.2)))

            self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width(), offset))
            self.display.blit(textures[1], (self.display.get_width() // 2 + textures[1].get_width() // 2, offset + int(self.display.get_height() * 0.2)))

          if self.playerCount > 3:
            self.display.blit(scaledRedLawnmower, (self.display.get_width() // 2 + scaledRedLawnmower.get_width() * 3, offset))
            texture = pygame.transform.scale_by(self.assets['keyboard' if playerControllerIds[3] == -1 else 'controller'], 2)
            self.display.blit(texture, (self.display.get_width() // 2 + texture.get_width() * 2.5, offset + int(self.display.get_height() * 0.2)))
        case 2:
          renderScrolls = [[0, 0]] * len(self.players)
          for i, player in enumerate(self.players):
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
              if keys[player.controlScheme[4]] and player.fertBombCooldown <= 0:
                self.fertilizerBomb(player)
              player.movement += movement
              player.rotationDirection += rotationV
            else:
              for joystick in self.joysticks.values():
                jid = joystick.get_instance_id()
                if player.controllerId == jid:
                  axis = joystick.get_axis(0)

                  if abs(axis) <= 0.1:
                    axis = 0
                  player.rotationDirection = axis
                  
                  hat = joystick.get_hat(0)[0]
                  if hat != 0:
                    player.rotationDirection = hat
                  
                  player.movement += joystick.get_button(0)
                  player.movement -= joystick.get_button(1)
                  if joystick.get_button(3) == 1 and player.fertBombCooldown <= 0:
                    self.fertilizerBomb(player)
          
            player.update(self.gridWidth * self.cellSize, self.gridHeight * self.cellSize, self.clock.get_time()) #Position rotation 

            gridX, gridY = int(player.position[0]) // self.cellSize, int(player.position[1]) // self.cellSize
            if 0 <= gridX < self.gridWidth and 0 <= gridY < self.gridHeight and self.grid[gridY][gridX] == 0:
              if self.grid[gridY][gridX] == player.team:
                player.speed = 1.2
              else:
                player.speed = 1
              if self.grid[gridY][gridX] == 0:
                self.grid[gridY][gridX] = player.team # Set grid colour

            
            self.camOffsets[i][0] = player.getCenter()[0] - self.cameras[i].get_width() / 2 
            self.camOffsets[i][1] = player.getCenter()[1] - self.cameras[i].get_height() / 2
            renderScrolls[i] = (int(self.camOffsets[i][0]), int(self.camOffsets[i][1]))

            self.channels[i].set_volume(abs(self.players[i].velocity) / 15)
          # self.sounds['motor'].set_volume(abs(self.players[0].velocity) / 10)
          for bomb in self.bombs:
            if bomb.update(self.clock.get_time()):
              self.regrowGrass(bomb.position, 3)
              self.bombs.remove(bomb)
              self.sounds['bomb'].play()
              del bomb
              

          for i, camera in enumerate(self.cameras):
            
            camera.fill((0, 10, 0))
            for y in range(max(renderScrolls[i][1] // self.cellSize, 0), min((renderScrolls[i][1] + camera.get_height()) // self.cellSize + 1, self.gridHeight)):
              for x in range(max(renderScrolls[i][0] // self.cellSize, 0), min((renderScrolls[i][0] + camera.get_width()) // self.cellSize + 1, self.gridWidth)):
                asset = "neutralGrass"
                if self.grid[y][x] == 1:
                  asset = "blueGrass"
                if self.grid[y][x] == 2:
                  asset = "redGrass"
                camera.blit(self.assets[asset], 
                            (x * self.cellSize - renderScrolls[i][0], 
                             y * self.cellSize - renderScrolls[i][1]))

            for bomb in self.bombs:
              bomb.render(camera, offset=renderScrolls[i], tileSize=self.cellSize)

            for player in self.players:
              player.render(surf=camera, offset=renderScrolls[i], spread=1)
            
            
            self.display.blit(camera, (self.display.get_width() // 2 if (i + 1) % 2 == 0 else 0, self.display.get_height() // 2 if (i + 1) > 2 else 0))
            pass

          playerGridCoordinates = [[player.team, (int(player.position[0]) // self.cellSize, int(player.position[1]) // self.cellSize)] for player in self.players]

          self.minimap.render(self.display, playerGridCoordinates)

          team1Percent = len([item for row in self.grid for item in row if item == 1]) / (self.gridWidth * self.gridHeight)
          team2Percent = len([item for row in self.grid for item in row if item == 2]) / (self.gridWidth * self.gridHeight)
          
          self.progressbar.render(self.display, team1Percent, team2Percent)
          self.display.blit(self.fonts['timer'].render(str(self.timer // 1000 + 1), False, (255, 255, 255)), (0, 0))
          self.timer -= self.clock.get_time()
          if self.timer <= 0:
            self.currentMenu = 3
            self.sounds['motor'].stop()
        case 3: # End screen
          winScreen.fill((0, 0, 0, 255))

          pygame.draw.polygon(winScreen, (10, 10, 150), ((0, 0), (winScreen.get_height(), 0), (0, winScreen.get_height())))
          pygame.draw.polygon(winScreen, (160, 10, 10), ((winScreen.get_width(), winScreen.get_height()), 
                                                         (winScreen.get_width() - winScreen.get_height(), winScreen.get_height()), 
                                                         (winScreen.get_width(), 0)))

          blueText, redText = (157, 198, 255), (255, 166, 166)
          if team1Percent > team2Percent:
            bigWinText = pygame.transform.rotate(self.fonts['bigWinText'].render(f'{round(team1Percent * 100, 2)}%', False, blueText), 45)
            smallWinText = pygame.transform.rotate(self.fonts['smallWinText'].render(f'{round(team2Percent * 100, 2)}%', False, redText), 45)
            winScreen.blit(bigWinText, (winScreen.get_width() // 2 - bigWinText.get_width() // 2 - 15, winScreen.get_height() // 2 - bigWinText.get_height() // 2 - 10))
            winScreen.blit(smallWinText, (winScreen.get_width() // 2 - smallWinText.get_width() // 2 + 25, winScreen.get_height() // 2 - smallWinText.get_height() // 2 + 20))
          else:
            bigWinText = pygame.transform.rotate(self.fonts['bigWinText'].render(f'{round(team2Percent * 100, 2)}%', False, redText), 45)
            smallWinText = pygame.transform.rotate(self.fonts['smallWinText'].render(f'{round(team1Percent * 100, 2)}%', False, blueText), 45)
            winScreen.blit(smallWinText, (winScreen.get_width() // 2 - smallWinText.get_width() // 2 - 25, winScreen.get_height() // 2 - smallWinText.get_height() // 2 - 20))
            winScreen.blit(bigWinText, (winScreen.get_width() // 2 - bigWinText.get_width() // 2 + 20, winScreen.get_height() // 2 - bigWinText.get_height() // 2 + 15))
          self.display.blit(winScreen, (0, 0))

      
      self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
      pygame.display.update()
      print(self.clock.get_fps())
      animFrames += self.clock.get_time()
      self.clock.tick(60)

Game().run()