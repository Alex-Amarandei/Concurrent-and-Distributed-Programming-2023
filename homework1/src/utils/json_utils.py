import json


def read_json_file(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
    return data


def main():
    file_name = input("File name: ")

    dictionary = read_json_file(file_name)
    print(dictionary)

    return dictionary


if __name__ == "__main__":
    main()
