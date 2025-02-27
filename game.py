import pygame
import random
import json
import logging
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
        logging.info(f"Game initialized with map size: {map_size}")
    
    def get_spawn_position(self):
        validPos = []
        for y in range(len(self.game_map)):
            for x in range(len(self.game_map[y])):
                if self.game_map[y][x] == 0:
                    validPos.append([x, y])
                    print('X', end='')
                else:
                    logging.log(self.game_map[y][x], end ='')
            print()
        pos = validPos[random.randint(0, len(validPos) - 1)]
        pos[0] = 25
        pos[1] = 25
        print(pos)
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
        pygame.draw.rect(
            self.screen,
            local_color,
            (
                int(self.local_player.x * self.cell_size) - int(0.5 * self.cell_size),
                int(self.local_player.y * self.cell_size) - int(0.5 * self.cell_size),
                self.cell_size, self.cell_size
            )
        )
        # If local player has been tagged, render "OUT" text.
        if self.local_player.role == "tagged":
            text = self.font.render("OUT", True, (255, 255, 0))
            self.screen.blit(text, (int(self.local_player.x * self.cell_size), int(self.local_player.y * self.cell_size)))
        
        # Draw remote players.
        for client_id, player in self.remote_players.items():
            if player.role == "tagger":
                pcolor = (0, 255, 0)  # Tagger is green
            else:
                pcolor = (0, 0, 255)  # Runner is blue
            pygame.draw.rect(
                self.screen,
                pcolor,
                (
                    int(player.x * self.cell_size) - int(0.5 * self.cell_size),
                    int(player.y * self.cell_size) - int(0.5 * self.cell_size),
                    self.cell_size, self.cell_size
                )
            )

            if player.role == "tagged":
                text = self.font.render("OUT", True, (255, 255, 0))
                self.screen.blit(text, (int(player.x * self.cell_size), int(player.y * self.cell_size)))
        
        # **NEW:** Render tagger text in green at the top left.
        if self.local_player.role == "tagger":
            tag_text = self.font.render("You are the tagger", True, (0, 255, 0))
            self.screen.blit(tag_text, (10, 10))
            
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
                'y': self.local_player.y
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
            logging.debug(f"Client {self.client_id} role updated to {new_role}")

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
                    logging.debug(f"Remote player {client_id} updated: x={pos['x']}, y={pos['y']}, role={pos.get('role', 'runner')}")
                    # Optional: print each remote client's role for debugging.
                    


    def handle_movement(self, player, keys):
        # Store the previous position for collision checking
        prev_x = player.x
        prev_y = player.y

        # Get movement input
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.PLAYER_SPEED

        # Update position
        new_x = player.x + dx
        new_y = player.y + dy

        # Check for collisions with walls
        player_radius = 0.4  # Adjust this value to change collision boundary
        
        # Get the grid cells that the player might collide with
        left = int(new_x - player_radius)
        right = int(new_x + player_radius)
        top = int(new_y - player_radius)
        bottom = int(new_y + player_radius)

        # Check each potential collision cell
        collision = False
        for check_y in range(top, bottom + 1):
            for check_x in range(left, right + 1):
                if (0 <= check_y < len(self.game_map) and 
                    0 <= check_x < len(self.game_map[0]) and 
                    self.game_map[check_y][check_x] == 1):
                    
                    # Calculate the closest point on the wall to the player
                    closest_x = max(check_x, min(new_x, check_x + 1))
                    closest_y = max(check_y, min(new_y, check_y + 1))
                    
                    # Calculate distance from closest point
                    distance = ((new_x - closest_x) ** 2 + (new_y - closest_y) ** 2) ** 0.5
                    
                    if distance < player_radius:
                        collision = True
                        break
            if collision:
                break

        # If there's a collision, keep the old position on the colliding axis
        if collision:
            # Try moving on X axis only
            if self.check_collision(player.x + dx, player.y, player_radius):
                new_x = player.x
            
            # Try moving on Y axis only
            if self.check_collision(new_x, player.y + dy, player_radius):
                new_y = player.y

        # Update the player position
        player.x = new_x
        player.y = new_y
        logging.debug(f"Player moved to x={player.x}, y={player.y}")

    def check_collision(self, x, y, radius):
        """Helper method to check if a position collides with walls"""
        left = int(x - radius)
        right = int(x + radius)
        top = int(y - radius)
        bottom = int(y + radius)

        for check_y in range(top, bottom + 1):
            for check_x in range(left, right + 1):
                if (0 <= check_y < len(self.game_map) and 
                    0 <= check_x < len(self.game_map[0]) and 
                    self.game_map[check_y][check_x] == 1):
                    
                    closest_x = max(check_x, min(x, check_x + 1))
                    closest_y = max(check_y, min(y, check_y + 1))
                    
                    distance = ((x - closest_x) ** 2 + (y - closest_y) ** 2) ** 0.5
                    
                    if distance < radius:
                        return True
        return False

class Player:
    def __init__(self, x, y, role="runner"):
        self.x = x
        self.y = y
        self.speed = 15
        self.size = 1
        self.role = role
        logging.info(f"Player created: x={x}, y={y}, role={role}")
    
    def can_move(self, grid, new_x, new_y):
        epsilon = 0.001  # Small value to expand the bounding box

        left = int(new_x - self.size - epsilon)
        right = int(new_x + self.size + epsilon)
        top = int(new_y - self.size - epsilon)
        bottom = int(new_y + self.size + epsilon)

        if left < 0 or top < 0 or right >= len(grid[0]) or bottom >= len(grid):
            return False

        # Check every cell within the player's bounding box
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                if grid[y][x] == 1:
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
        
        if self.can_move(grid, new_x, new_y):
            self.x = new_x
            self.y = new_y
            logging.debug(f"Player moved to x={self.x}, y={self.y} (dt={dt})")
