from client import Client


SERVER_IP = 'localhost'
SERVER_PORT = 5555

if __name__ == "__main__":

    player_name = input("Enter your name: ")
    c = Client(player_name)

    c.start()
