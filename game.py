import pygame
import random
import json
import logging
from powerup import Powerup
from map import generate_map

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='game.log'
    )

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
        self.font = pygame.font.SysFont(None, 24)  # font for text rendering
        self.local_player = Player(*self.get_spawn_position())
        self.remote_players = {}
        self.client_id = None
        self.powerup_positions = []
        self.powerup = Powerup()
        logging.info(f"Game initialized with map size: {map_size}")
    
    def get_spawn_position(self):
        validPos = []
        for y in range(len(self.game_map)):
            for x in range(len(self.game_map[y])):
                if self.game_map[y][x] == 0:
                    validPos.append([x, y])
                    # print('X', end='')
                else:
                    # print(self.game_map[y][x], end ='')
                    pass
            # print()
        pos = validPos[random.randint(0, len(validPos) - 1)]
        pos[0] = 25
        pos[1] = 25
        logging.debug(pos)
        logging.debug(f"Spawn position: {pos}")
        return float(pos[0]), float(pos[1])

    def display_map(self):
        dt = self.clock.tick(60) / 1000
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
        
        # Local player color: green if tagger, red if runner or tagged.
        local_color = (0, 255, 0) if self.local_player.role == "tagger" else (255, 0, 0)
        local_color = (0, 0, 0)
        if self.local_player.ghost:
            local_color = (128, 0, 128, 50)
        elif self.local_player.ghost and self.local_player.role == "tagger":
            local_color = (32, 0, 32, 50)
        elif self.local_player.shield:
            local_color = (255, 255, 0)    
        elif self.local_player.role == "tagger":
            local_color = (0, 255, 0)
        else:
            local_color = (255, 0, 0)
        pygame.draw.rect(
            self.screen,
            local_color,
            (
                round(self.local_player.x * self.cell_size) - int(0.5 * self.cell_size),  # Remove the - int(0.5 * self.cell_size)
                round(self.local_player.y * self.cell_size) - int(0.5 * self.cell_size),  # Remove the - int(0.5 * self.cell_size)
                self.cell_size,
                self.cell_size
            )
        )
        
        # Draw remote players.
        for _, player in self.remote_players.items():
            if player.ghost == True: # runner ghost is purple
                pcolor = (128, 0, 128, 50)
            elif player.ghost and player.role == "tagger": # tagger ghost super dark purple
                pcolor = (32, 0, 32, 50)
            elif player.role == "tagger":
                pcolor = (0, 255, 0)  # Tagger is green
            else:
                pcolor = (0, 0, 255)  # Runner is blue
            pygame.draw.rect(
                self.screen,
                pcolor,
                (
                    round(player.x * self.cell_size),  # Remove the - int(0.5 * self.cell_size)
                    round(player.y * self.cell_size),  # Remove the - int(0.5 * self.cell_size)
                    self.cell_size,
                    self.cell_size
                )
            )
        
        for powerup in self.powerup_positions:
            pygame.draw.rect(
                self.screen,
                self.powerup.draw_powerup(powerup["type"]),
                (
                    round(float(powerup["position"][0]) * self.cell_size),
                    round(float(powerup["position"][1]) * self.cell_size),
                    self.cell_size - self.cell_size/3,
                    self.cell_size - self.cell_size/3
                )
            )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Player quit the game.")
                return False
        return True

    
    def send_map(self, conn):
        data = json.dumps(self.game_map)
        conn.sendall(data.encode('utf-8'))
        logging.debug("Map data sent to client.")

    def receive_map(self, conn, buffer):
        try:
            while "\n" not in buffer:
                part = conn.recv(1024).decode('utf-8')
                if not part:
                    return buffer  # Connection closed; return current buffer.
                buffer += part
            line, buffer = buffer.split("\n", 1)
            msg = json.loads(line)
            if msg.get("type") == "map":
                self.game_map = msg["data"]
                logging.debug("Map data received from client.")
            else:
                self.game_map = msg
                logging.debug("Map data received from client (no type).")
            return buffer  # Return the updated buffer.
        except Exception as e:
            logging.error(f"Error receiving map: {e}")
            return buffer

    
    def send_player_data(self, conn):
        data = {
            'type': 'pos',
            'data': {
                'x': self.local_player.x, 
                'y': self.local_player.y,
                'ghost': self.local_player.ghost,
                'shield': self.local_player.shield
            }
        }
        msg = json.dumps(data) + '\n'
        conn.sendall(msg.encode('utf-8'))
        logging.debug(f"Player data sent: x={self.local_player.x}, y={self.local_player.y}")
    
    def receive_state(self, conn):
        buffer = ""
        try:
            while "\n" not in buffer:
                part = conn.recv(1024).decode('utf-8')
                if not part:
                    return
                buffer += part
            line, rest = buffer.split("\n", 1)
            try:
                state_data = json.loads(line)
            except Exception as e:
                logging.error(f"Error receiving state: {e}, State message: {line}")
                return
        except Exception as e:
            logging.error(f"Error receiving state (outer): {e}")
            return

        # Debug print the full state message

        # Update the local player's role even if it hasn't changed.
        clients_data = state_data.get('data', {}).get('clients', {})
        if self.client_id in clients_data:
            pos = clients_data[self.client_id]
            new_role = pos.get('role', self.local_player.role)
            self.local_player.role = new_role
            self.local_player.ghost = pos.get('ghost', self.local_player.ghost)
            if self.local_player.ghost:
                self.local_player.collision = False
            else:
                self.local_player.collision = True
            self.local_player.speed = pos.get('speed', self.local_player.speed)
            self.local_player.shield = pos.get('shield', self.local_player.shield)
            logging.debug(f"Client {self.client_id} role updated to {new_role}")

        logging.debug(state_data.get('data', {}).get('powerups', []))
        logging.debug(f"Type: {type(state_data.get('data', {}).get('powerups', []))}")
        self.powerup_positions = state_data.get('data', {}).get('powerups', [])
        
        # Process remote clients.
        for client_id, pos in clients_data.items():
            if client_id != self.client_id:  # Exclude local player
                if client_id not in self.remote_players:
                    self.remote_players[client_id] = Player(pos['x'], pos['y'], pos.get('role', 'runner'))
                    logging.info(f"New remote player added: Client ID {client_id}, x={pos['x']}, y={pos['y']}, role={pos.get('role', 'runner')}")
                else:
                    self.remote_players[client_id].x = pos['x']
                    self.remote_players[client_id].y = pos['y']
                    self.remote_players[client_id].role = pos.get('role', 'runner')
                    self.remote_players[client_id].ghost = pos["ghost"]
                    self.remote_players[client_id].shield = pos["shield"]
                    logging.debug(f"Remote player {client_id} updated: x={pos['x']}, y={pos['y']}, role={pos.get('role', 'runner')}")
                    # Optional: print each remote client's role for debugging.
        
                    
class Player:
    def __init__(self, x, y, role="runner"):
        self.x = x
        self.y = y
        self.speed = 15
        self.size = 0.5
        self.role = role
        self.ghost = False
        self.shield = False
        self.collision = True
        logging.info(f"Player created: x={x}, y={y}, role={role}")
    
    def can_move(self, grid, new_x, new_y):
        """Check if the player can move to the new position without colliding."""
        left = int(new_x - self.size)
        right = int(new_x + self.size)
        top = int(new_y - self.size)
        bottom = int(new_y + self.size)

        if left < 0 or top < 0 or right >= len(grid[0]) or bottom >= len(grid):
            if self.collision:
                return False
            else:
                return True
        if grid[top][left] == 1 or grid[top][right] == 1 or grid[bottom][left] == 1 or grid[bottom][right] == 1:
            if self.collision:
                return False
            else:
                return True
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