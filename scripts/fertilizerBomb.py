class Bomb:
  def __init__(self, position, sprite):
    self.blowUp = False
    self.msUntilBlowUp = 1000

    self.position = position
    self.sprite = sprite
    
  def update(self, passedMs):
    self.msUntilBlowUp -= passedMs

    if self.msUntilBlowUp <= 0:
      return True

  def render(self, surf, offset=[0, 0], tileSize=20):
    yOffset = 1 if self.msUntilBlowUp == 1000 else 1 - (2 ** (-10 * (self.msUntilBlowUp / 1000)))

    print(yOffset)

    surf.blit(self.sprite, (self.position[0] * tileSize - self.sprite.get_width() // 2 - offset[0], 
                            self.position[1] * tileSize - (yOffset * 2 * tileSize) - self.sprite.get_height() // 2 - offset[1]))

  def __str__(self):
    return f'{self.msUntilBlowUp} milliseconds until it blows up, {self.position} position'