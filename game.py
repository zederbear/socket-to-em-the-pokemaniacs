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
        self.remote_players = {}
    
    def get_spawn_position(self):
        x, y = 1, 1
        while self.game_map[y][x] == 1:
            x = random.randint(1, self.map_size - 2)
            y = random.randint(1, self.map_size - 2)
        return float(x), float(y)

    def display_map(self):
        dt = self.clock.tick(60) / 1000  # Delta time (seconds)
        
        self.local_player.handle_movement(self.game_map, dt)

        self.screen.fill((0, 0, 0))
        for y, row in enumerate(self.game_map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pygame.draw.rect(
                        self.screen,
                        (255, 255, 255),
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    )
        
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            (
                int(self.local_player.x * self.cell_size) - int(0.5 * self.cell_size),
                int(self.local_player.y * self.cell_size) - int(0.5 * self.cell_size),
                self.cell_size, self.cell_size
            )
        )
        for player in self.remote_players.values():
            pygame.draw.rect(
                self.screen,
                (0, 0, 255),
                (
                    int(player.x * self.cell_size) - int(0.5 * self.cell_size),
                    int(player.y * self.cell_size) - int(0.5 * self.cell_size),
                    self.cell_size, self.cell_size
                )
            )
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def send_map(self, conn):
        data = json.dumps(self.game_map)
        conn.sendall(data.encode('utf-8'))

    def receive_map(self, conn):
        buffer = ""
        while "\n" not in buffer:
            buffer += conn.recv(1024).decode('utf-8')
        line, _ = buffer.split("\n", 1)
        msg = json.loads(line)
        if msg.get("type") == "map":
            self.game_map = msg["data"]
        else:
            self.game_map = msg
    
    def send_player_data(self, conn):
        data = {
            'type': 'pos',
            'data': {
                'x': self.local_player.x, 
                'y': self.local_player.y
            }
        }
        msg = json.dumps(data) + '\n'
        conn.sendall(msg.encode('utf-8'))
    
    def receive_state(self, conn):
        buffer = ""
        try:
            while "\n" not in buffer:
                part = conn.recv(1024).decode('utf-8')
                if not part:
                    return  # Connection closed
                buffer += part
            line, _ = buffer.split("\n", 1)
            state_data = json.loads(line)
        except Exception as e:
            print("Error receiving state:", e)
            return

        clients_data = state_data.get('data', {}).get('clients', {})
        for client_id, pos in clients_data.items():
            if client_id not in self.remote_players:
                self.remote_players[client_id] = Player(pos['x'], pos['y'])
            else:
                self.remote_players[client_id].x = pos['x']
                self.remote_players[client_id].y = pos['y']

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
