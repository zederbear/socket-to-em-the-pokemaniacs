import pygame
import random
from map import generate_map
class Game:
    def __init__(self, map_size):
        self.map_size = map_size
        self.game_map = generate_map(map_size)

    def render_map(grid, players, cell_size=10):
        pygame.init()
        size = len(grid) * cell_size
        screen = pygame.display.set_mode((size, size))
        pygame.display.set_caption("Smooth Map Renderer")
        
        black = (0, 0, 0)
        white = (255, 255, 255)
        red = (255, 0, 0)
        
        clock = pygame.time.Clock()
        
        running = True
        while running:
            dt = clock.tick(60) / 1000  # Delta time (seconds)
            
            screen.fill(black)
            
            for y, row in enumerate(grid):
                for x, cell in enumerate(row):
                    if cell == 1:
                        pygame.draw.rect(screen, white, (x * cell_size, y * cell_size, cell_size, cell_size))
            
            for player in players:
                player.handle_movement(grid, dt)
                pygame.draw.rect(screen, red, (int(player.x * cell_size) - (0.5 * cell_size), int(player.y * cell_size) - (0.5 * cell_size), cell_size, cell_size))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        pygame.quit()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 15  # Movement speed in cells per second
        self.size = 0.4  # Collision box size factor
    
    def can_move(self, grid, new_x, new_y):
        """Check if the player can move to the new position without colliding."""
        left = int(new_x - self.size)
        right = int(new_x + self.size)
        top = int(new_y - self.size)
        bottom = int(new_y + self.size)
        
        if grid[top][left] == 1 or grid[top][right] == 1 or grid[bottom][left] == 1 or grid[bottom][right] == 1:
            return False
        return True
    
    def handle_movement(self, grid, dt):
        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        
        if keys[pygame.K_w]:
            if keys[pygame.K_a]:
                new_x -= self.speed * dt * 0.7071
                new_y -= self.speed * dt * 0.7071
            elif keys[pygame.K_d]:
                new_x += self.speed * dt * 0.7071
                new_y -= self.speed * dt * 0.7071
            else:
                new_y -= self.speed * dt
        if keys[pygame.K_s]:
            if keys[pygame.K_a]:
                new_x -= self.speed * dt * 0.7071
                new_y += self.speed * dt * 0.7071
            elif keys[pygame.K_d]:
                new_x += self.speed * dt * 0.7071
                new_y += self.speed * dt * 0.7071
            else:
                new_y += self.speed * dt
        if keys[pygame.K_a]:
            if not keys[pygame.K_w] and not keys[pygame.K_s]:
                new_x -= self.speed * dt
        if keys[pygame.K_d]:
            if not keys[pygame.K_w] and not keys[pygame.K_s]:
                new_x += self.speed * dt
        
        
        # Apply movement only if there's no collision
        if self.can_move(grid, new_x, self.y):
            self.x = new_x
        if self.can_move(grid, self.x, new_y):
            self.y = new_y

def map_display(map_size):
    game_map = generate_map(map_size)
    players = []
    for _ in range(1):  # Change this to add multiple players
        player_start = (1, 1)
        while game_map[player_start[1]][player_start[0]] == 1:
            player_start = (random.randint(1, map_size - 2), random.randint(1, map_size - 2))
        players.append(Player(float(player_start[0]), float(player_start[1])))
    
    Game.render_map(game_map, players, 10)

map_display(51)
