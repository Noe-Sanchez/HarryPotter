import socket
import time
import sys
import cv2
import mediapipe as mp
import numpy as np
import threading

debug = False
spell_cast = False
useServer = True
useESP = True

spell_index_to_type = {
    0 : "fire",
    1 : "water",
    2 : "earth"
}

if len(sys.argv) > 1:
    player = True if sys.argv[1].lower() == "--debug" else False
    debug = True if sys.argv[2].lower() == "--debug" else False
else:
    print("Usage: python3 emi.py <player> [--debug]")

def get_joint_xy(hand_landmark, joint):
    return [hand_landmark.landmark[joint].x, hand_landmark.landmark[joint].y]

def evaluate(points, tau):
    interp = np.array([1, tau, tau**2, tau**3], dtype=np.half)
    basis = np.array([[0, 1, 0, 0],[-0.5, 0, 0.5, 0],[1, -2.5, 2, -0.5],[-0.5, 1.5, -1.5, 0.5]], dtype=np.half)
    #print(interp, basis)
    return np.matmul(interp, np.matmul(basis, points))

class full_game_client():

    # fire, water, earth, BGR
    dotColors = {
        0 : (0, 0, 150),
        1 : (200, 0, 0),
        2 : (40, 80, 120)
    }

    lineColors = {
        0 : (0,0,255),
        1 : (230, 200, 0),
        3 : (20, 120, 230)
    }

    def __init__(self):
        print("Initializing")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if (useServer):
            self.host = '127.0.0.1'
            self.port = 19000
            self.client.connect((self.host, self.port))
            # client thread
            self.clientThreadEnabled = True
            self.clientThread = threading.Thread(target=self.client_listener)
            self.clientThread.start()
        self.clientData = None
        self.nodeData = 0
        if (useESP):
            self.nodeServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.nodeServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.esp_host = '0.0.0.0'
            self.esp_port = 11311
            self.nodeServer.bind((self.esp_host, self.esp_port))
            self.nodeServer.listen(1)
            self.nodeThreadEnabled = True
            self.nodeThread = threading.Thread(target=self.esp_listener)
            self.nodeThread.start()

        #mediapipe settings
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7)

        # Game variables
        self.spell_list = [[[0.20625, 0.8645833333333334], [0.0890625, 0.5708333333333333], [0.30625, 0.1], [0.6484375, 0.1125], [0.8546875, 0.46041666666666664], [0.49375, 0.8479166666666667], [0.3171875, 0.3145833333333333]], [[0.084375, 0.5833333333333334], [0.3, 0.22083333333333333], [0.553125, 0.32083333333333336], [0.69375, 0.8125], [0.7828125, 0.46458333333333335], [0.6015625, 0.2125], [0.4328125, 0.21875]], [[0.8390625, 0.36875], [0.596875, 0.1625], [0.1765625, 0.21875], [0.028125, 0.8666666666666667], [0.4875, 0.8083333333333333], [0.753125, 0.8416666666666667], [0.825, 0.60625]]]
        self.current_spell_index = 0
        self.current_tau = 0
        self.current_segment = 1

    def esp_listener(self):
        while self.nodeThreadEnabled:
            client, addr = self.nodeServer.accept()
            while self.nodeThreadEnabled:
                client.settimeout(5)
                self.nodeData = client.recv(8)
                if len(self.nodeData) == 0:
                    break
                else:
                    print(f"Received: {self.nodeData}")
                    if (self.nodeData == b'1'):
                        self.current_spell_index += 1
                        self.current_tau = 0
                        self.current_segment = 1
                        if (self.current_spell_index >= len(self.spell_list)):
                            self.current_spell_index = 0
                        while (self.nodeData == b'1'):
                            self.nodeData = client.recv(8)
        print("Closed ESP client")
        client.close()
            
    
    def client_listener(self):
        while self.clientThreadEnabled:
            self.clientData = self.client.recv(1024).decode("utf-8")
        #close client
        self.client.close()
        print("Closed game client")
    
    def run(self):
        print("Running")
        while True:
            global spell_cast
            try:
                
                mp_hands = mp.solutions.hands
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing_styles = mp.solutions.drawing_styles
                hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7)

                cap = cv2.VideoCapture(0)
                while cap.isOpened():
                    success, image = cap.read()
                    height, width, _ = image.shape
                    current_spell_recipe = np.array(self.spell_list[self.current_spell_index], dtype=np.half)
                    current_spell_recipe = np.vstack([2*current_spell_recipe[0]-current_spell_recipe[1], current_spell_recipe, 2*current_spell_recipe[0]-current_spell_recipe[1]])
                    current_spell_recipe = np.array([width, height])*current_spell_recipe
                    if not success:
                        print("Ignoring empty camera frame.")
                        continue
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = hands.process(image)
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            if debug:
                                mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())

                            x1, y1 = np.multiply(get_joint_xy(hand_landmarks, mp_hands.HandLandmark.INDEX_FINGER_MCP), [width, height]).astype(int)
                            x2, y2 = np.multiply(get_joint_xy(hand_landmarks, mp_hands.HandLandmark.RING_FINGER_MCP), [width, height]).astype(int)
                            x3, y3 = np.multiply(get_joint_xy(hand_landmarks, mp_hands.HandLandmark.WRIST), [width, height]).astype(int)

                            centerx, centery = [int(sum([x1,x2,x3])/3) , int(sum([y1,y2,y3])/3)]
                            cv2.circle(image, (centerx, centery), 40,self.lineColors[self.current_spell_index],3)
                            cv2.circle(image, (centerx, centery), 3,self.lineColors[self.current_spell_index],3)

                            for point in current_spell_recipe:
                                cv2.circle(image, (int(point[0]), int(point[1])), 3,self.dotColors[self.current_spell_index],3)
                            for i in range(1,self.current_segment):
                                cv2.line(image, (int(current_spell_recipe[i][0]), int(current_spell_recipe[i][1])), (int(current_spell_recipe[i+1][0]), int(current_spell_recipe[i+1][1])), self.lineColors[self.current_spell_index], 3)
                            if spell_cast:
                                cv2.line(image, (int(current_spell_recipe[self.current_segment][0]), int(current_spell_recipe[self.current_segment][1])), (int(current_spell_recipe[self.current_segment+1][0]), int(current_spell_recipe[self.current_segment+1][1])), self.lineColors[self.current_spell_index], 3)

                            next_point = np.array([current_spell_recipe[self.current_segment-1],
                                                current_spell_recipe[self.current_segment],
                                                current_spell_recipe[self.current_segment+1],
                                                current_spell_recipe[self.current_segment+2]],
                                                dtype=np.half)
                            next_point = evaluate(next_point, self.current_tau).astype(int)
                            cv2.circle(image, (next_point[0], next_point[1]), 3,self.lineColors[self.current_spell_index],3)
                            #print(next_point)

                            if spell_cast == False:
                                if abs(np.linalg.norm(np.array([centerx,centery])-next_point)) < 40:
                                    self.current_tau += 0.05
                                    if self.current_tau > 1:
                                        if self.current_segment == len(current_spell_recipe)-3:
                                            print("Spell cast!")
                                            spell_cast = True
                                            #self.current_segment = 1
        #self.current_tau = 0
                                        else:
                                            self.current_segment += 1

                                            self.current_tau = 0
                    print(self.clientData)
                    if self.clientData == "reset":
                        spell_cast = False
                        self.current_segment = 1
                        self.current_tau = 0
                        self.clientData = ""
                    if spell_cast == True:
                        if (useServer):
                            self.client.sendall("cast#fire".encode("utf-8"))
                            self.clientData = self.client.recv(1024).decode("utf-8")
                        else:
                            print("Spell Cast")
                        self.clientData = "reset"
                    else:
                        if (useServer):
                            self.client.sendall("nadota pa".encode("utf-8"))

                    cv2.imshow('Harry Potter', cv2.flip(image, 1))
                    cv2.waitKey(1)
                    if cv2.waitKey(25) & 0xFF == ord('c'):
                        break
                cap.release()
                cv2.destroyAllWindows()

                print(self.clientData)
                if self.clientData == "":
                    raise socket.error("Server disconnected")
            except socket.error as e:
                print("Disconnected from server")
                self.client.close()
                while True:
                    try:
                        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.client.connect((self.host, self.port))

                        print("Reconnected to server")
                        break
                    except Exception as e:
                        time.sleep(5)
                        print("Trying to reconnect...")
            except Exception as e:
                print(e)
            
            except KeyboardInterrupt as e:
                #close sockets
                self.clientThreadEnabled = False
                self.nodeThreadEnabled = False


        
if __name__ == '__main__':
    full_game_client().run()