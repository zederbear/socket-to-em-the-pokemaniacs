import pygame
import random
import json
from map import generate_map

class Game:
    def __init__(self, map_size=51):
        self.map_size = map_size
        self.game_map = generate_map(map_size)
        pygame.init()
        self.cell_size = 10
        screen_size = len(self.game_map) * self.cell_size
        self.screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption("Multiplayer tag")
        self.clock = pygame.time.Clock()
        self.local_player = Player(*self.get_spawn_position())
        self.remote_player = Player(*self.get_spawn_position())
    
    def get_spawn_position(self):
        x, y = 1, 1
        while True:
            x = random.randint(1, self.map_size - 2)
            y = random.randint(1, self.map_size - 2)
            if self.game_map[-y][-x] == 0:
                break
        return float(-x), float(-y)

    def display_map(self):
        dt = self.clock.tick(60) / 1000  # Delta time (seconds)
        
        self.local_player.handle_movement(self.game_map, dt)

        self.screen.fill((0, 0, 0))
        for y, row in enumerate(self.game_map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                      (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
        
        pygame.draw.rect(self.screen, (255, 0, 0),
                            (int(self.local_player.x * self.cell_size) - int(0.5 * self.cell_size),
                            int(self.local_player.y * self.cell_size) - int(0.5 * self.cell_size),
                            self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, (0, 0, 255),
                            (int(self.remote_player.x * self.cell_size) - int(0.5 * self.cell_size),
                            int(self.remote_player.y * self.cell_size) - int(0.5 * self.cell_size),
                            self.cell_size, self.cell_size))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def send_map(self, conn):
        data = json.dumps(self.game_map)
        conn.sendall(data.encode('utf-8'))

    def receive_map(self, conn):
        data = conn.recv(8192).decode('utf-8')
        self.game_map = json.loads(data)
    
    def send_player_data(self, conn):
        data = {'x': self.local_player.x, 'y': self.local_player.y}
        msg = json.dumps(data)
        conn.sendall(msg.encode('utf-8'))
    
    def receive_player_data(self, conn):
        data = conn.recv(1024).decode('utf-8')
        player_data = json.loads(data)
        self.remote_player.x = player_data['x']
        self.remote_player.y = player_data['y']

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
        
        if left < 0 or top < 0 or right >= len(grid[0]) or bottom >= len(grid):
            return False
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

# def map_display(map_size):
#     game_map = generate_map(map_size)
#     players = []
#     for _ in range(1):  # Change this to add multiple players
#         player_start = (1, 1)
#         while game_map[player_start[1]][player_start[0]] == 1:
#             player_start = (random.randint(1, map_size - 2), random.randint(1, map_size - 2))
#         players.append(Player(float(player_start[0]), float(player_start[1])))
    
#     Game.render_map(game_map, players, 10)

# map_display(51)
