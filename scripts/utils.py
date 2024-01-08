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

def lerp(num1, num2, poi=0.5):
  distance = num2 - num1
  return num1 + distance * poi

def easeOutExpo(time=0):
  return 1 if time >= 1 else 1 - 2**(time * -10)