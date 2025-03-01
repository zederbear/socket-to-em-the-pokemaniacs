import socket
import json
import threading
import random
import pygame
from game import Game, Player
from powerup import Powerup


clients = []
clients_lock = threading.Lock()
shutdown_event = threading.Event()
powerup_timers = {}
powerup_lock = threading.Lock()

def update_powerup_timers():
    with powerup_lock:
        for client_id in list(powerup_timers.keys()):
            for effect in list(powerup_timers[client_id].keys()):
                if powerup_timers[client_id][effect] is not None:
                    powerup_timers[client_id][effect] -= 1
                    print(f"Timer for client {client_id}, effect {effect}: {powerup_timers[client_id][effect]}")
                    if powerup_timers[client_id][effect] <= 0:
                        print(f"Removing {effect} effect from client {client_id}")
                        with clients_lock:
                            for cid, pl, _ in clients:
                                if str(cid) == client_id:
                                    if effect == "speed":
                                        pl.speed /= 1.5
                                        print(f"Speed reset for player {cid}")
                                    elif effect == "ghost":
                                        pl.ghost = False
                                        pl.collision = True
                                        print(f"Ghost reset for player {cid}")
                                    elif effect == "shield":
                                        pl.shield = False
                                        print(f"Shield reset for player {cid}")
                        del powerup_timers[client_id][effect]
            if not powerup_timers[client_id]:
                del powerup_timers[client_id]

def is_valid_spawn(game_map, x, y):
    """Checks if the given coordinates are a valid spawn position (black cell)."""
    if 0 <= y < len(game_map) and 0 <= x < len(game_map[0]):
        return game_map[y][x] == 0
    return True

def handle_client(conn, client_id, client_player):
    buffer = ""
    try:
        while not shutdown_event.is_set():  # Check for shutdown signal
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    msg = json.loads(line)
                    if msg["type"] == "pos":
                        pos = msg["data"]
                        client_player.x = pos["x"]
                        client_player.y = pos["y"]
                except Exception as e:
                    print(f"Error processing message from client {client_id}: {e}")
    except Exception as e:
        print(f"Client {client_id} connection error: {e}")
    finally:
        print(f"Client {client_id} disconnected")
        conn.close()
        with clients_lock:
            for i, (cid, _, _) in enumerate(clients):
                if cid == client_id:
                    clients.pop(i)
                    break

def broadcast_state(game, server_player, powerups):
    with clients_lock:
        state = {
            "type": "state",
            "data": {
                "server": {
                    "id": "server",
                    "x": server_player.x,
                    "y": server_player.y,
                    "role": server_player.role
                },
                "clients": {
                    str(cid): {
                        "id": str(cid),
                        "x": pl.x - 0.4,
                        "y": pl.y - 0.4,
                        "role": pl.role,
                        "ghost": pl.ghost,
                        "shield": pl.shield,
                        "speed": pl.speed
                    } for cid, pl, _ in clients
                },
                "powerups": powerups.powerup_positions
            }
        }
        msg = (json.dumps(state) + "\n").encode()
        for _, _, conn in clients:
            try:
                conn.sendall(msg)
            except Exception as e:
                print("Error sending state to a client:", e)




def check_tagging(game):
    tagger = None
    with clients_lock:
        for cid, pl, _ in clients:
            if pl.role == "tagger":
                tagger = pl
                break
    if tagger:
        # Check all clients.
        with clients_lock:
            for cid, pl, _ in clients:
                if pl.role == "runner" and abs(tagger.x - pl.x) < 0.5 and abs(tagger.y - pl.y) < 0.5:
                    if pl.shield:
                        return
                    else:
                        pl.role = "tagger"

def accept_clients(server_socket, game, used_spawns):
    """Continuously accepts new clients and assigns them a spawn position.
    
    Args:
        server_socket: The main server socket listening for connections
        game: The Game instance containing map and game state
        used_spawns: Set tracking already used spawn positions
    """
    client_id_counter = 1
    tagger_assigned = False  # Flag to ensure only one tagger is assigned

    while not shutdown_event.is_set():
        try:
            # Accept new client connection
            conn, addr = server_socket.accept()
            print(f"Client {client_id_counter} connected: {addr}")

            # Send initial game map to client
            map_msg = json.dumps({"type": "map", "data": game.game_map}) + "\n"
            try:
                conn.sendall(map_msg.encode())
            except Exception as e:
                print("Error sending map:", e)
                conn.close()
                continue

            # Send unique client ID
            id_msg = json.dumps({"type": "client_id", "data": client_id_counter}) + "\n"
            try:
                conn.sendall(id_msg.encode())
            except Exception as e:
                print("Error sending client ID:", e)
                conn.close()
                continue

            # Assign spawn position and role
            while True:
                # Generate random spawn coordinates
                x = random.randint(0, len(game.game_map[0]) - 1)
                y = random.randint(0, len(game.game_map) - 1)
                if is_valid_spawn(game.game_map, x, y):
                    # Second player becomes tagger
                    if client_id_counter == 2 and not tagger_assigned:
                        client_player = Player(float(x), float(y), role="tagger")
                        tagger_assigned = True
                    else:
                        client_player = Player(float(x), float(y), role="runner")
                    break

            # Add new client to active clients list
            with clients_lock:
                clients.append((client_id_counter, client_player, conn))
            
            # Start client handler thread
            threading.Thread(target=handle_client, 
                           args=(conn, client_id_counter, client_player), 
                           daemon=True).start()
            client_id_counter += 1

        except socket.timeout:
            continue # Continue to check the shutdown_event
        except Exception as e:
            print(f"Error accepting client: {e}")
            break

def main():
    # Initialize server socket
    port = int(input("Enter port: "))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)  # Allow up to 5 pending connections
    server_socket.settimeout(1) # 1 second timeout for accept()
    print(f"Server listening on port {port}")

    # Initialize game state
    game = Game()
    used_spawns = set()
    powerups = Powerup()
    powerups.spawn_powerups()

    # Start client acceptance thread
    accept_thread = threading.Thread(target=accept_clients, 
                                   args=(server_socket, game, used_spawns), 
                                   daemon=True)
    accept_thread.start()

    server_player = game.local_player

    # Main game loop
    running = True
    try:
        while running:
            # Update game state
            running = game.display_map()
            
            # Reset server player position
            server_player.x = 0.0
            server_player.y = 0.0
            server_player.role = game.local_player.role

            with clients_lock:
                for cid, pl, _ in clients:
                    for powerup in powerups.powerup_positions[:]:
                        powerup_pos = powerup['position']
                        distance = ((pl.x - powerup_pos[0]) ** 2 + (pl.y - powerup_pos[1]) ** 2) ** 0.5
                        if distance < 1:  # Player radius
                            print(f"Player {cid} collected {powerup['type']} powerup")
                            duration = powerups.apply_powerup_effect(powerup['type'], pl)
                            client_id = str(cid)
                            with powerup_lock:
                                if client_id not in powerup_timers:
                                    powerup_timers[client_id] = {}
                                powerup_timers[client_id][powerup['type']] = duration
                                print(f"Set timer for client {client_id}, effect {powerup['type']}: {duration}")
                            powerups.powerup_positions.remove(powerup)

# Add timer update before broadcast_state
            update_powerup_timers()

            broadcast_state(game, server_player, powerups)
            check_tagging(game)
    finally:
        shutdown_event.set()  # Signal shutdown to all threads
        print("Shutting down server...")

        # Close all client connections
        with clients_lock:
            for _, _, conn in clients:
                try:
                    conn.close()
                except Exception as e:
                    print("Error closing client connection:", e)

        server_socket.close()
        accept_thread.join() # Wait for the accept thread to finish
        pygame.quit()  # Cleanly exit pygame when done.
        print("Server shutdown complete.")

if __name__ == "__main__":
    main()
