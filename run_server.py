from server import Server


SERVER_IP = 'localhost'
SERVER_PORT = 5556

if __name__ == '__main__':
    game_server = Server(SERVER_IP, SERVER_PORT)
    game_server.main_loop()
