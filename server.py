import socket
import json
from game import Game
from map import generate_map 

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(input("Enter port: "))
    server.bind(('', port))
    server.listen(1)
    print(f"Server listening on port {port}")

    game = Game()
    print(f"\nWaiting for opponent...")

    conn, addr = server.accept()
    print(f"Opponent connected: {addr}")

    conn.send("ready".encode())

    game.send_map(conn)

    try:
        running = True
        while running:
            running = game.display_map()
            game.receive_player_data(conn)
            game.send_player_data(conn)
    except ConnectionResetError:
        print("Opponent disconnected")
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    main()
    