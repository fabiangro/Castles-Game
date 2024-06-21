import subprocess
import time


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def start_server(ip, port):
    return subprocess.Popen(['python', 'run_server.py', ip, str(port)])


def start_client(ip, port, name):
    return subprocess.Popen(['python', 'run_client.py', ip, str(port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    SERVER_IP = 'localhost'
    SERVER_PORT = 5555

    if not is_port_in_use(SERVER_PORT):
        SERVER_PORT += 1
    server_process = start_server(SERVER_IP, SERVER_PORT)
    time.sleep(1)

    client1_process = start_client(SERVER_IP, SERVER_PORT, 'client1')
    client2_process = start_client(SERVER_IP, SERVER_PORT, 'client2')

    client1_process.stdin.write(b'client1\n')
    client1_process.stdin.flush()
    client2_process.stdin.write(b'client2\n')
    client2_process.stdin.flush()

    client1_process.wait()
    client2_process.wait()

    server_process.terminate()






