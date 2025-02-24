import socket
import json
from game import Game

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_ip = input("Enter server IP: ")
    port = int(input("Enter port: "))

    try:
        client.connect((server_ip, port))
        print("Connected to server!")
        
        game = Game()
        game.receive_map(client)  # Receive and update the map
        
        running = True
        while running:
            running = game.display_map()
            game.send_player_data(client)
            game.receive_state(client)  # Now receives complete messages
    except ConnectionRefusedError:
        print("Connection refused")
    except ConnectionResetError:
        print("Server disconnected")
    finally:
        client.close()

if __name__ == "__main__":
    main()
