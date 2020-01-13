import leds
import display
import vibra
import utime
import buttons
import color
import bhi160


class SumBuffer:
    def __init__(self, size_max, filter_max = 300):
        self.max = size_max
        self.data = []
        self.cur = 0
        self.filter_max = filter_max
        for i in range(1,size_max+1):
            self.data.append(0)
            
    def append(self,x):
        if x >= self.filter_max:
            x = 0
        self.data[self.cur] = x
        self.cur = (self.cur+1) % self.max

    def getsum(self):
        """ Return a list of elements from the oldest to the newest. """
        return sum(self.data)


act_duration = 5000  # should stay on for 5 seconds
blink_duration = 750 # time for on or off
start_time = 0
led_on = False
led_time = 0
blink_on = False
leds.set_powersave(eco=True)
disp = display.open()
pressed = buttons.read(buttons.TOP_RIGHT)
gyro = bhi160.BHI160Gyroscope(sample_rate=10)
accel = bhi160.BHI160Accelerometer(sample_rate=10)


gyro_x = SumBuffer(10,200)
gyro_y = SumBuffer(10,200)
gyro_z = SumBuffer(10,200)
accel_x = SumBuffer(10,200)
accel_y = SumBuffer(10,200)
accel_z = SumBuffer(10,200)


def leds_on():
    vibra.vibrate(60)
    leds.set_all([[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0],[255,180,0]])
    disp.backlight(100)
    disp.clear(color.YELLOW)
    disp.update()
    
def leds_off():
    leds.set_all([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
    disp.clear(color.BLACK)
    disp.update()
    
while True:
    gyro_samples = gyro.read()
    if not gyro_samples:
        gyro_x.append(0)
        gyro_y.append(0)
        gyro_z.append(0)
    else:
        gyro_sample = gyro_samples[-1]
        gyro_x.append(gyro_sample.x)
        gyro_y.append(gyro_sample.y)
        gyro_z.append(gyro_sample.z)

    accel_samples = accel.read()
    if not accel_samples:
        accel_x.append(0)
        accel_y.append(0)
        accel_z.append(0)
    else:
        accel_sample = accel_samples[-1]
        accel_x.append(accel_sample.x)
        accel_y.append(accel_sample.y)
        accel_z.append(accel_sample.z)

    print(gyro_x.getsum(),gyro_y.getsum(),gyro_z.getsum(), accel_x.getsum(), accel_y.getsum(), accel_z.getsum())
    if gyro_x.getsum() < -500 and gyro_y.getsum() < -300 and accel_x.getsum() < -3:
        # ok we could have an activation
        start_time = utime.ticks_ms()
        led_time = start_time
        print("Blink activated")

    act_time = utime.ticks_ms()
    if act_time - start_time <= act_duration:
        # ok, we are blinking
        if not blink_on:
            leds_on()
            led_on = True
            blink_on = True
        else:
            if act_time - led_time > blink_duration:
                # we have to toggle led state
                led_time = act_time
                if led_on:
                    leds_off()
                    led_on = False
                else:
                    leds_on()
                    led_on = True
    else:
        if led_on:
            leds_off()
        blink_on = False
    utime.sleep_ms(10)

