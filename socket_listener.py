import socket
import time

print("Creating server...")
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
time.sleep(1)
s.bind(('0.0.0.0', 11311))
s.listen(1)

try:
    while True:
        client, addr = s.accept()
        while True:
            content = client.recv(8)
            if len(content) == 0:
                break
            else:
                print(content)
        

except KeyboardInterrupt:
    print("Closing connection")
    client.close()
    s.close()
