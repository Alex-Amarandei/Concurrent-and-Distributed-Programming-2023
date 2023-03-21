import os


def delete_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)


def create_file(file_name, size):
    with open(file_name, "wb") as f:
        f.write(b"0" * size)


def main():
    file_name = input("File name: ")
    size = int(input("Size (in MB): "))

    delete_file(file_name)
    create_file(file_name, size)


if __name__ == "__main__":
    main()
