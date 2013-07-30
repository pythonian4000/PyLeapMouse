#Jack Grigg
#Leap Python mouse controller POC
#This file is for hand-position and gesture-based control (--hand)
#Based on PalmControl.py by William Yager


import math
from leap import Leap, Mouse
import Geometry
from MiscFunctions import *


class Hand_Control_Listener(Leap.Listener):  #The Listener that we attach to the controller. This listener is for hand position movement
    def __init__(self, mouse, smooth_aggressiveness, smooth_falloff):
        super(Hand_Control_Listener, self).__init__()  #Initialize like a normal listener
        #Initialize a bunch of stuff specific to this implementation
        self.screen_resolution = (0,0)
        self.cursor = mouse.absolute_cursor()  #The cursor object that lets us control mice cross-platform
        self.mouse_position_smoother = mouse_position_smoother(smooth_aggressiveness, smooth_falloff) #Keeps the cursor from fidgeting
        self.gesture_debouncer = n_state_debouncer(5,3)  #A signal debouncer that ensures a reliable, non-jumpy gesture detection

    def on_init(self, controller):
        self.screen_resolution = (Mouse.GetDisplayWidth(), Mouse.GetDisplayHeight())
        print self.screen_resolution

        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        frame = controller.frame()  #Grab the latest 3D data
        if not frame.hands.empty:  #Make sure we have some hands to work with
            rightmost_hand = frame.hands.rightmost  #Get rightmost hand
            leftmost_hand = None
            if len(frame.hands) > 1:  #Multiple hands. We have a right AND a left
                leftmost_hand = frame.hands.leftmost  #Get leftmost hand
            self.do_gesture_recognition(leftmost_hand, rightmost_hand)

    #The gesture hand signals what action to do,
    #The mouse hand gives extra data (if applicable)
    #Like scroll speed/direction
    def do_gesture_recognition(self, gesture_hand, mouse_hand):
        if gesture_hand:
            if len(gesture_hand.fingers) == 2:  #Two open fingers on gesture hand (scroll mode)
                self.gesture_debouncer.signal(2)  #Tell the debouncer we've seen this gesture
            elif len(gesture_hand.fingers) == 1:  #One open finger on gesture hand (click down)
                self.gesture_debouncer.signal(1)
            else:  #No open fingers or 3+ open fingers (click up/no action)
                self.gesture_debouncer.signal(0)
        else:  #Only one hand
            self.gesture_debouncer.signal(0)
        #Now that we've told the debouncer what we *think* the current gesture is, we must act
        #On what the debouncer thinks the gesture is
        if self.gesture_debouncer.state == 2:  #Scroll mode
            y_scroll_amount = self.velocity_to_scroll_amount(mouse_hand.palm_velocity.y)  #Mouse hand controls scroll amount
            x_scroll_amount = self.velocity_to_scroll_amount(mouse_hand.palm_velocity.x)
            self.cursor.scroll(x_scroll_amount, y_scroll_amount)
        elif self.gesture_debouncer.state == 1:  #Click/drag mode
            if not self.cursor.left_button_pressed: self.cursor.click_down()  #Click down (if needed)
            self.do_mouse_stuff(mouse_hand)  #We may want to click and drag
        elif self.gesture_debouncer.state == 0:  #Move cursor mode
            if self.cursor.left_button_pressed: self.cursor.click_up()  #Click up (if needed)
            self.do_mouse_stuff(mouse_hand)

    def do_mouse_stuff(self, hand):  #Take a hand and use it as a mouse
         print hand.palm_position.x, hand.palm_position.y
         x_coord = 10.0 * hand.palm_position.x + (self.screen_resolution[0] / 2)
         y_coord = self.screen_resolution[1] - 10.0 * (hand.palm_position.y - 100)
         x_coord,y_coord = self.mouse_position_smoother.update((x_coord,y_coord)) #Smooth movement
         self.cursor.move(x_coord,y_coord)  #Move the cursor

    def velocity_to_scroll_amount(self, velocity):  #Converts a finger velocity to a scroll velocity
        #The following algorithm was designed to reflect what I think is a comfortable
        #Scrolling behavior.
        vel = velocity  #Save to a shorter variable
        vel = vel + math.copysign(300, vel)  #Add/subtract 300 to velocity
        vel = vel / 150
        vel = vel ** 3  #Cube vel
        vel = vel / 8
        vel = vel * -1  #Negate direction, depending on how you like to scroll
        return vel

    def convert_position_to_mouse_velocity(self, pos):
        x_movement = pos.x / 150
        y_movement = pos.y / 150
        return (x_movement, y_movement)
