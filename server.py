import socket
import threading
import json
import pygame
import time
from map import generate_map
from game import Player

# Game parameters
MAP_SIZE = 51
CELL_SIZE = 10  # Adjust display size as needed

# Generate map and choose spawn positions
game_map = generate_map(MAP_SIZE)

# For simplicity, use a fixed spawn if possible; otherwise, search for a floor (cell==0)
def find_spawn(map_grid):
    for y, row in enumerate(map_grid):
        for x, cell in enumerate(row):
            if cell == 0:
                return (x, y)
    return (1, 1)

server_spawn = find_spawn(game_map)
client_spawn = find_spawn(game_map)

server_player = Player(float(server_spawn[0]), float(server_spawn[1]))
client_player = Player(float(client_spawn[0]), float(client_spawn[1]))

# Networking
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000))
server_socket.listen(1)
print("Waiting for connection...")

conn, addr = server_socket.accept()
print(f"Connected to {addr}")

def network_listener(conn):
    """Listen for messages from the client to update client player's position."""
    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            data = json.loads(msg)
            if data["type"] == "pos":
                pos = data["data"]
                client_player.x = pos["x"]
                client_player.y = pos["y"]
        except Exception as e:
            print("Network error:", e)
            break
    conn.close()

threading.Thread(target=network_listener, args=(conn,), daemon=True).start()

# Pygame initialization
pygame.init()
screen_size = MAP_SIZE * CELL_SIZE
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Server - Red Player")
clock = pygame.time.Clock()

white = (255, 255, 255)  # walls
black = (0, 0, 0)        # floor
red = (255, 0, 0)        # server player
blue = (0, 0, 255)       # client player

running = True
while running:
    dt = clock.tick(60) / 1000.0  # seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update server player movement based on keyboard input.
    server_player.handle_movement(game_map, dt)

    # Send server player's position to client.
    try:
        msg = json.dumps({"type": "pos", "data": {"x": server_player.x, "y": server_player.y}})
        conn.send(msg.encode())
    except Exception as e:
        print("Send error:", e)
        running = False

    # Drawing
    screen.fill(black)
    # Draw map: walls are drawn in white.
    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(screen, white, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw players.
    pygame.draw.rect(screen, red, (int(server_player.x * CELL_SIZE), int(server_player.y * CELL_SIZE), CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, blue, (int(client_player.x * CELL_SIZE), int(client_player.y * CELL_SIZE), CELL_SIZE, CELL_SIZE))

    pygame.display.flip()

pygame.quit()
server_socket.close()