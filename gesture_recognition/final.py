import mediapipe as mp
import cv2
import numpy as np
import uuid
import os
import time
import motion

drone=motion.init_drone()
class handDetector():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
 
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
 
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS,
                                               self.mpDraw.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                               self.mpDraw.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)
                                              )
        return img
    
    def findPosition(self, img, handNo=0, draw=True):
 
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
 
        return lmList
def point_inside_polygon(x,y,poly):

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
def GetFingerInfo(lmList):
    yo = [1, 1, 0, 0, 1]
    tipIds = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # 4 Fingers
    for id in range(1, 5):
        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    totalFingers = fingers.count(1)

    if fingers == yo:
        totalFingers = 6
    
    return totalFingers




def counter_detetion():
    cap = cv2.VideoCapture(0) 
    detector = handDetector(detectionCon=0.75)

    command = {1:"Stay",2:"Left",3:"Right",4:"Up",5:"Down",6:"Forward",7:"Back"} #command Mapping
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if len(lmList) != 0:
            totalFingers = GetFingerInfo(lmList)
            ##############################################
            # "totalFingers" Total finger variable ka use karna hai drone manoeuvre
            ##############################################
            cv2.rectangle(img, (40, 310), (100, 385), (121, 22, 76), cv2.FILLED)
            cv2.putText(img, command[totalFingers + 1], (45, 375), cv2.FONT_HERSHEY_PLAIN,
                        5, (250, 44, 250), 5)
        cv2.imshow("Image", img)

    cap.release()
    cv2.destroyAllWindows()



def range_detection():
    cap = cv2.VideoCapture(0) 
    detector = handDetector(detectionCon=0.75)
    h_limit = 100
    w_limit = 180
    h_full = 479
    w_full = 639
    quad = [[(0,0),(w_limit,h_limit),(w_limit,h_full - h_limit),(0,h_full)],#left
            [(w_full - w_limit,h_limit),(w_full,0),(w_full,h_full),(w_full - w_limit,h_full - h_limit)],#right
            [(0,0),(w_full,0),(w_full - w_limit,h_limit),(w_limit,h_limit)],#up
            [(0,h_full),(w_limit,h_full - h_limit),(w_full - w_limit,h_full - h_limit),(w_full,h_full)],#down
            [(w_limit,h_limit),(w_full - w_limit,h_limit),(w_full - w_limit,h_full - h_limit),(w_limit,h_full - h_limit)]]#centre
    pos = ["Right","Left","Up","Down","Centre"]
    tipIds = [4, 8, 12, 16, 20]
    command = {"Stay":1,"Left":2,"Right":3,"Up":4,"Down":5,"Forward":6,"Back":7} #command Mapping
    yo = [1, 1, 0, 0, 1]
    while True:
        move = ""
        success, img = cap.read()

        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)


        cv2.rectangle(img, (w_limit, h_limit), (w_full - w_limit, h_full - h_limit), (250, 44, 250))
        cv2.line(img,(0,0),(w_limit, h_limit),(250, 44, 250))
        cv2.line(img,(w_full - w_limit, h_full - h_limit),(w_full,h_full),(250, 44, 250))
        cv2.line(img,(w_full - w_limit, h_limit),(w_full,0),(250, 44, 250))
        cv2.line(img,(w_limit, h_full - h_limit),(0,h_full),(250, 44, 250))
        img = cv2.flip(img, 1)
        if lmList:
            for i in range(5):
                if point_inside_polygon(lmList[9][1],lmList[9][2],quad[i]) and point_inside_polygon(lmList[13][1],lmList[13][2],quad[i]) :
                    move = pos[i]
                    break
            totalFingers = GetFingerInfo(lmList)
            if totalFingers == 0:
                move = "Stay"
            if move == "Centre":
                move = "Stay"
                if totalFingers == 5:
                    move = "Forward"
                if totalFingers == 6:
                    move = "Back"
                    
            cv2.rectangle(img, (40, 310), (100, 385), (121, 22, 76), cv2.FILLED)
            if move!="":
                cv2.putText(img, str(move), (45, 375), cv2.FONT_HERSHEY_PLAIN,
                            5, (250, 44, 250), 5)
                totalFingers = command[move]
                if totalFingers==2:
                    drone.leftward()
                elif totalFingers==3:
                    drone.rightward()
                elif totalFingers==4:
                    drone.up()
                elif totalFingers==5:
                    drone.down()
                elif totalFingers==6:
                    drone.forward()
                elif totalFingers==7:
                    drone.backward()


                ##############################################
                # "totalFingers" Total finger variable ka use karna hai drone manoeuvre
                ##############################################
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cv2.imshow("Image", img)

    cap.release()
    cv2.destroyAllWindows()



range_detection()
# drone=motion.init_drone()


# cap = cv2.VideoCapture(0) 
# detector = handDetector(detectionCon=0.75)
 
# tipIds = [4, 8, 12, 16, 20]
# command = ["Stay","Left","Right","Up","Down","Forward","Back"]
# yo = [1, 1, 0, 0, 1]
# while True:
#     success, img = cap.read()
#     img = detector.findHands(img)
#     lmList = detector.findPosition(img, draw=False)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

#     if len(lmList) != 0:
#         fingers = []

#         # Thumb
#         if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
#             fingers.append(1)
#         else:
#             fingers.append(0)

#         # 4 Fingers
#         for id in range(1, 5):
#             if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
#                 fingers.append(1)
#             else:
#                 fingers.append(0)
#         totalFingers = fingers.count(1)

#         if fingers == yo:
#             totalFingers = 7
            
#         cv2.rectangle(img, (40, 310), (100, 385), (121, 22, 76), cv2.FILLED)
#         cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN,
#                     5, (250, 44, 250), 5)
#         if totalFingers==1:
#             drone.leftward()
#         elif totalFingers==2:
#             drone.rightward()
#         elif totalFingers==3:
#             drone.up()
#         elif totalFingers==4:
#             drone.down()
#         elif totalFingers==5:
#             drone.forward()
#         elif totalFingers==6:
#             drone.backward()
#         elif totalFingers==0:
#             drone.anticlockwise()
#         elif totalFingers==7:
#             drone.clockwise()

#     cv2.imshow("Image", img)
    
# cap.release()
# cv2.destroyAllWindows()