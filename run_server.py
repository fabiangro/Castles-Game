import sys
from server import Server


SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])

if __name__ == '__main__':
    game_server = Server(SERVER_IP, SERVER_PORT)
    game_server.main_loop()
