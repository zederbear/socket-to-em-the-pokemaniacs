import random
import time

def create_empty_map(size):
    return [[1 for _ in range(size)] for _ in range(size)]

def carve_room(grid, x, y, width, height):
    for i in range(y, y + height):
        for j in range(x, x + width):
            grid[i][j] = 0

def carve_hallway(grid, x1, y1, x2, y2):
    if random.choice([True, True, False]):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y1][x] = 0
            if y1 + 1 < len(grid):
                grid[y1 + 1][x] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x2] = 0
            if x2 + 1 < len(grid[0]):
                grid[y][x2 + 1] = 0
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x1] = 0
            if x1 + 1 < len(grid[0]):
                grid[y][x1 + 1] = 0
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y2][x] = 0
            if y2 + 1 < len(grid):
                grid[y2 + 1][x] = 0

def generate_map(size):
    grid = create_empty_map(size)
    rooms = []
    
    for _ in range(random.randint(10, 16)):
        w, h = random.randint(5, 10), random.randint(5, 10)
        x, y = random.randint(1, size - w - 1), random.randint(1, size - h - 1)
        carve_room(grid, x, y, w, h)
        rooms.append((x + w // 2, y + h // 2))
    
    for i in range(len(rooms) - 1):
        carve_hallway(grid, *rooms[i], *rooms[i + 1])
    
    return grid

def print_map(grid):
    for row in grid:
        print("".join("#" if cell == 1 else "." for cell in row))

def get_map_data(grid):
    return grid

if __name__ == "__main__":
    game_map = generate_map(51)
    print_map(game_map)
    map_data = get_map_data(game_map)
