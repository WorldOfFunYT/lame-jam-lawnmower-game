import pygame

ASSET_PATH = './assets/'
def loadImage(name, colorKey=(255, 255, 255)):
  image = pygame.image.load(ASSET_PATH + name + '.png').convert()
  image.set_colorkey(colorKey)
  return image