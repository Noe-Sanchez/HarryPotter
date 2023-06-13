import socket
import asyncio
import time
#from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

clients = {}
data = {}

class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.id_counter = 0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Server started at", self.host, "on port", self.port)

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        while True:
            global clients
            client, incomming_address = self.server.accept()
            self.id_counter += 1
            #self.clients.append(client)
            #clients.append(client)
            clients.update({str(self.id_counter): client})
            data.update({str(self.id_counter): 0})
            #print(clients)
            print("New connection from: " + str(incomming_address))
            client.sendall(("ID: " + str(self.id_counter)).encode('utf-8'))
            time.sleep(0.2)

    def broadcast(self):
        while True:
            global clients
            #print("Broadcasting")
            #print(clients)
            for client_id, client in clients.copy().items():
                try:
                    client.sendall((str(data)).encode('utf-8'))
                    data[client_id] = client.recv(1024).decode('utf-8')
                except Exception as e:
                    try:
                        print("Client:", client_id, "disconnected")
                        client.close()
                        del clients[client_id]
                        del data[client_id]
                    except:
                        pass
            time.sleep(0.2)

if __name__ == '__main__':
    server = TCPServer("127.0.0.1", 19000)

    executor = ThreadPoolExecutor(10)
    loop = asyncio.new_event_loop()
    broadcast_thread = loop.run_in_executor(executor, server.broadcast)
    start_thread = loop.run_in_executor(executor, server.start)

    loop.run_forever()
