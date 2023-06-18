# turns on a buzzer with PWM, a relay for AC, has continous music reproduction and takes a photo
import serial
import threading
import time
import pygame
import sys
import RPi.GPIO as GPIO
import os
import cv2

def play_sound(sound):
    global play_sounds
    pygame.mixer.init()

    while play_sounds:
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and play_sounds:
            continue
    print("Thread closed")

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

def take_photo_after(seconds, file):
    time.sleep(seconds)
    print("Taking photo")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cv2.imwrite(file, frame)
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    folder = "photos"
    file = "photo"
    if not os.path.exists(folder):
        os.mkdir(folder)
    value = 0
    serialValue = 0
    serialThread = threading.Thread(target=read_Serial)
    serialThreadEnabled = True
    sound = "music1.mp3"
    soundThread  = threading.Thread(target=play_sound, args=(sound,))
    play_sounds = True
    soundThread.start()
    serialThread.start()

    buzzerpin = 3
    ACpin = 7

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ACpin, GPIO.OUT)
    GPIO.setup(buzzerpin, GPIO.OUT)
    buzzer = GPIO.PWM(buzzerpin, 1000)

    photoTaken = False
    try:
        while True:
            print(f"Executing game, value = {serialValue}")
            if serialValue == 1:
                # player 1 won
                GPIO.output(ACpin, True)
                buzzer.start(100)
                time.sleep(0.1)
                buzzer.stop()
                time.sleep(0.1)
                if not photoTaken:
                    photoTaken = True
                    file_count = len(os.listdir(folder))
                    filename = f"{folder}/{file}_{file_count}.jpg"
                    photoThread = threading.Thread(target=take_photo_after, args=(5,filename,))
                    photoThread.start()

            elif serialValue == 2:
                # player 2 won
                GPIO.output(ACpin, True)
                buzzer.start(50)
                time.sleep(0.05)
                buzzer.stop()
                time.sleep(0.05)
                if not photoTaken:
                    photoTaken = True
                    file_count = len(os.listdir(folder))
                    filename = f"{folder}/{file}_{file_count}.jpg"
                    photoThread = threading.Thread(target=take_photo_after, args=(10,filename,))
                    photoThread.start()
            else:
                buzzer.stop()
                GPIO.output(ACpin, False)
                time.sleep(0.5)
                photoTaken = False

    except KeyboardInterrupt:
        print("Closing thread")
        serialThreadEnabled = False
        print("Clean up") 
        buzzer.stop()
        GPIO.output(ACpin, False)
        GPIO.cleanup()
        print("Thread closed")
        exit(0)