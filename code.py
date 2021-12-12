import time
import board
import digitalio
import adafruit_rgbled
import busio
import neopixel

class StickPlayer():    
    version = 1
    frames = 1
    columns = 1
    leds = 144
    duration = 5
    blank1 = 0
    blank2 = 0
        
    step_time = 0
    step_time_seconds = 0
    time_slices = 320

    frame_num = 0
    column_num = 0
    current_col = [(0, 0, 0)]
    frame_start_time = 0
    
    NUM_LEDS = 144
    BRIGHTNESS = 1
    CLEAR = (0, 0, 0)  # clear (or second color)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    led_strip = False
    button_boot = False
    button_a = False
    button_b = False
    led = False
    
    hardware = False
    
    def __init__(self, hardware=False):
        self.hardware = hardware
        self.load_meta_data() 
        
        if(self.hardware):
            self.add_hardware()
        else:
            self.load_frame()
            self.show_frame()
            exit()
        
    def __str__(self):
        return "f"+str(self.frames)+" c"+str(self.columns)+" l"+str(self.leds)
        
    def add_hardware(self):
        print("add_hardware")
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
        
        self.led.color = self.BLUE
    
    def load_meta_data(self):
        print("load_meta_data")
        self.frame_num = 0
            
        try:
            # get filename ("/media/meggleton/CIRCUITPY/data.hex")
            self.file = open("data.hex","rb")
            self.version    = int.from_bytes(self.file.read(1),"little")    
            self.frames     = int.from_bytes(self.file.read(1),"little")    
            self.columns    = int.from_bytes(self.file.read(2),"little")    
            self.leds       = int.from_bytes(self.file.read(1),"little")    
            self.duration   = int.from_bytes(self.file.read(1),"little")    
            self.blank1     = int.from_bytes(self.file.read(1),"little")    
            self.blank2     = int.from_bytes(self.file.read(1),"little") 
        
            print(str(self))
            
        except OSError as e:
            self.led.color = self.RED
            print(str(e))

    def show_frame(self):
        print("show_frame", self.frame_num )
        self.frame_start_time = 1.0 + time.monotonic()
        
        duration = float(self.duration)
        self.step_time = (duration / float(self.time_slices))
        self.step_time_seconds = duration / float(self.time_slices)
        
        self.load_column()
        for i in range(self.columns + 1):
            self.column_num = i
            while time.monotonic() < (self.frame_start_time + (self.step_time * self.column_num)):
                time.sleep(0.01)
            #    pass
            self.led_strip.show()
            if self.column_num < self.columns:
                self.load_column()
            else:
                self.led_strip.fill(self.CLEAR)
            
        self.frame_num += 1

    def load_column(self):
        
        print("load_column", self.column);
        col_data = []
        try:
            for i in range(self.leds):
                num = list(self.file.read(3))
                self.led_strip[i] = tuple(num)#self.current_col[i]
            return col_data 
                        
        except OSError as e:
            self.led.color = self.RED
            self.led_strip.fill(self.CLEAR)
            self.led_strip.show()
            return 

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
    player = StickPlayer( hardware=True )
    player.main()