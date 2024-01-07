import pygame
import math

ASSET_PATH = './assets/'
def loadImage(name, colorKey=(255, 255, 255)):
  image = pygame.image.load(ASSET_PATH + name + '.png').convert()
  image.set_colorkey(colorKey)
  return image

def distance(coord1, coord2):
  dx = coord2[0] - coord1[0]
  dy = coord2[1] - coord1[1]

  return abs(math.sqrt(dx ** 2 + dy ** 2))