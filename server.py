from typing import Dict, List, Any, Union
import pickle
import random
import socket
import select
from game import AntsGame


MAX_MSG_LENGTH = 1024*8
DISCONNECT_MESSAGE = ""


class Server:
    """A class representing a server for a game.
    """

    def __init__(self, server_ip="localhost", server_port=5556) -> None:
        #: IP to host server, 'localhost' default
        self.server_ip = server_ip

        #: port to host server, 5556, default
        self.server_port = server_port

        #: List of clients connected to the server.
        self.connected_clients: List[Any] = []

        #: Dictionary with players as keys, and their unique ID as value.
        self.clients_ids: Dict[Any, int] = {}

        #: List of clients waiting to receive data.
        self.clients_to_respond: List[Any] = []

        #: Instance of Game class representing the server's game.
        self.game: Union[None, AntsGame] = None

    def start_server(self) -> Any:
        """Start the server.

        :return: The server socket.
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        current_server = 'localhost'
        print(f"Starting server on {current_server}:{self.server_port}")
        server_socket.bind((self.server_ip, self.server_port))
        server_socket.listen()
        print("Listening for clients...")
        return server_socket

    def disconnect_client(self, socket_to_remove: Any, client_address: int) -> None:
        """Disconnect a client from the server.

        :param socket_to_remove: The socket to remove.
        :param client_address: The client address.
        """

        print(client_address, "Connection closed")
        self.connected_clients.remove(socket_to_remove)
        self.game.remove_player(self.clients_ids[socket_to_remove])
        del self.clients_ids[socket_to_remove]
        socket_to_remove.close()
        self.close_empty_game()

    def close_empty_game(self) -> None:
        """Close the game if there are no players."""
        if len(self.game.players) == 0:
            self.game = None
            print("~ Game has been closed")

    def create_client_id(self) -> int:
        """Create a unique client ID.

        :return: New client ID.
        """

        client_id = random.randint(1000, 9999)
        while client_id in self.clients_ids.values():
            client_id = random.randint(1000, 9999)
        return client_id

    def handle_new_client(self, client_socket: Any, client_address: int) -> None:
        """

        :param client_socket: The client socket.
        :param client_address: The client address.
        """

        client_id = self.create_client_id()


        if self.game is not None:
            if not self.game.is_full() and not self.game.has_started:
                self.connected_clients.append(client_socket)
                self.clients_ids[client_socket] = client_id

                self.game.add_player(client_id)
                print("New client joined:", client_address)
            return
        self.connected_clients.append(client_socket)
        self.clients_ids[client_socket] = client_id

        self.game = AntsGame()
        self.game.add_player(client_id)
        print("New client joined:", client_address)

    def handle_client_rec_data(self, current_socket: Any, client_address: int) -> None:
        """Handle a new client connection.

        :param current_socket: The client socket.
        :param client_address: The client address.
        """

        try:
            data = current_socket.recv(MAX_MSG_LENGTH).decode()
            if data == DISCONNECT_MESSAGE:
                self.disconnect_client(current_socket, client_address)
            else:
                self.clients_to_respond.append((current_socket, data))
        except:
            self.disconnect_client(current_socket, client_address)

    def handle_player_action(self, player_socket: Any, rec_data: str) -> None:
        """Handle receiving data from a client.

        :param player_socket: The current socket.
        :param rec_data: The client address.
        """

        client_id = self.clients_ids[player_socket]
        status = self.game.player_action(client_id, rec_data)
        # print(status)
        player_socket.send(pickle.dumps(status))

    def send_all_messages(self, ready_to_write: List) -> None:
        """Send all messages to the clients.

        :param ready_to_write: The list of sockets ready to write.
        """

        for client, msg in self.clients_to_respond:
            if client in ready_to_write:
                self.handle_player_action(client, msg)
                self.clients_to_respond.remove((client, msg))

    def main_loop(self) -> None:
        """The main loop of the server."""
        server_socket = self.start_server()

        while True:
            ready_to_read, ready_to_write, in_error = select.select(
                [server_socket] + self.connected_clients, self.connected_clients, [])

            for current_socket in ready_to_read:
                if current_socket is server_socket:
                    client_socket, client_address = current_socket.accept()
                    self.handle_new_client(client_socket, client_address)
                else:
                    self.handle_client_rec_data(current_socket, client_address)

            self.send_all_messages(ready_to_write)
