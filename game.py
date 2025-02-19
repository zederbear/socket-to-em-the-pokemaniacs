import pygame
import random
from map import generate_map, print_map, get_map_data

def render_map(grid, player, cell_size=10):
    pygame.init()
    size = len(grid) * cell_size
    screen = pygame.display.set_mode((size, size))
    pygame.display.set_caption("Map Renderer")
    
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        screen.fill(black)
        
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 1:
                    pygame.draw.rect(screen, white, (x * cell_size, y * cell_size, cell_size, cell_size))
        
        pygame.draw.rect(screen, red, (player.x * cell_size, player.y * cell_size, cell_size, cell_size))
        
        pygame.display.flip()
        
        keys = pygame.key.get_pressed()
        new_x, new_y = player.x, player.y
        if keys[pygame.K_w]:
            new_y -= 1
        if keys[pygame.K_s]:
            new_y += 1
        if keys[pygame.K_a]:
            new_x -= 1
        if keys[pygame.K_d]:
            new_x += 1
        
        if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid) and grid[new_y][new_x] == 0:
            player.move(new_x, new_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(10)
    
    pygame.quit()

def map_display(map_size):
    game_map = generate_map(map_size)
    player_start = (1, 1)
    while game_map[player_start[1]][player_start[0]] == 1:
        player_start = (random.randint(1, map_size - 2), random.randint(1, map_size - 2))
    
    player = Player(player_start[0], player_start[1])
    render_map(game_map, player)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def move(self, x, y):
        self.x = x
        self.y = y

map_display(51)
