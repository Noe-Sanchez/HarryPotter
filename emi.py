# pyright: reportMissingImports=false
import sys
import cv2
import mediapipe as mp
import numpy as np
import time

debug = False
spell_cast = False

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
    print(interp, basis)
    return np.matmul(interp, np.matmul(basis, points))
                      
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(
static_image_mode=False,
max_num_hands=2,
min_detection_confidence=0.7)

current_tau = 0
current_segment = 1
cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, image = cap.read()
    height, width, _ = image.shape
    #current_spell_recipe = np.array([[0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75,0.75], [0.25,0.25]], dtype=np.half)
    current_spell_recipe = np.array([[0.75, 0.25], [0.75, 0.75], [0.75, 0.5], [0.25,0.5], [0.25,0.25], [0.25,0.75]], dtype=np.half)
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
            cv2.circle(image, (centerx, centery), 40,(255,180,130),3)
            cv2.circle(image, (centerx, centery), 3,(255,180,130),3)

            for point in current_spell_recipe:
                cv2.circle(image, (int(point[0]), int(point[1])), 3,(0,0,255),3)
            for i in range(1,current_segment):
                cv2.line(image, (int(current_spell_recipe[i][0]), int(current_spell_recipe[i][1])), (int(current_spell_recipe[i+1][0]), int(current_spell_recipe[i+1][1])), (255,180,130), 3)
            if spell_cast:
                cv2.line(image, (int(current_spell_recipe[current_segment][0]), int(current_spell_recipe[current_segment][1])), (int(current_spell_recipe[current_segment+1][0]), int(current_spell_recipe[current_segment+1][1])), (255,180,130), 3)

            #if current_segment == 0:
            #    next_point = np.array([2*current_spell_recipe[current_segment]-current_spell_recipe[current_segment+1],
            #                             current_spell_recipe[current_segment],
            #                             current_spell_recipe[current_segment+1],
            #                             current_spell_recipe[current_segment+2]],
            #                             dtype=np.half)
            #    print("First alg: reflect begin ", current_segment,current_segment+1,current_segment+2)
            #elif current_segment == len(current_spell_recipe)-3:
            #    next_point = np.array([current_spell_recipe[current_segment],
            #                           current_spell_recipe[current_segment+1],
            #                           current_spell_recipe[current_segment+2],
            #                         2*current_spell_recipe[current_segment]-current_spell_recipe[current_segment-1]],
            #                           dtype=np.half)
            #    print("Third alg:", current_segment, current_segment+1, current_segment+2, "reflect end")
            #else:
            #print(current_spell_recipe)
            next_point = np.array([current_spell_recipe[current_segment-1],
                                   current_spell_recipe[current_segment],
                                   current_spell_recipe[current_segment+1],
                                   current_spell_recipe[current_segment+2]],
                                   dtype=np.half)
            #print(next_point)
#    print("Second alg:", current_segment-1, current_segment,current_segment+1,current_segment+2)
            #print("Current segment", current_segment, " Total segments", len(current_spell_recipe)-1)    
            next_point = evaluate(next_point, current_tau).astype(int)
            cv2.circle(image, (next_point[0], next_point[1]), 3,(255,180,130),3)
            print(next_point)

            if spell_cast == False:
                if abs(np.linalg.norm(np.array([centerx,centery])-next_point)) < 40:
                    #current_tau += 0.25
                    current_tau += 0.05
                    if current_tau > 1:
                        if current_segment == len(current_spell_recipe)-3:
                            print("Spell cast!")
                            spell_cast = True
                            #current_segment = 1
                            #current_tau = 0
                        else:
                            current_segment += 1
                            current_tau = 0

    cv2.imshow('Harry Potter', cv2.flip(image, 1))
    cv2.waitKey(1)
    if cv2.waitKey(25) & 0xFF == ord('c'):
        break
cap.release()
cv2.destroyAllWindows()
