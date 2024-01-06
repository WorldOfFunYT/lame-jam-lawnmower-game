import pygame

ASSET_PATH = './assets/'
def loadImage(name):
  image = pygame.image.load(ASSET_PATH + name + '.png').convert()
  image.set_colorkey((255, 255, 255))
  return image