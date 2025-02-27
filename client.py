import socket
import json
from game import Game
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='client.log'
    )

def receive_message(client_socket, buffer):
    while "\n" not in buffer:
        try:
            part = client_socket.recv(1024).decode('utf-8')
            if not part:
                return None, buffer  # Connection closed
            buffer += part
        except ConnectionResetError:
            return None, buffer  # Connection reset

    message, rest = buffer.split("\n", 1)
    if not message.strip():
        # If the message is empty, recursively try to get the next message.
        return receive_message(client_socket, rest)
    return json.loads(message), rest


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_ip = input("Enter server IP: ")
    port = int(input("Enter port: "))

    try:
        client.connect((server_ip, port))
        print("Connected to server!")
        
        game = Game()
        buffer = ""
        buffer = game.receive_map(client, buffer)


        # Receive client ID
        message, buffer = receive_message(client, buffer)
        if message and message.get("type") == "client_id":
            game.client_id = str(message["data"])  # Store client ID as string
            print(f"Received client ID: {game.client_id}")
        else:
            print("Failed to receive client ID.")
            return  # Exit if no client ID
        
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
