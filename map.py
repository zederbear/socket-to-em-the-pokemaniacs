import random
import pygame

def create_empty_map(size):
    return [[1 for _ in range(size)] for _ in range(size)]

def carve_room(grid, x, y, width, height):
    for i in range(y, y + height):
        for j in range(x, x + width):
            grid[i][j] = 0
    for i in range(-2, 3):
        for j in range(-2, 3):
            grid[25 + i][25 + j] = 0

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


def generate_map(size):
    grid = create_empty_map(size)
    rooms = []
    min_distance = 5  # Minimum distance between room centers
    hallway_cells = set()  # To store hallway cell coordinates
    connect_prob = 0.75 # Probability of connecting to existing hallway

    max_rooms = random.randint(10, 20)
    for _ in range(max_rooms):
        w, h = random.randint(5, 10), random.randint(5, 10)
        x, y = random.randint(1, size - w - 1), random.randint(1, size - h - 1)

        # Check if the new room is too close to existing rooms
        valid_position = True
        for rx, ry in rooms:
            distance = ((x + w // 2 - rx) ** 2 + (y + h // 2 - ry) ** 2) ** 0.5
            if distance < min_distance:
                valid_position = False
                break

        if valid_position:
            carve_room(grid, x, y, w, h)
            rooms.append((x + w // 2, y + h // 2))

    for i in range(len(rooms) - 1):
        carve_hallway(grid, *rooms[i], *rooms[i + 1], hallway_cells, connect_prob)

    x1, y1 = 25, 25
    x2, y2 = 1, 25
    hallway_width = 3
    for x in range(x2, x1 + 25):
        for i in range(hallway_width):
            y = y1 - hallway_width // 2 + i
            if 0 <= y < len(grid):
                grid[y][x] = 0

    return grid

def print_map(grid):
    grid[25][25] = 6
    for row in grid:
        print("".join("#" if cell == 1 else "/" if cell == 5 else "|" if cell == 6 else "-" if cell == 7 else "." for cell in row))

def get_map_data(grid):
    return grid

if __name__ == "__main__":
    game_map = generate_map(51)
    print_map(game_map)