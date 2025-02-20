import random
from game import Game
def create_empty_map(size):
    return [[1 for _ in range(size)] for _ in range(size)]

def carve_room(grid, x, y, width, height):
    for i in range(y, y + height):
        for j in range(x, x + width):
            grid[i][j] = 0

def carve_hallway(grid, x1, y1, x2, y2, hallway_cells, connect_prob=0.5):
    hallway_width = 3  # Adjust width of hallways

    if random.choice([True, True, False]):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for i in range(hallway_width):
                if y1 + i < len(grid):
                    if (x, y1 + i) not in hallway_cells or random.random() < connect_prob:
                        grid[y1 + i][x] = 0
                        hallway_cells.add((x, y1 + i))
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for i in range(hallway_width):
                if x2 + i < len(grid[0]):
                    if (x2 + i, y) not in hallway_cells or random.random() < connect_prob:
                        grid[y][x2 + i] = 0
                        hallway_cells.add((x2 + i, y))
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for i in range(hallway_width):
                if x1 + i < len(grid[0]):
                    if (x1 + i, y) not in hallway_cells or random.random() < connect_prob:
                        grid[y][x1 + i] = 0
                        hallway_cells.add((x1 + i, y))
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for i in range(hallway_width):
                if y2 + i < len(grid):
                    if (x, y2 + i) not in hallway_cells or random.random() < connect_prob:
                        grid[y2 + i][x] = 0
                        hallway_cells.add((x, y2 + i))

    return grid

def print_map(grid):
    for row in grid:
        print("".join("#" if cell == 1 else "." for cell in row))

def get_map_data(grid):
    return grid

if __name__ == "__main__":
    game_map = Game.generate_map(51)
    print_map(game_map)