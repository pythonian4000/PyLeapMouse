#William Yager
#Leap Python mouse controller POC
import sys
from leap import Leap, Mouse
from HandControl import Hand_Control_Listener  #For hand-position based control
from PalmControl import Palm_Control_Listener  #For palm-tilt based control
from FingerControl import Finger_Control_Listener  #For finger-pointing control

def show_help():
    print "----------------------------------PyLeapMouse----------------------------------"
    print "Use --finger (or blank) for pointer finger control, and --palm for palm control."
    print "Set smooth aggressiveness (# samples) with \"--smooth-aggressiveness [# samples]\""
    print "Set smooth falloff with \"--smooth-falloff [% per sample]\""
    print "Read README.md for even more info.\n"

def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        show_help()
        return

    print "----------------------------------PyLeapMouse----------------------------------"
    print "Use --finger (or blank) for pointer finger control, and --palm for palm control."
    print "Use -h or --help for more info.\n"

    #Default
    mode = 0
    smooth_aggressiveness = 8
    smooth_falloff = 1.3

    for i in range(0,len(sys.argv)):
        arg = sys.argv[i].lower()
        if "--palm" in arg:
            mode = 1
        elif "--hand" in arg:
            mode = 2
        if "--smooth-falloff" in arg:
            smooth_falloff = float(sys.argv[i+1])
        if "--smooth-aggressiveness" in arg:
            smooth_aggressiveness = int(sys.argv[i+1])

    listener = None;  #I'm tired and can't think of a way to organize this segment nicely

    #Create a custom listener object which controls the mouse
    if mode == 0:  #Finger pointer mode
        listener = Finger_Control_Listener(Mouse, smooth_aggressiveness=smooth_aggressiveness, smooth_falloff=smooth_falloff)
        print "Using finger mode..."
    elif mode == 1:  #Palm control mode
        listener = Palm_Control_Listener(Mouse)
        print "Using palm mode..."
    else:  #Hand position mode
        listener = Hand_Control_Listener(Mouse, smooth_aggressiveness=smooth_aggressiveness, smooth_falloff=smooth_falloff)
        print "Using hand mode..."


    controller = Leap.Controller()  #Get a Leap controller
    print "Adding Listener."
    controller.add_listener(listener)  #Attach the listener

    #Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()
    #Remove the sample listener when done
    controller.remove_listener(listener)

main()
