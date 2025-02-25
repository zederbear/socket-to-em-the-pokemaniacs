import socket
import json
import threading
import random
import pygame
from game import Game, Player
from map import generate_map 

clients = []
clients_lock = threading.Lock()

def handle_client(conn, client_id, client_player):
    buffer = ""
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data
            # Process complete messages delimited by newline.
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

def broadcast_state(game, server_player):
    """Broadcast the current state (server and all clients) to every client."""
    with clients_lock:
        state = {
            "type": "state",
            "data": {
                "server": {"x": server_player.x, "y": server_player.y},
                "clients": {cid: {"x": pl.x, "y": pl.y} for cid, pl, _ in clients}
            }
        }
        msg = (json.dumps(state) + "\n").encode()
        for _, _, conn in clients:
            try:
                conn.sendall(msg)
            except Exception as e:
                print("Error sending state to a client:", e)

def accept_clients(server_socket, game, used_spawns):
    """Continuously accepts new clients and assigns them a spawn."""
    client_id_counter = 1
    while True:
        conn, addr = server_socket.accept()
        print(f"Client {client_id_counter} connected: {addr}")
        # Send the map so the client can initialize its game state.
        map_msg = json.dumps({"type": "map", "data": game.game_map}) + "\n"
        try:
            conn.sendall(map_msg.encode())
        except Exception as e:
            print("Error sending map:", e)
            conn.close()
            continue

        # Choose a spawn that is not already used.
        spawn = None
        valid_spawns = []
        for y, row in enumerate(game.game_map):
            for x, cell in enumerate(row):
                if cell == 0 and (x, y) not in used_spawns:
                    valid_spawns.append((x, y))
        
        if valid_spawns:
            spawn = random.choice(valid_spawns)
        else:
            spawn = (1, 1)  # Default spawn if no valid spawns are found
            print("No valid spawns found. Using default spawn.")
            
        used_spawns.add(spawn)
        client_player = Player(float(spawn[0]), float(spawn[1]))

        with clients_lock:
            clients.append((client_id_counter, client_player, conn))
        threading.Thread(target=handle_client, args=(conn, client_id_counter, client_player), daemon=True).start()
        client_id_counter += 1

def main():
    port = int(input("Enter port: "))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)  # Increase backlog if needed.
    print(f"Server listening on port {port}")

    game = Game()
    used_spawns = set()

    # Start accepting clients in a separate thread.
    threading.Thread(target=accept_clients, args=(server_socket, game, used_spawns), daemon=True).start()

    server_player = game.local_player

    # Main game loop: process input, update the game, render and broadcast state.
    running = True
    while running:
        running = game.display_map()  # This handles movement, rendering, and events.
        broadcast_state(game, server_player)
    
    pygame.quit()  # Cleanly exit pygame when done.

if __name__ == "__main__":
    main()
