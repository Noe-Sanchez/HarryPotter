# has a thread to take a photo on a thread after 5 seconds
import cv2
import threading
import time
def take_photo(seconds):
    time.sleep(seconds)
    print("Taking photo")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cv2.imwrite("photo.jpg", frame)
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    photoThread  = threading.Thread(target=take_photo, args=(5,))
    photoThread.start()
    print("STARTING THREAD")
    for i in range(10):
        print("Executing photo take")
        time.sleep(1)
