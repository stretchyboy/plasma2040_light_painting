import time
from typing import List

class MockButton:
    value = False

class MockLED:
    color = (0,0,0)

class MockStrip(List):
    def __init__(self, count):
        self.extend([(0,0,0) for i in range(count)])
    
    def show(self):
        print (self)

    def fill(self, color):
        pass
    
class StickPlayer():    
    version     = 1
    frames      = 1
    columns     = 1
    leds        = 144
    duration    = 5
    blank1      = 0
    blank2      = 0
        
    step_time        = 0
    step_time_seconds   = 0
    time_slices         = 320

    frame_num           = 0
    current_frame       = [[(0,0,0)]]
    frame_start_time    = 0
    column_num          = 0

    NUM_LEDS = 144

    BRIGHTNESS = 1

    CLEAR = (0, 0, 0)  # clear (or second color)

    RED     = (255, 0, 0)
    GREEN   = (0, 255, 0)
    BLUE    = (0, 0, 255)

    led_strip   = MockStrip(144)
    button_boot = MockButton()
    button_a    = MockButton()
    button_b    = MockButton()
    led         = MockLED()
    
    hardware    = False
    
    def __init__(self, hardware=False):
        self.load_meta_data()
        self.hardware = hardware
        #print ("self", str(self))

        if(self.hardware):
            self.add_hardware()
        else:
            self.load_frame()
            self.show_frame()
            exit()
        
         
    def __str__(self):
        return "f"+str(self.frames)+" c"+str(self.columns)+" l"+str(self.leds)

        
    def add_hardware(self):
        import board
        import digitalio
        import adafruit_rgbled
        import busio
        import neopixel
        
        self.led_strip = neopixel.NeoPixel(board.DATA, self.NUM_LEDS, brightness=self.BRIGHTNESS, auto_write=False)

        self.button_boot = digitalio.DigitalInOut(board.USER_SW)
        self.button_boot.direction = digitalio.Direction.INPUT
        self.button_boot.pull = digitalio.Pull.UP

        self.button_a = digitalio.DigitalInOut(board.SW_A)
        self.button_a.direction = digitalio.Direction.INPUT
        self.button_a.pull = digitalio.Pull.UP

        self.button_b = digitalio.DigitalInOut(board.SW_B)
        self.button_b.direction = digitalio.Direction.INPUT
        self.button_b.pull = digitalio.Pull.UP

        self.led = adafruit_rgbled.RGBLED(board.LED_R, board.LED_G, board.LED_B, invert_pwm = True)

        self.led_strip.fill(self.CLEAR)
        self.led_strip.show()
    

    def load_meta_data(self):
        self.led.color = self.BLUE
        self.frame_num = 0
        if self.hardware == False:
            print ("self", str(self))
            
        try:
            # get filename ("/media/meggleton/CIRCUITPY/data.hex")

            with open("data.hex","rb") as file:    
                self.version    = int.from_bytes(file.read(1),"little")    
                self.frames     = int.from_bytes(file.read(1),"little")    
                self.columns    = int.from_bytes(file.read(2),"little")    
                self.leds       = int.from_bytes(file.read(1),"little")    
                self.duration   = int.from_bytes(file.read(1),"little")    
                self.blank1     = int.from_bytes(file.read(1),"little")    
                self.blank2     = int.from_bytes(file.read(1),"little") 
        
            if self.hardware == False:
                print ("self", str(self))
                
        except OSError as e:
            self.led.color = self.RED
        
                
    def load_frame(self):
        self.led.color = self.GREEN
        frame_data = []
        try:
            with open("data.hex","rb") as file:               
                junk = file.read(8 + (3 * self.frame_num * self.columns * self.leds ))
                
                for i in range(self.columns):
                    frame_data.append([])
                    for j in range(self.leds):
                        num = list(file.read(3))
                        frame_data[i].append(tuple(num))
            return frame_data
                        
        except OSError as e:
            self.led.color = self.RED
        
    def show_frame(self):
        self.frame_start_time = 1.0 + time.monotonic()
        self.current_frame = self.load_frame()    
        
        duration = float(self.duration)
        self.step_time = (duration / float(self.time_slices))
        self.step_time_seconds = duration / float(self.time_slices)
        
        self.show_column()

    def on_frame_end(self):
        self.led_strip.fill(self.CLEAR)
        self.led_strip.show()
        self.frame_num += 1

    def show_column(self):
        while time.monotonic() < (self.frame_start_time + (self.step_time * self.column_num)):
            time.sleep(0.0001)

        if(self.column_num >= self.columns):    
            self.on_frame_end()
            return 
        
        for i in range(self.leds):
            self.led_strip[i] = self.current_frame[self.column_num][i]

        self.led_strip.show()
        self.column_num += 1
        self.show_column()
        
    def button_read(self, button):
        return not button.value
       
    def main(self):
        while True:
            if self.button_read(self.button_a):
                self.show_frame()
                
            if self.button_read(self.button_b):
                if self.frame_num > 0:
                    self.frame_num -= 1
                self.show_frame()
                
            if self.button_read(self.button_boot):
                pass
            
if __name__ == '__main__':
    player = StickPlayer(hardware=False)
    player.main()
     


        
            
            
    