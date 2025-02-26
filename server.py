import socket
import json
import threading
import time
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
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    msg = json.loads(line)
                    if msg["type"] == "pos":
                        pos = msg["data"]
                        client_player.x = pos["x"]
                        client_player.y = pos["y"]
                        # Update role if sent by client.
                        if "role" in pos:
                            client_player.role = pos["role"]
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
    with clients_lock:
        state = {
            "type": "state",
            "data": {
                "server": {"x": server_player.x, "y": server_player.y, "role": server_player.role},
                "clients": {str(cid): {"x": pl.x, "y": pl.y, "role": pl.role} for cid, pl, _ in clients}
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
                    pl.role = "tagged"
        # Check the server's local player.
        if game.local_player.role == "runner" and abs(tagger.x - game.local_player.x) < 0.5 and abs(tagger.y - game.local_player.y) < 0.5:
            game.local_player.role = "tagged"

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
        for y, row in enumerate(game.game_map):
            for x, cell in enumerate(row):
                if cell == 0 and (x, y) not in used_spawns:
                    spawn = (x, y)
                    break
            if spawn:
                break
        if not spawn:
            spawn = (1, 1)
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
        check_tagging(game)
    
    pygame.quit()  # Cleanly exit pygame when done.

if __name__ == "__main__":
    main()
