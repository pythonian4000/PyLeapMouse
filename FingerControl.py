#William Yager
#Dennis Janssen
#Leap Python mouse controller POC
#This file is for pointer-finger-based control (--finger and default)


import math
from leap import Leap, Mouse
import subprocess
import Geometry
from MiscFunctions import *


class Finger_Control_Listener(Leap.Listener):  #The Listener that we attach to the controller. This listener is for pointer finger movement
    def __init__(self, mouse, smooth_aggressiveness=8, smooth_falloff=1.3):
        super(Finger_Control_Listener, self).__init__()  #Initialize like a normal listener
        #Initialize a bunch of stuff specific to this implementation
        self.screen = None
        self.screen_resolution = (0,0)
        self.cursor = mouse.absolute_cursor()  #The cursor object that lets us control mice cross-platform
        self.mouse_position_smoother = mouse_position_smoother(smooth_aggressiveness, smooth_falloff) #Keeps the cursor from fidgeting
        self.mouse_button_debouncer = debouncer(5)  #A signal debouncer that ensures a reliable, non-jumpy click
        self.most_recent_pointer_finger_id = None  #This holds the ID of the most recently used pointing finger, to prevent annoying switching

    def on_init(self, controller):
        if controller.calibrated_screens.empty:
            print "Calibrate your Leap screen feature"
        self.screen = controller.calibrated_screens[0]
        self.screen_resolution = (self.screen.width_pixels, self.screen.height_pixels)

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
            hand = frame.hands[0]  #The first hand
            if has_two_pointer_fingers(hand):  #Scroll mode
                self.do_scroll_stuff(hand)
            if has_four_pointer_fingers(hand):  #Scroll mode
                self.do_four_finger_gesture_stuff(hand)
            else:  #Mouse mode
                self.do_mouse_stuff(hand)

    def do_scroll_stuff(self, hand):  #Take a hand and use it as a scroller
        fingers = hand.fingers  #The list of fingers on said hand
        if not fingers.empty:  #Make sure we have some fingers to work with
            sorted_fingers = sort_fingers_by_distance_from_screen(fingers)  #Prioritize fingers by distance from screen
            finger_velocity = sorted_fingers[0].tip_velocity  #Get the velocity of the forwardmost finger
            x_scroll = self.velocity_to_scroll_amount(finger_velocity.x)
            y_scroll = self.velocity_to_scroll_amount(finger_velocity.y)
            self.cursor.scroll(x_scroll, y_scroll)

    def do_four_finger_gesture_stuff(self, hand): #Four fingers can be used to launch Mission Control and switch spaces
        fingers = hand.fingers #The list of fingers on said hand
        if not fingers.empty: #Make sure we have some fingers to work with
            sorted_fingers = sort_fingers_by_distance_from_screen(fingers) #Prioritize fingers by distance from screen
            finger_velocity = sorted_fingers[0].tip_velocity #Get the velocity of the forwardmost finger
            gesture_script = None
            if self.velocity_to_scroll_amount(finger_velocity.y) > 200 or self.velocity_to_scroll_amount(finger_velocity.y) < -100: # Once the finger reaches a certain velocity (or negative velocity for downward movement...
                gesture_script = "tell app \"Mission Control\" to activate" #Use AppleScript to trigger Mission Control
            if self.velocity_to_scroll_amount(finger_velocity.x) > 300: #Moving hand to the right
                gesture_script = "tell application \"System Events\" to key code 124 using control down" #Use AppleScript to press Ctrl+Right
            if self.velocity_to_scroll_amount(finger_velocity.x) < -300: #Moving hand to the right
                gesture_script = "tell application \"System Events\" to key code 123 using control down" #Use AppleScript to press Ctrl+Left
            if gesture_script != None:
                PIPE = subprocess.PIPE
                osa = subprocess.Popen('osascript', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                (out, err) = osa.communicate(gesture_script)
                gesture_script = None

    def velocity_to_scroll_amount(self, velocity):  #Converts a finger velocity to a scroll velocity
        #The following algorithm was designed to reflect what I think is a comfortable
        #Scrolling behavior.
        vel = velocity  #Save to a shorter variable
        vel = vel + math.copysign(300, vel)  #Add/subtract 300 to velocity
        vel = vel / 150
        vel = vel ** 3  #Cube vel
        vel = vel / 8
        vel = vel * 5  #I (Dennis) added this because I felt scrolling should be faster. Feel free to edit this to make it feel better for you.
        vel = vel * -1  #Negate direction, depending on how you like to scroll
        return vel

    def do_mouse_stuff(self, hand):  #Take a hand and use it as a mouse
        fingers = hand.fingers  #The list of fingers on said hand
        if not fingers.empty:  #Make sure we have some fingers to work with
            pointer_finger = self.select_pointer_finger(fingers)  #Determine which finger to use
            intersection = self.screen.intersect(pointer_finger, True)  #Where the finger projection intersects with the screen
            if not math.isnan(intersection.x) and not math.isnan(intersection.y):  #If the finger intersects with the screen
                x_coord = intersection.x * self.screen_resolution[0]  #x pixel of intersection
                y_coord = (1.0 - intersection.y) * self.screen_resolution[1]  #y pixel of intersection
                x_coord,y_coord = self.mouse_position_smoother.update((x_coord,y_coord)) #Smooth movement
                self.cursor.move(x_coord,y_coord)  #Move the cursor
                if len(hand.fingers) == 2:  #I changed clicking, so it can happen with two fingers
                    sorted_fingers = sort_fingers_left_to_right(hand.fingers)  #Sorting fingers from left to right, so I can use my index finger for pointing. Sorry lefties!
                    finger1_pos = Geometry.to_vector(sorted_fingers[0].tip_position)
                    finger2_pos = Geometry.to_vector(sorted_fingers[1].tip_position)
                    difference = finger1_pos - finger2_pos
                    if difference.norm() > 40 and left_finger_still(sorted_fingers[0].tip_velocity.y) and right_finger_moving(sorted_fingers[1].tip_velocity.y):  #Check if the fingertips are a bit apart, the right finger is clicking down but the left finger is keeping still. This line prevents clicking while scrolling (or it should...)
                        self.mouse_button_debouncer.signal(True)  #We have detected a possible click. The debouncer ensures that we don't have click jitter
                    else:
                        self.mouse_button_debouncer.signal(False)  #Same idea as above (but opposite)

                    if self.cursor.left_button_pressed != self.mouse_button_debouncer.state:  #We need to push/unpush the cursor's button
                        self.cursor.set_left_button_pressed(self.mouse_button_debouncer.state)  #Set the cursor to click/not click

    def select_pointer_finger(self, possible_fingers):  #Choose the best pointer finger
        sorted_fingers = sort_fingers_left_to_right(possible_fingers)  #Prioritize fingers from left to right, sorry Lefties!
        if self.most_recent_pointer_finger_id != None and self.number_of_fingers != None:  #If we have a previous pointer finger in memory
             for finger in sorted_fingers:  #Look at all the fingers
                if finger.id == self.most_recent_pointer_finger_id and self.number_of_fingers == len(sorted_fingers):  #The previously used pointer finger is still in frame
                    return finger  #Keep using it
        #If we got this far, it means we don't have any previous pointer fingers OR we didn't find the most recently used pointer finger in the frame
        self.most_recent_pointer_finger_id = sorted_fingers[0].id  #This is the new pointer finger
        self.number_of_fingers = len(sorted_fingers)
        return sorted_fingers[0]
