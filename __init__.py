import sys
import leds
import display
import vibra
import utime
import buttons
import color
import bhi160
sys.path.append("/apps/blinker/")
import ThreeAxisBuffer

# some constants DO NOT CHANGE
GT = 1  # greater than >
LT = 0  # less than <
DC = -1  # don't care

# play with parameters here (could go also to json)
sumtime = 600 # time in ms to sum up
looptime = 10 # time in ms to wait in the recognition loop
blink_duration = 750 # time for on or off
act_duration = 4 * blink_duration  # should stay on for 5 seconds

# the more mathematical parameters
gyro_x_max = 200 # do not record values beyond that (in + and -)
gyro_y_max = gyro_x_max
gyro_z_max = gyro_x_max

accel_x_max = 2 # do not record values beyond that (in + and -)
accel_y_max = accel_x_max
accel_z_max = accel_x_max

# the comparison parameters (play with the output to find out)
gyro_x_comp = LT  # the comparator (see below)
gyro_x_trig = -270  # the trigger value
gyro_y_comp = DC  # the comparator (see below)
gyro_y_trig = 0  # the trigger value
gyro_z_comp = DC  # the comparator (see below)
gyro_z_trig = 0  # the trigger value

accel_x_comp = DC
accel_x_trig = 0
accel_y_comp = GT
accel_y_trig = 7
accel_z_comp = DC
accel_z_trig = 0

# internal variables - do not change
start_time = 0
led_on = False
led_time = 0
blink_on = False
leds.set_powersave(eco=True)
disp = display.open()
pressed = buttons.read(buttons.TOP_RIGHT)
gyrodev = bhi160.BHI160Gyroscope(sample_rate=10)
acceldev = bhi160.BHI160Accelerometer(sample_rate=10)
gyro_str_format = "% 6d"
accel_str_format = "% 6.1f"
gyro_str = ""
accel_str = ""
act_gyro_str = ""
act_accel_str = ""

bufferdepth = int(sumtime / looptime)
gyro = ThreeAxisBuffer.ThreeAxisBuffer(bufferdepth,gyro_x_max, gyro_y_max, gyro_z_max)
accel = ThreeAxisBuffer.ThreeAxisBuffer(bufferdepth,accel_x_max, accel_y_max, accel_z_max)

null_sample = ThreeAxisBuffer.ThreeAxis(0,0,0)

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


# this is the main loop
while True:
    utime.sleep_ms(looptime)
    gyro_samples = gyrodev.read()
    if not gyro_samples:
        gyro.append(null_sample)
    else:
        gyro_sample = gyro_samples[-1]
        gyro.append(gyro_sample)

    accel_samples = acceldev.read()
    if not accel_samples:
        accel.append(null_sample)
    else:
        accel_sample = accel_samples[-1]
        accel.append(accel_sample)

    gyro_str = gyro.getstr(gyro_str_format)
    accel_str = accel.getstr(accel_str_format)
    print(gyro_str,accel_str)
    if gyro.compare_sum(gyro_x_comp, gyro_x_trig, gyro_y_comp, gyro_y_trig, gyro_z_comp, gyro_z_trig) \
            and accel.compare_sum(accel_x_comp, accel_x_trig,accel_y_comp, accel_y_trig,accel_z_comp, accel_z_trig):
        # ok we could have an activation
        act_gyro_str = gyro_str
        act_accel_str = accel_str
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
        if blink_on:
            if led_on:
                leds_off()
            # now display the last activation vector
            if act_gyro_str != "":
                disp.print(act_gyro_str[0:6],fg=color.YELLOW,font=display.FONT16,posx=2,posy=2)
                disp.print(act_gyro_str[7:13],fg=color.YELLOW,font=display.FONT16,posx=2,posy=24)
                disp.print(act_gyro_str[14:20],fg=color.YELLOW,font=display.FONT16,posx=2,posy=46)
            if act_accel_str != "":
                disp.print(act_accel_str[0:6],fg=color.RED, font=display.FONT16,posx=85,posy=2)
                disp.print(act_accel_str[7:13],fg=color.RED, font=display.FONT16,posx=85,posy=24)
                disp.print(act_accel_str[14:20],fg=color.RED, font=display.FONT16,posx=85,posy=46)
            disp.update()
            blink_on = False

