import random
import time
import pygame

def create_empty_map(size):
    return [[1 for _ in range(size)] for _ in range(size)]

def carve_room(grid, x, y, width, height):
    for i in range(y, y + height):
        for j in range(x, x + width):
            grid[i][j] = 0

def carve_hallway(grid, x1, y1, x2, y2):
    hallway_width = 3  # Adjust width of hallways
    
    if random.choice([True, True, False]):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for i in range(hallway_width):
                if y1 + i < len(grid):
                    grid[y1 + i][x] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for i in range(hallway_width):
                if x2 + i < len(grid[0]):
                    grid[y][x2 + i] = 0
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for i in range(hallway_width):
                if x1 + i < len(grid[0]):
                    grid[y][x1 + i] = 0
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for i in range(hallway_width):
                if y2 + i < len(grid):
                    grid[y2 + i][x] = 0


def generate_map(size):
    grid = create_empty_map(size)
    rooms = []
    for _ in range(room_count):
        w, h = random.randint(min_size, max_size), random.randint(min_size, max_size)
        x1, y1 = random.randint(1, size - w - 1), random.randint(1, size - h - 1)
        x2, y2 = x1 + w, y1 + h
        rooms.append((x1, y1, x2, y2))
    return rooms

def create_hallways(rooms):
    hallways = []
    for i in range(len(rooms) - 1):
        x1, y1 = (rooms[i][0] + rooms[i][2]) // 2, (rooms[i][1] + rooms[i][3]) // 2
        x2, y2 = (rooms[i + 1][0] + rooms[i + 1][2]) // 2, (rooms[i + 1][1] + rooms[i + 1][3]) // 2
        
        if random.choice([True, False]):
            hallways.append((x1, y1, x2, y1))  # Horizontal segment
            hallways.append((x2, y1, x2, y2))  # Vertical segment
        else:
            hallways.append((x1, y1, x1, y2))  # Vertical segment
            hallways.append((x1, y2, x2, y2))  # Horizontal segment
    return hallways

# def generate_map(size):
#     grid = create_empty_map(size)
#     rooms = []
    
#     for _ in range(random.randint(10, 16)):
#         w, h = random.randint(5, 10), random.randint(5, 10)
#         x, y = random.randint(1, size - w - 1), random.randint(1, size - h - 1)
#         carve_room(grid, x, y, w, h)
#         rooms.append((x + w // 2, y + h // 2))
    
#     for i in range(len(rooms) - 1):
#         carve_hallway(grid, *rooms[i], *rooms[i + 1])
    
#     return grid 

def generate_map(size):
    room_count = random.randint(10, 16)
    rooms = create_rooms(size, room_count, 5, 10)
    hallways = create_hallways(rooms)
    return rooms, hallways

def print_map(grid):
    for row in grid:
        print("".join("#" if cell == 1 else "." for cell in row))

def get_map_data(grid):
    return grid

# if __name__ == "__main__":
#     game_map = generate_map(51)
#     print_map(game_map)
