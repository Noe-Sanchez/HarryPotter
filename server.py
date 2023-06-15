import socket
import asyncio
import time
#from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

clients = {}
casts = {}
life = {}
turn_end = False
turn_duration = 5

class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.id_counter = 0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.startGame = False
        print("Server started at", self.host, "on port", self.port)

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        while True:
            global clients
            global casts
            global life
            global turn_end
            if len(clients) < 2:
                client, incomming_address = self.server.accept()
                self.id_counter += 1
                clients.update({str(self.id_counter % 2): client})
                casts.update({str(self.id_counter % 2): ""})
                life.update({str(self.id_counter % 2): 100})
                print("New connection from: " + str(incomming_address))
                client.sendall(("ID: " + str(self.id_counter)).encode('utf-8'))
                time.sleep(0.2)
            else:
                print("Starting game...")
                self.startGame = True
                break

    def transceiver(self):
        while not self.startGame:
            pass
        while self.startGame:
            global clients
            global casts
            global turn_end
            for client_id, client in clients.copy().items():
                try:
                    if life["0"] <= 0 or life["1"] <= 0:
                        print("Game ended")
                        client.sendall("end".encode('utf-8'))
                        print("Sleeping...")
                        self.startGame = False
                        time.sleep(20)
                        # send 0 to database
                        print("Turning rasp off...")
                    if turn_end:
                        print("Turn ended hit")
                        client.sendall("reset".encode('utf-8'))
                        casts["0"] = ""
                        casts["1"] = ""
                        for client_id, client in clients.copy().items():
                            client.sendall("reset".encode('utf-8'))
                        turn_end = False
                    else:
                        client.sendall(str(life).encode('utf-8'))
                    incomming = client.recv(1024).decode('utf-8')
                    #print("Client:", client_id, "sent:", incomming)
                    for cast in casts:
                        #print(f"Current {cast} spell is {casts[cast]}")
                        pass
                    if "cast" in incomming:
                        casts[client_id] = incomming.split("#")[1]
                        #print("Client:", client_id, "casted spell:", casts[client_id])
                    
                except Exception as e:
                    try:
                        print(e)
                        print("Client:", client_id, "disconnected")
                        client.close()
                        del clients[client_id]
                        del casts[client_id]
                    except:
                        pass
            #if turn_end:
             #   turn_end = False
            time.sleep(0.01)

    def game(self):
        while not self.startGame:
            pass
        while self.startGame:
            global casts
            global life
            global turn_end
            print("Game started")
            prevtime = time.time()
            while (time.time() - prevtime) < turn_duration:
                #each second passed print remaining time
                print("Remaining time:", turn_duration - (time.time() - prevtime))
                time.sleep(1)
                pass
            
            print("Evaluating...")
            try:
                if casts["0"] == "fire" and casts["1"] == "water":
                    life["0"] -= 25
                elif casts["0"] == "water" and casts["1"] == "fire":
                    life["1"] -= 25
                elif casts["0"] == "fire" and casts["1"] == "earth":
                    life["1"] -= 25
                elif casts["0"] == "earth" and casts["1"] == "fire":
                    life["0"] -= 25
                elif casts["0"] == "water" and casts["1"] == "earth":
                    life["0"] -= 25
                elif casts["0"] == "earth" and casts["1"] == "water":
                    life["1"] -= 25
                elif casts["0"] == "" and casts["1"]!="":
                    life["0"] -= 25
                elif casts["0"] != "" and casts["1"]=="":
                    life["1"] -= 25
                print("Wizard 0 life:", life["0"])    
                print("Wizard 1 life:", life["1"])
                turn_end = True
                casts["0"] = ""
                casts["1"] = ""
                time.sleep(0.5)
            except Exception as e:
                turn_end = True
                print(e)
                pass


if __name__ == '__main__':
    server = TCPServer("192.168.137.245", 19000)

    executor = ThreadPoolExecutor(10)
    loop = asyncio.new_event_loop()
    transceiver_thread = loop.run_in_executor(executor, server.transceiver)
    game_thread = loop.run_in_executor(executor, server.game)
    start_thread = loop.run_in_executor(executor, server.start)

    loop.run_forever()
