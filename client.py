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

        running = True
        while running:

            running = game.display_map()
            game.send_player_data(client)
            game.receive_player_data(client)
    except ConnectionRefusedError:
        print("Connection refused")
    except ConnectionResetError:
        print("Server disconnected")
    finally:
        client.close()

if __name__ == "__main__":
    main()
