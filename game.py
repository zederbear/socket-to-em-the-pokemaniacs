import pygame
import random
from map import generate_map, print_map, get_map_data

def render_map(grid, players, cell_size=10):
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
        
        for player in players:
            pygame.draw.rect(screen, red, (player.x * cell_size, player.y * cell_size, cell_size, cell_size))
        
        pygame.display.flip()
        
        for player in players:
            player.handle_movement(grid)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(10)
    
    pygame.quit()

def map_display(map_size):
    game_map = generate_map(map_size)
    players = []
    for _ in range(1):  # Change this to add multiple players
        player_start = (1, 1)
        while game_map[player_start[1]][player_start[0]] == 1:
            player_start = (random.randint(1, map_size - 2), random.randint(1, map_size - 2))
        players.append(Player(player_start[0], player_start[1]))
    
    render_map(game_map, players)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def move(self, x, y):
        self.x = x
        self.y = y
    
    def handle_movement(self, grid):
        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        if keys[pygame.K_w]:
            new_y -= 1
        if keys[pygame.K_s]:
            new_y += 1
        if keys[pygame.K_a]:
            new_x -= 1
        if keys[pygame.K_d]:
            new_x += 1
        
        if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid) and grid[new_y][new_x] == 0:
            self.move(new_x, new_y)

map_display(51)
