import sys
from client import Client


SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])


if __name__ == "__main__":
    player_name = input("Enter your name: ")
    c = Client(player_name)

    c.start(SERVER_IP, SERVER_PORT)
