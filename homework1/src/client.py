import socket
import time
from utils.json_utils import read_json_file


def get_data():
    with open("data/data.txt", "r") as f:
        data = f.read()

        return data.encode("utf-8")


def get_input():
    config = read_json_file("data/config.json")
    common_config = read_json_file("data/common_config.json")

    protocol = input("Choose a protocol (TCP or UDP): ")
    method = input("Choose a method (Stop and Wait or Streaming): ")
    message_size = input(
        "The size of your message (1MB, 10MB, 50MB, 100MB, 500MB, 1GB): "
    )

    return config, common_config, protocol, method, message_size


def get_methods_dictionary():
    methods = {
        "TCP": {"Stop and Wait": TCP_Stop_and_Wait, "Streaming": TCP_Streaming},
        "UDP": {"Stop and Wait": UDP_Stop_and_Wait, "Streaming": UDP_Streaming},
    }

    return methods


def print_report(response, protocol, number, bytes_sent, time_elapsed):
    if len(response) > 0:
        print(f"Decoded response: {response}\n")

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

    start_time, end_time = 0, 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    client_socket.send(MESSAGE_SIZE.to_bytes(8, byteorder="big"))

    data = get_data()

    start_time = time.time()

    sent_bytes, number_of_messages = 0, 0

    try:
        while sent_bytes < MESSAGE_SIZE:
            bytes_to_send = min(BUFFER_SIZE, MESSAGE_SIZE - sent_bytes)
            client_socket.send(data[sent_bytes : sent_bytes + bytes_to_send])
            sent_bytes += bytes_to_send
            number_of_messages += 1

            response = client_socket.recv(BUFFER_SIZE)

            while response != b"OK":
                client_socket.send(data[sent_bytes - bytes_to_send : sent_bytes])
                response = client_socket.recv(BUFFER_SIZE)
    except ConnectionResetError:
        pass
    finally:
        end_time = time.time()

        print_report(
            "",
            "TCP - Stop and Wait",
            number_of_messages,
            sent_bytes,
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

    client_socket.send(MESSAGE_SIZE.to_bytes(8, byteorder="big"))

    data = get_data()

    start_time = time.time()

    total_sent_bytes, sent_bytes, number_of_messages = 0, 0, 0

    while total_sent_bytes < MESSAGE_SIZE:
        bytes_to_send = min(BUFFER_SIZE, MESSAGE_SIZE - total_sent_bytes)
        sent_bytes = client_socket.send(data[sent_bytes : sent_bytes + bytes_to_send])
        total_sent_bytes += sent_bytes
        number_of_messages += 1

    response = client_socket.recv(BUFFER_SIZE)
    end_time = time.time()

    print_report(
        response.decode(),
        "TCP - Streaming",
        number_of_messages,
        total_sent_bytes,
        end_time - start_time,
    )

    client_socket.close()


def UDP_Stop_and_Wait(config, common_config, message_size):
    PORT = config["PORT"]
    HOST = common_config["HOST"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    MESSAGE_SIZE = common_config["MESSAGE_SIZE"][message_size]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = get_data()

    start_time = time.time()

    total_sent_bytes, sent_bytes, number_of_messages = 0, 0, 0

    for i in range(0, MESSAGE_SIZE, BUFFER_SIZE):
        packet = data[i : i + BUFFER_SIZE]

        while True:
            sent_bytes = client_socket.sendto(packet, (HOST, PORT))
            total_sent_bytes += sent_bytes
            number_of_messages += 1
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            if response == b"ACK":
                break

    end_time = time.time()

    client_socket.sendto(b"done", (HOST, PORT))

    print_report(
        "",
        "UDP - Stop and Wait",
        number_of_messages,
        total_sent_bytes,
        end_time - start_time,
    )

    client_socket.close()


def UDP_Streaming(config, common_config, message_size):
    PORT = config["PORT"]
    HOST = common_config["HOST"]
    BUFFER_SIZE = config["BUFFER_SIZE"]
    MESSAGE_SIZE = common_config["MESSAGE_SIZE"][message_size]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = get_data()

    start_time = time.time()

    number_of_messages, total_sent_bytes, sent_bytes = 0, 0, 0

    for i in range(0, MESSAGE_SIZE, BUFFER_SIZE):
        packet = data[i : i + BUFFER_SIZE]
        sent_bytes = client_socket.sendto(packet, (HOST, PORT))
        number_of_messages += 1
        total_sent_bytes += sent_bytes

    end_time = time.time()

    client_socket.sendto(b"done", (HOST, PORT))

    print_report(
        "",
        "UDP - Streaming",
        number_of_messages,
        total_sent_bytes,
        end_time - start_time,
    )

    client_socket.close()


def main():
    config, common_config, protocol, method, message_size = get_input()
    methods = get_methods_dictionary()

    methods[protocol][method](config[protocol][method], common_config, message_size)


if __name__ == "__main__":
    main()
