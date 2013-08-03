from pymouse import PyMouse
mouse = PyMouse()


#A cursor that does commands based on absolute position (good for finger pointing)
class absolute_cursor(object):
    def __init__(self):
        screen_size = mouse.screen_size()
        self.x_max = screen_size[0] - 1
        self.y_max = screen_size[1] - 1
        self.left_button_pressed = False
        self.x = 0
        self.y = 0

    def move(self, posx, posy):  #Move to coordinates
        self.x = posx
        self.y = posy
        if self.x > self.x_max:
            self.x = self.x_max
        if self.y > self.y_max:
            self.y = self.y_max
        if self.x < 0.0:
            self.x = 0.0
        if self.y < 0.0:
            self.y = 0.0
        if self.left_button_pressed:  #We are dragging
            mouse.drag(self.x, self.y)
        else:  #We are not dragging
            mouse.move(self.x, self.y)

    def click(self, posx=None, posy=None):  #Click at coordinates (current coordinates by default)
        if posx == None:
            posx = self.x
        if posy == None:
            posy = self.y
        mouse.click(posx, posy)

    def set_left_button_pressed(self, boolean_button):  #Set the state of the left button
        if boolean_button == True:  #Pressed
            self.click_down()
        else:  #Not pressed
            self.click_up()

    def click_down(self, posx=None, posy=None):
        if posx == None:
            posx = self.x
        if posy == None:
            posy = self.y
        mouse.press(posx, posy)
        self.left_button_pressed = True

    def click_up(self, posx=None, posy=None):
        if posx == None:
            posx = self.x
        if posy == None:
            posy = self.y
        mouse.release(posx, posy)
        self.left_button_pressed = False

    def rightClick(self, posx=None, posy=None):
        if posx == None:
            posx = self.x
        if posy == None:
            posy = self.y
        mouse.click(posx, posy, button=2)

    def scroll(self, x_movement, y_movement):
        mouse.scroll(vertical=y_movement, horizontal=x_movement)


#Allows for relative movement instead of absolute movement. This implementation is not a "true" relative mouse,
#but is really just a relative wrapper for an absolute mouse. Not the best way to do it, but I need to
#figure out how to send raw "mouse moved _this amount_" events. This class is (as of writing) untested.
#It's only here in case someone else wants to figure out how to do this properly on OS X.
#I will be "actually" implementing this on Windows shortly. OSX TBD.
class relative_cursor(absolute_cursor):
    def __init__(self):
        absolute_cursor.__init__(self)

    def move(self, x_amt, y_amt):
        self.x = self.x + x_amt
        self.y = self.y + y_amt
        if self.x > self.x_max:
            self.x = self.x_max
        if self.y > self.y_max:
            self.y = self.y_max
        if self.x < 0.0:
            self.x = 0.0
        if self.y < 0.0:
            self.y = 0.0
        if self.left_button_pressed:  #We are dragging
            mouse.drag(self.x, self.y)
        else:  #We are not dragging
            mouse.move(self.x, self.y)
