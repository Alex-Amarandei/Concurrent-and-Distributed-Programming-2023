import socket
import time
from utils.json_utils import read_json_file
import sys

sys.set_int_max_str_digits(0)


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

    actually_received = 0
    message_count = 0
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        actually_received += len(data)
        message_count += 1

        client_socket.send(b"OK")

        if not data:
            break

    print_report("TCP - Stop-Wait", message_count, actually_received)

    close_connection(server_socket)


def TCP_Streaming(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_STREAM)

    client_socket, address = server_socket.accept()
    print(f"{address} connected.")

    actually_received, message_count = 0, 0

    while True:
        data = client_socket.recv(BUFFER_SIZE)
        actually_received += len(data)
        message_count += 1
        if not data:
            break

    print_report("TCP - Streaming", message_count, actually_received)

    close_connection(server_socket)


def UDP_Stop_and_Wait(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_DGRAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)

    actually_received, message_count = 0, 0
    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        actually_received += len(data)
        message_count += 1

        server_socket.sendto(b"OK", client_address)

        if not data:
            break

    print_report("UDP - Stop and Wait", message_count, actually_received)

    close_connection(server_socket)


def UDP_Streaming(config, common_config):
    BUFFER_SIZE = config["BUFFER_SIZE"]
    server_socket = init_connection(config, common_config, socket.SOCK_DGRAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)

    actually_received, message_count = 0, 0
    while True:
        data, _ = server_socket.recvfrom(BUFFER_SIZE)
        actually_received += len(data)
        message_count += 1
        if not data:
            break

    print_report(
        "UDP - Streaming",
        message_count,
        actually_received,
    )

    close_connection(server_socket)


def main():
    config, common_config, protocol, method = get_input()
    methods = get_methods_dictionary()

    methods[protocol][method](config[protocol][method], common_config)


if __name__ == "__main__":
    main()
