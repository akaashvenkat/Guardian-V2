#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 15:01:34 2020

@author: audi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detecting lasers: Red circles with inner white fillings
#ADDED LINE FOR TEST
@author: audi
"""
from PIL import Image as im
import numpy as np
import cv2
import sys
import time
import signal
import statistics as stat
import math

#img = cv.imread('BLAH.png') #

#make a function: input image: output x,y
#check prev laser if it moved too much, if so, invalid. return (-1,-1)


'''
NEXT STEP: since filter red with min dist is prob optimal now, problem really is with circle detection.
time per image
when it's not a circle
optimize the parameters.

WORK ON:
ISSUE 1:
performance varies greatly for different videos, especially with the sofa shit.
1: good
2 : b
3 : b
4 : good
5 : good 

for vid2, check the canny edge image. decide to tune canny edge or param2


ISSUE 2: false positives: NEED better white red detection.
ALREADY SO LENIENT. BUT DAMN 
70 percent on real laser
90 percent on false laser
fuck.




'''


'''
parameters for cv2.HoughCircles
input:
image	8-bit, single-channel, grayscale input image.
method	Detection method, see HoughModes. Currently, the only implemented method is HOUGH_GRADIENT
dp	Inverse ratio of the accumulator resolution to the image resolution. For example, if dp=1 , the accumulator has the same resolution as the input image. If dp=2 , the accumulator has half as big width and height.
minDist	Minimum distance between the centers of the detected circles. If the parameter is too small, multiple neighbor circles may be falsely detected in addition to a true one. If it is too large, some circles may be missed.

param1	First method-specific parameter. In case of HOUGH_GRADIENT , it is the higher threshold of the two passed to the Canny edge detector (the lower one is twice smaller).
param2	Second method-specific parameter. In case of HOUGH_GRADIENT , it is the accumulator threshold for the circle centers at the detection stage. The smaller it is, the more false circles may be detected. Circles, corresponding to the larger accumulator values, will be returned first.
minRadius	Minimum circle radius.
maxRadius	Maximum circle radius. If <= 0, uses the maximum image dimension. If < 0, returns centers without finding the radius.

output:
circles	Output vector of found circles. Each vector is encoded as 3 or 4 element floating-point vector (x,y,radius) or (x,y,radius,votes) .

'''


'''
dp: anything larger than 2 yields too many cirlces. 0.5 gives about the same result. so far do 1
minDist:
    
param1: lower, less edges get filtered out.
param2: higher, less circles: 30 is optimal now


# circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50,
    param1=1, param2=33, minRadius=10, maxRadius=40) #max 60 pixel cir

'''
#    cv2.Smooth(gray, gray, cv2.CV_GAUSSIAN, 7, 7)
total_time = 0
total_circles = 0
no_circle = 0
no_laser = 0
frames = 0


white_detected = 0
red_detected = 0

avg_circles = 0
circle_detection = 0 #percent of time actually detected a circle
laser_detection = 0 #percentage of time detected a laser  given a circle
avg_time = 0

#USE THIS FUNCTION TO REPLACE MAIN: input a string of file path to image.
def master_func(path_to_image): #input an image, returns and prints the detected coordinate. Returns empty list if none found.
    frame = cv2.imread(path_to_image)
    detected_circles = detect_circle(frame)
    red_circle = filter_red(frame, detected_circles)
    print(red_circle)
    return red_circle


def detect_circle(frame): # Display the resulting frame, WITH THE LASER CIRCLED
    global total_circles
    global no_circle
    edges = canny_edge(frame, 30) #if this num is too high, less circles detected and high chance of no circled deteced

    gray = cv2.cvtColor(edges, cv2.COLOR_BGR2GRAY)
    #gray = cv2.medianBlur(gray, 5)
    
    #print("detecting circles...")
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50,
    param1=1, param2=13, minRadius=0, maxRadius=30) #max 60 pixel circle #50 , param2 small = more false circles
    
    #print("cirlces:")
    #print(circles)
    
    #circles = np.uint16(np.around(circles))
    count = 0
    if circles is not None:
         ignore, count, ignore2 = circles.shape
         #if count > 10: if too many adjust param1 for cann_edge and param2 
                
         #print("detected %s circle(s)" %count)
         total_circles += count

         
          #save the detected circles iamges for anaylysis:
         #im.save("./laser_circles" + str())
         
    else:
        print("Failed to detect laser in this frame, skip and continue")
        no_circle +=1
        return np.asarray([])
   
    #print(circles)
    #print(circles.shape) #1 by how many circles by 3 (x, y, and radius)
    
    return circles
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()


#draw the circles onto the frame
#circles is whether 1 by number of circles by 3 when num of circles >1 OR simply one d 3

def draw_circles(frame, circles):
    #print(circles.shape)
    #print(circles)
    
    #shape = circles.shape
    #print(type(shape))
    #if len(circles == 0):
     #   print("Can't draw circles on frame because cirlces np array is empty")
    if circles.shape == (3,):  #one circle
        (x, y ,r) = circles
        cv2.circle(frame, (x, y), r, (255, 255, 255), 1)  #the circle
        cv2.circle(frame, (x, y), 2, (0, 0, 0), 3) #the nucleus
    elif circles.ndim == 3:#multiple circles". circles.shape = 1 * number of circles * 3
        for (x, y ,r) in circles[0, :]:
            cv2.circle(frame, (x, y), r, (255, 255, 255), 1)  #the circle
            cv2.circle(frame, (x, y), 2, (0, 0, 0), 3) #the nucleus
    else:
        print("Can't draw circles on frame because cirlces np array is empty")

    
    cv2.imshow('frame',frame)
    cv2.waitKey(100) #1000 miliseconds
    #cv2.destroyAllWindows()
    #time.sleep(0.5)


def take_first(l):
    return l[0]

def take_second(l):
    return l[1]

def take_third(l):
    return l[2]

hsv_list = []
#min_distance 

def filter_red(frame, circles): #1920*1080*3
    global no_laser       
    global red_detected
    global white_detected
    global hsv_list
    
    
    if circles.ndim == 1:#one circle
        return circles

    elif circles.ndim == 3:
        #red_circles = []
        result = np.asarray([])
        min_dist = float("inf")
        
        for circle in circles[0, :]: #cirlce = (x, y ,radius)
            x = int(circle[0])
            y = int(circle[1])
            r,g,b = frame[y,x] 
            
    
        
            rgb = frame[y,x] 
            rgb_pixel = rgb.reshape((1,1,3))
            hsv = cv2.cvtColor(rgb_pixel, cv2.COLOR_BGR2HSV)
            h = hsv[0,0,0]
            s = hsv[0,0,1]
            v = hsv[0,0,2]
            
            red = (h < 200) and (s < 110) and (v>100) 
            if red:
                red_detected+=1
                squares = (h-81)**2 + (s-30)**2 + (v-250)**2
                dist = math.sqrt( squares )
                #red_circles.append(circle)
                
                if dist < min_dist:
                    #print("Found a better one!")
                    result = circle
                    min_dist = dist
                    #print(min_dist)
       
        if result.shape != (3,) :
            print("failed to find white or red center")
            no_laser += 1
        
        coord = result[0:2]
        #print(coord)
        return result
                    
        #n = len(red_circles)
        #red_circles = np.array(red_circles).reshape(1,n,3)       
        #return red_circles
          
            #hsv range:  vide 1 first 84 frames result
            #h: 0-200 (0-170) mean: 81, median 90
            #s: 0-110 (0-85) mean: 10 median: 5. 36?
            #v: 120-255 (129-255) mean: 250, median 255 
    else:
        print("Skipping filtering because function detect_cirlces detected no circles")
        #print(np.asarray([]))
        return np.asarray([])
    '''
    white = (r > 200 and g > 200 and b > 200) #(r > 220 and g > 220 and b > 220) 
    red = (r > 100 and g > 30 and b > 40) #(r > 120 and g > 40 and b > 60)
    if white:
        white_detected+=1
    if red:
        red_detected+=1
    
    
    if white or red:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv_list.append(hsv[y,x])
        return circle


    '''    
    
    

    '''
    #for debugging only
    coord = (x,y)
    rgb = frame[y,x] 
    print("coord:" + str(coord) +  " rgb: " +  str(rgb) )
    '''


def canny_edge(frame, val): #output a grayscale image of edges, easier for cv2.HoughCircles to detect circles
    ratio = 13 #3
    kernel_size = 3 #
    low_threshold = val #30
    img_blur = cv2.blur(frame, (3,3)) #3,3
    detected_edges = cv2.Canny(img_blur, low_threshold, low_threshold*ratio, kernel_size)
    mask = detected_edges != 0
    dst = frame * (mask[:,:,None].astype(frame.dtype)) #numpy array 
    #cv2.imshow('edges', dst)
    return dst

'''
canny edge argument:
    
image	8-bit input image.
edges	output edge map; single channels 8-bit image, which has the same size as image .
threshold1	first threshold for the hysteresis procedure.
threshold2	second threshold for the hysteresis procedure.
apertureSize	aperture size for the Sobel operator.

'''

def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        avg_circles = total_circles/frames
        circle_detection = 100 - no_circle/frames * 100
        laser_detection = 100 - no_laser/(frames - no_circle) *100
        #red_detection = 100 * red_detected/(frames - no_circle)
        red_detection = 100 * red_detected/total_circles
        white_detection = 100 * white_detected/(frames - no_circle)

        avg_time = total_time/frames
        
        '''
        #FIGURING OUT WHAT HSV VALUE IS BEST
        hsv_list.sort(key = take_first)#h
        h = [val[0] for val in hsv_list]
        
        
        print("Min h:")
        print(h[0])
        print("Max h:")
        print(h[-1])
        print("mean:")
        print(stat.mean(h))
        print("median:")
        print(stat.median(h))

        
        print(h)
        
        
        
        hsv_list.sort(key = take_second)#s
        h = [val[1] for val in hsv_list]
        
        print("Min s:")
        print(h[0])
        print("Max s:")
        print(h[-1])
        print("mean:")
        print(stat.mean(h))
        print("median:")
        print(stat.median(h))
        print(h)
        
        hsv_list.sort(key = take_third)#v
        h = [val[2] for val in hsv_list]
        
        print("Min v:")
        print(h[0])
        print("Max v:")
        print(h[-1])
        print("mean:")
        print(stat.mean(h))
        print("median:")
        print(stat.median(h))
        
        print(h)
        '''
        
        
        print("\nSUMMARY:")
        print("frames:", frames)
        print("%s average circles detected per frame" %round(avg_circles,2))
        print("%s percent circle_detection" %round(circle_detection,2) )
        print("%s percent of the time we are able to find at least one red laser" %round(laser_detection,2) )
        
        print("%s percent of all circled detected are classified as red" %round(red_detection,2) )
        #print("%s percent white_detection" %round(white_detection,2) )


        print("%s second per frame" % avg_time )
        sys.exit(0)
        
        
        
signal.signal(signal.SIGINT, signal_handler)
#signal.pause()



# Create a VideoCqapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
#cap = cv2.VideoCapture('/Users/audi/Desktop/x1/Link_Laser_Samples/laser_sample_3/video.mp4')


# Check if camera opened successfully
#if (cap.isOpened()== False): 
 # print("Error opening video stream or file")
 
# Read until video is completed

#while(cap.isOpened()):
  # Capture frame-by-frame
  



    
frame_index = 1

while (True):
    frame_str = '/Users/audi/Desktop/x1/Link_Laser_Samples/laser_sample_1/rgb_frames/' +"video_frame_" + str(frame_index) + ".jpg"
    frame = cv2.imread(frame_str)
  
    if frame is None:
        break
  #ret, frame = cap.read()

  #if ret == True: 
    start_time = time.time()

    #original_frame = np.copy(frame)
    detected_circles = detect_circle(frame)
    #print(detected_circles)
    
    #edges = canny_edge(frame, 30)
    #draw_circles(edges, detected_circles) #will modify frame to show the circles
    
    
    #time.sleep(2)
    red_circle = filter_red(frame, detected_circles)
    #print(red_circle)
    
    time_elapsed =  time.time() - start_time
    total_time += time_elapsed
    
    #NOTE: DON'T EVER DRAW BEFORE YOU DETECT, WILL MESS UP THE IMAGE DATA
    draw_circles(frame, red_circle) #will modify frame to show the circles
    #time.sleep(2)
    
    
    #DO SOME SUMMARY STATISTICS
    
    #if len(detected_circles) == 0: 
     #   no_circle += 1
        
        
    frames += 1
    frame_index +=1
    
   
    
    
    # Press Q on keyboard to  exit
    #if cv2.waitKey(25) & 0xFF == ord('q'):
       
  # Break the loop
  #else:
    #print("Failed to load frame:")
    #break



 
# When everything done, release the video capture object
#cap.release()
 
# Closes all the frames
cv2.destroyAllWindows()




'''

cap = cv2.VideoCapture("BLAH.mp4")
while(True):
    gray = cv2.medianBlur(cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY),5)
    cirles=cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 10)# ret=[[Xpos,Ypos,Radius],...]
    if cirles!=None:print "Circle There !"
    cv2.imshow('video',gray)
    if cv2.waitKey(1)==27:# esc Key
        break
cap.release()
cv2.destroyAllWindows()

'''






'''
cap.read() returns a bool (True/False). If frame is read correctly, it will be True.
'''
