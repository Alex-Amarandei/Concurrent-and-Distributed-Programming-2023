import socket
import time
from utils.json_utils import read_json_file
from utils.generate_file import delete_file, create_file
import sys

sys.set_int_max_str_digits(0)


def get_data(message_size):
    delete_file("data/data.txt")
    create_file("data/data.txt", message_size)

    with open("data/data.txt", "r") as f:
        data = f.read()

        return data.encode("utf-8")


def get_input():
    config = read_json_file("data/config.json")
    common_config = read_json_file("data/common_config.json")

    protocol = input("Choose a protocol (TCP or UDP): ")
    method = input("Choose a method (Stop and Wait or Streaming): ")
    message_size = input(
        "The size of your message (1MB, 10MB, 50MB, 100MB, 500MB, 1GB, 2GB): "
    )

    return config, common_config, protocol, method, message_size


def get_methods_dictionary():
    methods = {
        "TCP": {"Stop and Wait": TCP_Stop_and_Wait, "Streaming": TCP_Streaming},
        "UDP": {"Stop and Wait": UDP_Stop_and_Wait, "Streaming": UDP_Streaming},
    }

    return methods


def print_report(protocol, number, bytes_sent, time_elapsed):
    print(
        f"Used Protocol: {protocol}\n"
        + f"Number of messages: {number}\n"
        + f"Number of bytes: {bytes_sent}\n"
        + f"Total time: {time_elapsed}"
    )


def TCP_Stop_and_Wait(config, common_config, message_size):
    PORT = config["PORT"]
    HOST = common_config["HOST"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    MESSAGE_SIZE = common_config["MESSAGE_SIZE"][message_size]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    data = get_data(MESSAGE_SIZE)

    start_time = time.time()
    actually_sent, message_count = 0, 0

    while actually_sent < MESSAGE_SIZE:
        to_send = min(BUFFER_SIZE, MESSAGE_SIZE - actually_sent)
        client_socket.send(data[actually_sent : actually_sent + to_send])
        actually_sent += to_send
        message_count += 1

        response = client_socket.recv(BUFFER_SIZE)

        while response != b"OK":
            client_socket.send(data[actually_sent - to_send : actually_sent])
            response = client_socket.recv(BUFFER_SIZE)
            message_count += 1

    end_time = time.time()
    print_report(
        "TCP - Streaming",
        message_count,
        actually_sent,
        end_time - start_time,
    )
    client_socket.close()


def TCP_Streaming(config, common_config, message_size):
    PORT = config["PORT"]
    HOST = common_config["HOST"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    MESSAGE_SIZE = common_config["MESSAGE_SIZE"][message_size]

    start_time, end_time = 0, 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    data = get_data(MESSAGE_SIZE)

    start_time = time.time()

    actually_sent, message_count = 0, 0

    while actually_sent < MESSAGE_SIZE:
        to_send = min(BUFFER_SIZE, MESSAGE_SIZE - actually_sent)
        client_socket.sendall(data[actually_sent : actually_sent + to_send])
        actually_sent += to_send
        message_count += 1

    end_time = time.time()
    print_report(
        "TCP - Streaming",
        message_count,
        actually_sent,
        end_time - start_time,
    )

    client_socket.close()


def UDP_Stop_and_Wait(config, common_config, message_size):
    PORT = config["PORT"]
    HOST = common_config["HOST"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    MESSAGE_SIZE = common_config["MESSAGE_SIZE"][message_size]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = get_data(MESSAGE_SIZE)

    start_time = time.time()

    actually_sent, message_count = 0, 0
    for i in range(0, MESSAGE_SIZE, BUFFER_SIZE):
        packet = data[i : i + BUFFER_SIZE]

        while True:
            client_socket.sendto(packet, (HOST, PORT))
            actually_sent += len(packet)
            message_count += 1
            response, _ = client_socket.recvfrom(BUFFER_SIZE)

            if response == b"OK":
                break
    client_socket.sendto(b"", (HOST, PORT))

    end_time = time.time()

    print_report(
        "UDP - Stop and Wait",
        message_count,
        actually_sent,
        end_time - start_time,
    )

    client_socket.close()


def UDP_Streaming(config, common_config, message_size):
    PORT = config["PORT"]
    HOST = common_config["HOST"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    MESSAGE_SIZE = common_config["MESSAGE_SIZE"][message_size]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = get_data(MESSAGE_SIZE)

    start_time = time.time()

    message_count, actually_sent = 0, 0

    while actually_sent < MESSAGE_SIZE:
        bytes_to_send = min(BUFFER_SIZE, MESSAGE_SIZE - actually_sent)
        client_socket.sendto(
            data[actually_sent : actually_sent + bytes_to_send], (HOST, PORT)
        )
        actually_sent += bytes_to_send
        message_count += 1
    client_socket.sendto(b"", (HOST, PORT))

    end_time = time.time()

    print_report("UDP - Streaming", message_count, actually_sent, end_time - start_time)

    client_socket.close()


def main():
    config, common_config, protocol, method, message_size = get_input()
    methods = get_methods_dictionary()

    methods[protocol][method](config[protocol][method], common_config, message_size)


if __name__ == "__main__":
    main()
