README:

Hi, this respository was forked from the PyLeapMouse by wyager, he offered a great starting point, so: thanks! I added some basic Mac functionality, like Mission Control and switching spaces. I'll try to explain in detail, feel free to contact me if some parts need more in-depth explanation.

NOTE: Quickly tested this out for SDK 0.7.4, everything seems to work, although the connection with osascript seems even slower now...

USAGE:
1. Moving a hand with 1 or 2 fingers in the field of sight of the Leap should make your mouse pointer move. The left finger is always the pointing finger, since I'm right-handed. (Southpaws, feel free to edit this!)
2. Moving your 2 fingers (I myself use my index and middle finger) closer together 'grabs' the page and you can then move it up and down for scrolling. Moving them further apart again 'releases' the page.
3. Moving the most right finger in a quick flick downwards performs a 'click'. This is a bit tricky, since it feels like a right-mouse-click actually… Hope this makes sense.
4. Moving 4 fingers into the frame activates gestures-mode, with up and down movement activates and deactivates Mission Control, left and right are used to switch spaces. Note: move your hand faster in the direction you want to go and go back slower. Moving back and forth equally fast will make you switch back and forth between two spaces as well. (Sounds obvious, yet I struggle with this myself…)


CONFIGURATION:
1. Copy the entire folder to your local Mac. I myself like using the GitHub Mac App, since it always gives me a good view of the changes I made and also makes it easy to manage local and online repositories. Some developers here will probably shoot me for this confession... Oh well...
2. Open Terminal and open the folder you copied the code to. The easiest way to do so is type "cd" and then drag the folder to your Terminal window. In my case the command is: "cd /Users/dennis/PyLeapMouse ".
3. Run the Python file PyLeapMouse.py. The following command will do: "python PyLeapMouse.py". The app should start giving you some feedback on the startup and notify you it's up and running eventually.

