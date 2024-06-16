import socket
import pickle
from typing import Dict, Union


class Network:
    """A class representing a network connection.

    :param server_ip: The IP address of the server to connect.
    :param port: The port of the server to connect:
    """

    def __init__(self, server_ip, port) -> None:
        #: The socket object for the connection.
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #: The IP address of the server.
        self.server_ip = server_ip

        #: The port of the server.
        self.port = port

        #: The maximum message length for receiving data.
        self.max_msg_length = 1024 * 8

    def connect(self) -> None:
        """Connect to the server."""
        self.my_socket.connect((self.server_ip, self.port))

    def send(self, data: str) -> None:
        """Send data to the server.

        :param data: The data to send.
        """

        self.my_socket.send(data.encode())

    def receive_data(self) -> Union[str, Dict]:
        """_summary_

        :return: The received data.
        """

        rec_data = pickle.loads(self.my_socket.recv(self.max_msg_length))
        return rec_data

    def close(self) -> None:
        """Close the network connection."""
        self.my_socket.close()
