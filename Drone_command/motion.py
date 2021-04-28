
import numpy as np
import time
import cv2
import math

try:
    import sim
except:
    print('--------------------------------------------------------------')
    print('"sim.py" could not be imported. This means very probably that')
    print('either "sim.py" or the remoteApi library could not be found.')
    print('Make sure both are in the same folder as this file,')
    print('or appropriately adjust the file "sim.py"')
    print('--------------------------------------------------------------')
    print('')


class init_drone():
    def __init__(self):

        print('Program started')
        sim.simxFinish(-1)  # just in case, close all opened connections
        self.clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)  # Connect to CoppeliaSim
        if self.clientID != -1:
            print('Connected to remote API server')

            return_code, self.handle = sim.simxGetObjectHandle(self.clientID, 'Quadricopter_target', sim.simx_opmode_blocking)
            return_code, self.handle_cam_front = sim.simxGetObjectHandle(self.clientID, 'Vision_sensor',
                                                               sim.simx_opmode_oneshot_wait)
            self.err, self.resolution, self.image = sim.simxGetVisionSensorImage(self.clientID, self.handle_cam_front, 0, sim.simx_opmode_streaming)



            return_code, self.current_ori= sim.simxGetObjectOrientation(self.clientID, self.handle, -1, sim.simx_opmode_oneshot_wait)

            return_code,self.current_pos=sim.simxGetObjectPosition(self.clientID, self.handle, -1, sim.simx_opmode_oneshot_wait)




            time.sleep(1)
        else:
            print('Failed connecting to remote API server')
            print('Program ended')
    def move_to(self,target_pos,steps):
        d_target = list((np.array(target_pos) - np.array(self.current_pos)) / steps);
        for i in range( steps):
            self.current_pos = list(np.array(self.current_pos) + np.array(d_target))

            return_code = sim.simxSetObjectPosition(self.clientID, self.handle, -1,
                                                    [self.current_pos[0], self.current_pos[1], self.current_pos[2]],
                                                     sim.simx_opmode_blocking)

        return_code, ori = sim.simxGetObjectOrientation(self.clientID, self.handle, -1, sim.simx_opmode_oneshot_wait)
        print(ori)


    def ori_change(self,target_ori,steps):
        d_target = list((np.array(target_ori) - np.array(self.current_ori)) / steps)
        for i in range( steps):
            self.current_ori = list(np.array(self.current_ori) + np.array(d_target))

            return_code = sim.simxSetObjectOrientation(self.clientID, self.handle, -1,
                                                    [self.current_ori[0], self.current_ori[1], self.current_ori[2]],
                                                    sim.simx_opmode_blocking)

        return_code, self.current_ori = sim.simxGetObjectOrientation(self.clientID, self.handle, -1,
                                                                     sim.simx_opmode_oneshot_wait)
        print(self.current_ori)

    def get_feed(self,cam_no):


        if(cam_no==1):
            err, self.resolution, self.image = sim.simxGetVisionSensorImage(self.clientID,self.handle_cam_front,0,sim.simx_opmode_buffer)
            if err == sim.simx_return_ok:
                    print("image OK!!!")
                    img = np.array(self.image,dtype=np.uint8)
                    img.resize([self.resolution[1],self.resolution[0],3])
                    return img

            elif err == sim.simx_return_novalue_flag:
                print("no image yet")
                pass
            else:
                print(err)


    def forward(self):

        self.move_to([self.current_pos[0]+0.035*math.cos(self.current_ori[2]),self.current_pos[1]+0.035*math.sin(self.current_ori[2]),self.current_pos[2]],1)

    def backward(self):

        self.move_to([self.current_pos[0] - 0.1 * math.cos(self.current_ori[2]),
                      self.current_pos[1] - 0.1 * math.sin(self.current_ori[2]), self.current_pos[2]], 1)

    def leftward(self):
        self.move_to([self.current_pos[0] - 0.1 * math.sin(self.current_ori[2]),
                      self.current_pos[1] - 0.1 * math.cos(self.current_ori[2]), self.current_pos[2]], 1)

    def rightward(self):
        self.move_to([self.current_pos[0] + 0.1 * math.sin(self.current_ori[2]),
                      self.current_pos[1] + 0.1 * math.cos(self.current_ori[2]), self.current_pos[2]], 1)

    def clockwise(self):
        self.current_ori[2]=self.current_ori[2]-0.05
        self.ori_change(self.current_ori,1)

    def anticlockwise(self):
        self.current_ori[2]=self.current_ori[2]+0.05
        self.ori_change(self.current_ori,1)

    def up(self):
        self.current_pos[2]=self.current_pos[2]+0.02
        self.move_to(self.current_pos,1)

    def down(self):
        self.current_pos[2]=self.current_pos[2]-0.02
        self.move_to(self.current_pos,1)

# drone=init_drone()

# i=0

# while (1):

#     i=i+0.05
#     image=drone.get_feed(1)
#     image2=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

#     mask=cv2.inRange(image,(0,0,0),(82,255,255))
#     res=cv2.bitwise_and(image,image,mask=mask)

#     res=cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)

#     ret,thresh=cv2.threshold(res,100,255,cv2.THRESH_BINARY)
#     contours,hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#     cv2.drawContours(image, contours, -1, (0, 255, 0),3)
#     cv2.imshow('final',image)
#     cnt=contours[0]
#     M=cv2.moments(cnt)
#     cx=128
#     cy=128
#     if( M['m00']):
#         cx = int(M['m10'] / M['m00'])
#         cy = int(M['m01'] / M['m00'])
#     print(cx,cy)

#     #

#     if(100<cx<155):
#         drone.forward()
#     elif(cx<100):
#         drone.clockwise()
#     elif(cx>155):
#         drone.anticlockwise()






#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break








# cv2.destroyAllWindows()