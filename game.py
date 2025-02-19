players = [] # (x, y)

def map_display():
  pass

class map():
  def __init__(self):
    self.map = [[0 for i in range(10)] for j in range(10)]

class player():
  def __init__(self, x, y, type):
    self.x = x
    self.y = y
    self.type = type
    self.id = players.length

  def move(self, x, y):
    self.x = x
    self.y = y

  def tag(self):
   
