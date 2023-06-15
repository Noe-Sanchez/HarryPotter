import socket
import time
import sys

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    id = "999"
    host = "192.168.12.1"
    port = 19000

    client.connect((host, port))

    magic = sys.argv[1]

    while True:
        try:
            data = client.recv(1024).decode("utf-8")
            client.sendall(magic.encode("utf-8"))

            print(data)
            if data == "":
                raise socket.error("Server disconnected")
            elif data in ["0", "1"]:
                id = data
            elif data == "end":
                data = client.recv(1024).decode("utf-8")
                if data == id:
                    print("You won!")
        except socket.error as e:
            print("Disconnected from server")
            client.close()
            while True:
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    client.connect((host, port))

                    print("Reconnected to server")
                    break
                except Exception as e:
                    time.sleep(5)
                    print("Trying to reconnect...")

if __name__ == '__main__':
    main()
