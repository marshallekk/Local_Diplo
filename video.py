import cv2
import os

def toFrames(video_path):

    vidcap = cv2.VideoCapture(video_path)
    success,image = vidcap.read()
    count = 0
    zeros = "00000"
    while success:
        print("%s%d.jpg" % (zeros,count))
        path ="C:\\Users\\hrebe\\source\\repos\\NewRepo\\Frames\\nosferatu\\%s%d.jpg" % (zeros,count)     
        cv2.imwrite(path, image)     # save frame as JPEG file      
        success,image = vidcap.read()
        #print('Read a new frame: ', success)
        count += 1
        if (count // 10 != 0):
            zeros = "0000"
        if (count // 100 != 0):
            zeros = "000"
        if (count // 1000 != 0):
            zeros = "00"
        if (count // 10000 != 0):
            zeros = "0"
        

toFrames("C:\\Users\\hrebe\\source\\repos\\NewRepo\\nosferatu.mp4")