from map import generate_map, print_map, get_map_data

players = [] # (x, y)

def map_display(map_size):
  game_map = generate_map(map_size)
  print_map(game_map)
  map_data = get_map_data(game_map)


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
    pass

map_display(51)