import RPi.GPIO as GPIO
import time

pin = 8

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

i = 0
while True:
    try:
        print(i, ": Off")
        GPIO.output(pin, True)
        time.sleep(5)
        print(i, ": On")
        GPIO.output(pin, False)
        time.sleep(5)
        i += 1
    except KeyboardInterrupt:
        print("")
        print("Clean up") 
        GPIO.cleanup()
        exit(0)
