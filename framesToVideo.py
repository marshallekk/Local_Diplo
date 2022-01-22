import cv2
import numpy as np
import glob

def to_video(video_path):
    img_array = []
    for filename in glob.glob('C:\\Users\\hrebe\\source\\repos\\NewRepo\\Col_Frames\\*.jpg'):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)


    out = cv2.VideoWriter(video_path,cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
 
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

to_video("C:\\Users\\hrebe\\source\\repos\\NewRepo\\nosferatu.avi")
