#!/usr/bin/env python

from __future__ import print_function

import time
from sr.robot import *

a_th = 2.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

silver = True
""" boolean: variable for letting the robot know if it has to look for a silver or for a golden marker"""

R = Robot()
""" instance of the class Robot"""

def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0


def clear_way(dist, rot_y):
	"""
    Function to determine if the way to the next silver token is free or if there is a golden token 
    in between.

    Returns:
    True(boolean): if there is a golden token closer than a silver one in a range of [-10, 10]
                    in the direction of the silver detection
    False(boolean): if there isn't a golden token on the way of the robot

    Args:
    dist(float): distance from the robot and the silver token
    rot_y(float): orientation in degrees between the robot and the silver token
    """
	for token in R.see():
		if  token.info.marker_type is MARKER_TOKEN_GOLD and rot_y-10 < token.rot_y < rot_y + 10 and token.dist < dist:
			return True       		
	return False


def find_silver_token():
    """
    Function to find the the next silver token. The '-90 <= token.rot_y <= 90' condition is used
    to consider just the tokens in front of the robot (avoiding searching for the one we have just released).
    The 'not(clear_way(token.dist, token.rot_y))' condition assure me that there aren't golden token
    between the robot and the next silver token. 

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if -90<=token.rot_y<=90 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and not(clear_way(token.dist, token.rot_y)):
            dist=token.dist
	    rot_y=token.rot_y

    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_front_wall():
    """
    Function to find the closest golden token in front of the robot (that is the one on the wall in front 
    of it). To be sure we don't detect token on the sides of the robot the range in which it can search for 
    the token is [-7.5, 7.5].

    Returns:
	dist (float): distance of the golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if -7.5<token.rot_y<7.5 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_left_wall():
    """
    Function to find the closest golden token on the wall on the left of the robot, in a range of 
    [-105, 75].

    Returns:
	dist (float): distance of the closest left golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the left golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if -105<token.rot_y<-75 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_right_wall():
    """
    Function to find the closest golden token on the wall on the right of the robot, in a range of
    [75, 105].

    Returns:
	dist (float): distance of the closest right golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the right golden token (-1 if no golden token is detected)
    """
    
    dist=100
    for token in R.see():
        if 75<token.rot_y<105 and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def drive_safely():

    """
    Function to drive the robot avoiding to touch the wall on its sides. To do so, it is considered a limit
    on the left and on the right of 0.75m that, if exceeded, make the robot turn a bit to return on the 
    centre of the corridor. The same applies for the frontal wall where, if the limit of 0.9 is exceeded, 
    make the robot turn of +90 clockwise when there is a wall on the left (controlled with a distance 
    limitation again) or +90 counter-clockwise when there is a wall on the right.
    """

    dist_right = find_right_wall()[0]
    dist_left = find_left_wall()[0]
    dist_front = find_front_wall()[0]

    if dist_right < 0.75:
        turn(-5,1) #turn counter-clockwise
        drive(30,0.5)
    elif dist_left < 0.75:
        turn(5,1) #turn clockwise
        drive(30,0.5)
    elif dist_front < 0.9:
        if dist_right < 2.5:
            turn(-30,1)
        elif dist_left < 2.5:
            turn(30,1)    
        
        drive(40,0.5) #drive after the turning

    drive(50,0.1)  #drive if there aren't wall detections

### main ###

while 1:
    
	dist, rot_y = find_silver_token()      

    	if dist==-1: # if no token is detected, we make the robot turn 
		print("I don't see any token!!") 
		drive_safely()          
	else:
		drive_safely() #after detecting the silver token the robot drives safe to it
              	
        	if dist <d_th: # if we are close to the token, we try grab it.
        		print("Found it!")
        		if R.grab(): # if we grab the token, we turn the robot go forward, we release the token, and we go back to the initial position
        		        print("Gotcha!")
				turn(30, 1.999)  #turn 180 degrees
		                drive(40,0.25)
		        	R.release()
        	        	drive(-40,0.25)  
		            	turn(-30, 1.999) #turn 180 degrees again
                    	
		        else:
        	        	print("Aww, I'm not close enough.")
        	elif -a_th<= rot_y <= a_th: # if the robot is well aligned with the token, we go forward
        		print("Ah, that'll do.")
        		drive(100, 0.05)
		elif rot_y < -a_th: # if the robot is not well aligned with the token, we move it on the left or on the right
        		print("Left a bit...")
                	turn(-8, 0.125)
		elif rot_y > a_th:
                	print("Right a bit...")
        		turn(+8, 0.125)
	
