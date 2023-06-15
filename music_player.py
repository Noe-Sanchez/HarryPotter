import pygame
import threading
import time

def play_sound(sound):
    global play_sounds
    pygame.mixer.init()

    while play_sounds:
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and play_sounds:
            continue
    print("Thread closed")

if __name__ == "__main__":
    sound = "music1.mp3"
    soundThread  = threading.Thread(target=play_sound, args=(sound,))
    play_sounds = True
    soundThread.start()
    print("STARTING THREAD")
    try:
        while True:
            print("Executing game")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing thread")
        play_sounds = False
        print("Thread closed")
