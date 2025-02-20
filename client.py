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

        client.recv(1024).decode()
        
        game = Game()
        game.receive_map(client)

        try:
            while True:
                game.display_map()
                game.send_player_data(client)
                game.receive_player_data(client)
        except ConnectionResetError:
            print("Server disconnected")
            client.close()
            return
    except ConnectionRefusedError:
        print("Connection refused")
        return