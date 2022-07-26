import board
import busio
import time
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
import usb_hid
from adafruit_hid.keyboard import Keyboard
# Import the keyboard layout description
from adafruit_hid.keyboard_layout_uk import KeyboardLayoutUK

from adafruit_hid.keycode import Keycode

version = "0.0"

class Switch():
    def __init__(self, pin, name, ch): 
        self.pin = pin
        self.name = name
        self.ch = ch
    
class Key():
    def __init__(self, keyboard, switch): 
        self.keyboard = keyboard
        self.switch = switch
        # make a digital io from the pin
        io = DigitalInOut(self.switch.pin)
        # add a pullup
        io.pull = Pull.UP
        # create the key debouncer
        self.debounce = Debouncer(io,interval=0.01)
        self.debounce.update()
        self.pressed = not self.debounce.value

    def update(self):
        debounce = self.debounce
        debounce.update()
        if debounce.fell:
            self.key_down()
        if debounce.rose:
            self.key_up()
            
    def key_down(self):
        print("key:",self.switch.name,"down")
        keyboard = self.keyboard
        keyboard.press(self.switch.ch)
        self.pressed = True
    
    def key_up(self):
        keyboard = self.keyboard
        print("key:",self.switch.name,"up")
        keyboard.release(self.switch.ch)
        self.pressed = False
            
class DirtywaveKeys:
    def __init__(self, key_switches):
        hello_message = "Dirtwave M8 keyboard " + str(version)
        print(hello_message)
        #
        self.usb_kbd = Keyboard(usb_hid.devices)
        # Set the required keyboard layout
        self.usb_layout = KeyboardLayoutUK(self.usb_kbd)
        #
        # Create the array of keys
        self.keys = []
        # going to use a mask bit for each key to assemble a key pattern
        for switch in key_switches:
            # Make the key
            key = Key(keyboard=self.usb_kbd,switch=switch)
            # add it to the list of keys
            self.keys.append(key)
        
        self.wait_for_all_keys_up()
        
    def key_down(self):
        for key in self.keys:
            # get the key debouncer
            debounce = key.debounce
            debounce.update()
            if not debounce.value:
                return True
        return False
        
    def wait_for_all_keys_up(self):
        while True:
            if self.key_down():
                continue
            return
        
    def test(self):
        print("Test")        
        while True:
            # scan the keyboard and turn pressed keys red
            for key in self.keys:
                # get the key debouncer
                debounce = key.debounce
                debounce.update()
                if debounce.fell:
                    print("Key down:", key.switch.name)
                if debounce.rose:
                    print("Key up:", key.switch.name)
    
    def update_keys(self):
        for key in self.keys:
            key.update()
    
    def update(self):
        self.update_keys()
        
    def run(self):
        while True:
            self.update()
            
key_switches = [
        Switch(pin=board.GP18,name="up",ch=Keycode.UP_ARROW),      # up
        Switch(pin=board.GP19,name="option",ch=Keycode.Z),  # option
        Switch(pin=board.GP20,name="Edit",ch=Keycode.X),    # edit 
        Switch(pin=board.GP13,name="Left",ch=Keycode.LEFT_ARROW),    # left
        Switch(pin=board.GP12,name="down",ch=Keycode.DOWN_ARROW),    # down
        Switch(pin=board.GP11,name="right",ch=Keycode.RIGHT_ARROW),   # right
        Switch(pin=board.GP21,name="shift",ch=Keycode.LEFT_SHIFT),   # shift 
        Switch(pin=board.GP22,name="play",ch=Keycode.SPACEBAR)   # play - h
        ]

keyboard = DirtywaveKeys(key_switches=key_switches)
keyboard.run()

