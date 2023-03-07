import socket
import time
from utils.json_utils import read_json_file


def init_connection(config, common_config, socket_type):
    PORT = config["PORT"]
    HOST = common_config["HOST"]

    server_socket = socket.socket(socket.AF_INET, socket_type)
    server_socket.bind((HOST, PORT))

    if socket_type == socket.SOCK_DGRAM:
        print(f"Server on {HOST}:{PORT}...")
    else:
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}...")

    return server_socket


def close_connection(server_socket):
    time.sleep(1)
    print("Client disconnected.")

    server_socket.close()


def print_report(protocol, number, bytes_received):
    print(
        f"Used Protocol: {protocol}\n"
        + f"Number of messages: {number}\n"
        + f"Number of bytes: {bytes_received}\n"
    )


def get_input():
    config = read_json_file("data/config.json")
    common_config = read_json_file("data/common_config.json")

    protocol = input("Choose a protocol (TCP or UDP): ")
    method = input("Choose a method (Stop and Wait or Streaming): ")

    return config, common_config, protocol, method


def get_methods_dictionary():
    methods = {
        "TCP": {"Stop and Wait": TCP_Stop_and_Wait, "Streaming": TCP_Streaming},
        "UDP": {"Stop and Wait": UDP_Stop_and_Wait, "Streaming": UDP_Streaming},
    }

    return methods


def TCP_Stop_and_Wait(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_STREAM)

    client_socket, address = server_socket.accept()
    print(f"{address} connected.")

    message_size_bytes = client_socket.recv(BUFFER_SIZE)
    message_size = int.from_bytes(message_size_bytes, byteorder="big")

    print(f"Receiving message of size {message_size} bytes...")

    received_bytes, num_messages = 0, 0

    while received_bytes < message_size:
        data = client_socket.recv(BUFFER_SIZE)
        received_bytes += len(data)
        num_messages += 1

        client_socket.send(b"ACK")

    print_report("TCP - Stop and Wait", num_messages, received_bytes)

    client_socket.send(b"Message received.")

    close_connection(server_socket)


def TCP_Streaming(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_STREAM)

    client_socket, address = server_socket.accept()
    print(f"{address} connected.")

    while True:
        message_size_bytes = client_socket.recv(8)

        if not message_size_bytes:
            break

        message_size = int.from_bytes(message_size_bytes, byteorder="big")

        received_bytes, num_messages = 0, 0

        message = b""

        while received_bytes < message_size:
            data = client_socket.recv(BUFFER_SIZE)
            message += data
            received_bytes += len(data)
            num_messages += 1

        print_report("TCP - Streaming", num_messages, received_bytes)

        client_socket.send(b"Message received.")

    close_connection(server_socket)


def UDP_Stop_and_Wait(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_DGRAM)

    received_bytes, num_messages, done = 0, 0, False

    while not done:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        received_bytes += len(data)
        num_messages += 1

        server_socket.sendto(b"ACK", address)

        if not data:
            break

        if data == b"done":
            done = True

    print_report("UDP - Stop and Wait", num_messages, received_bytes)

    close_connection(server_socket)


def UDP_Streaming(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_DGRAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)

    received_bytes, num_messages, done = 0, 0, False

    while not done:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        received_bytes += len(data)
        num_messages += 1

        if not data:
            break

        if data == b"done":
            done = True

        server_socket.sendto(b"ack", address)

    print_report("UDP - Streaming", num_messages, received_bytes)

    close_connection(server_socket)


def main():
    config, common_config, protocol, method = get_input()
    methods = get_methods_dictionary()

    methods[protocol][method](config[protocol][method], common_config)


if __name__ == "__main__":
    main()
