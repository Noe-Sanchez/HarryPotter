import serial
import threading
import time

def read_Serial():
    global serialThreadEnabled
    global serialValue
    device =  "/dev/ttyUSB0"
    baud_rate = 115200
    ser = None
    while ((ser is None) and serialThreadEnabled):
        try:
            ser = serial.Serial(device, baud_rate, timeout=5)
        except:
            ser = None
            print("Waiting for connection...")
            time.sleep(1)
    
    while serialThreadEnabled:
        line = None
        line = ser.readline().decode('utf-8').rstrip()
        print(f"Read {line}")
        
        if (line is not None and (line in ["0", "1", "2"])):
            print("Updated")
            value = int(line)
            serialValue = value
    ser.close()
    print("Thread closed")

if __name__ == "__main__":
    value = 0
    serialValue = 0
    serialThread = threading.Thread(target=read_Serial)
    serialThreadEnabled = True
    serialThread.start()
    try:
        while True:
            print(f"Executing game, value = {serialValue}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing thread")
        serialThreadEnabled = False
        print("Thread closed")