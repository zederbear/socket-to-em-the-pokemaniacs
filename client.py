import socket
import json
import threading
import pygame
import time
from game import Player

# Networking
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = input("Enter server IP: ")
port = int(input("Enter port: "))

try:
    client_socket.connect((server_ip, port))
    print("Connected to server")
except Exception as e:
    print("Unable to connect:", e)
    exit()

# Global values – will be set on receipt of the map from server.
game_map = None
CELL_SIZE = 10  # Should match the server!
MAP_SIZE = None

client_player = None
server_player = None  # represents the remote (server's) player

# First, wait to receive the map from the server.
while game_map is None:
    try:
        msg = client_socket.recv(4096).decode()
        if msg:
            data = json.loads(msg)
            if data["type"] == "map":
                game_map = data["data"]
                MAP_SIZE = len(game_map)
                # Set a spawn for the client player (client spawn) and a placeholder for server player
                # For simplicity, choose first available floor.
                def find_spawn(map_grid):
                    for y, row in enumerate(map_grid):
                        for x, cell in enumerate(row):
                            if cell == 0:
                                return (x, y)
                    return (1, 1)
                spawn = find_spawn(game_map)
                client_player = Player(float(spawn[0]), float(spawn[1]))
                # Initialize the server (remote) player's position.
                server_player = Player(float(spawn[0]), float(spawn[1]))
    except Exception as e:
        print("Error receiving map:", e)

def network_listener(sock):
    """Listen for messages from the server to update server player's position."""
    global server_player
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            data = json.loads(msg)
            if data["type"] == "pos":
                pos = data["data"]
                server_player.x = pos["x"]
                server_player.y = pos["y"]
        except Exception as e:
            print("Network error:", e)
            break
    sock.close()

threading.Thread(target=network_listener, args=(client_socket,), daemon=True).start()

# Pygame initialization
pygame.init()
screen_size = MAP_SIZE * CELL_SIZE
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Client - Blue Player")
clock = pygame.time.Clock()

white = (255, 255, 255)  # walls
black = (0, 0, 0)        # floor
blue = (0, 0, 255)       # client player
red = (255, 0, 0)        # server player

running = True
while running:
    dt = clock.tick(60) / 1000.0  # seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update client player movement based on keyboard input.
    client_player.handle_movement(game_map, dt)

    # Send client player's position to server.
    try:
        msg = json.dumps({"type": "pos", "data": {"x": client_player.x, "y": client_player.y}})
        client_socket.send(msg.encode())
    except Exception as e:
        print("Send error:", e)
        running = False

    # Drawing
    screen.fill(black)
    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(screen, white, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw players.
    pygame.draw.rect(screen, blue, (int(client_player.x * CELL_SIZE), int(client_player.y * CELL_SIZE), CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, red, (int(server_player.x * CELL_SIZE), int(server_player.y * CELL_SIZE), CELL_SIZE, CELL_SIZE))
    
    pygame.display.flip()

pygame.quit()
client_socket.close()


