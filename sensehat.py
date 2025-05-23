from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from signal import pause
from datetime import datetime
import os
import requests
import time

SITE = "http://127.0.0.1:8000/post_data/"

## LED array data ##

S = [153, 217, 234]
O = [0, 0, 0]
H = [255, 0, 0]
Y = [255, 255, 51]
R = [255, 0, 0]
N = [255, 128, 51]
B = [26, 26, 26]
P = [255, 163, 177]

snowflake = [
    O, O, S, O, S, O, O, O,
    O, O, O, S, O, O, O, O,
    S, O, S, S, S, O, S, O,
    O, S, S, O, S, S, O, O,
    S, O, S, S, S, O, S, O,
    O, O, O, S, O, O, O, O,
    O, O, S, O, S, O, O, O,
    O, O, O, O, O, O, O, O,
    ]

flame = [
    O, O, O, O, O, R, O, O,
    O, O, O, O, O, R, O, O,
    O, O, R, O, R, R, O, O,
    O, O, R, R, R, R, O, R,
    R, O, R, N, Y, R, R, R,
    R, R, R, N, Y, N, R, R,
    R, R, N, N, Y, Y, N, R,
    R, R, N, Y, Y, Y, N, R,
    ]

happy = [
    O, O, Y, Y, Y, O, O, O,
    Y, Y, Y, Y, Y, Y, Y, O,
    Y, Y, B, Y, B, Y, Y, O,
    R, Y, Y, R, Y, Y, R, O,
    Y, B, Y, Y, Y, B, Y, O,
    Y, Y, B, B, B, Y, Y, O,
    Y, Y, Y, Y, Y, Y, Y, O,
    O, O, O, O, O, O, O, O,
    ]

COLD = 22
HOT = 33
    
def calculate_heat_index(temperature, humidity):
    """
    Calculate the heat index given the temperature (in Fahrenheit) and relative humidity (in percentage).

    :param temperature: Temperature in degrees Fahrenheit
    :param humidity: Relative humidity in percentage
    :return: Heat index in degrees Fahrenheit
    """
    
    # Convert temp to F:
    temperature = temperature * 9/5 + 32
    
    if temperature < 80 or humidity < 40:
        # convert back to celcius
        temperature = (temperature - 32) * 5/9
        return round(temperature, 2)

    # Constants for the heat index formula
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -0.00683783
    c6 = -0.05481717
    c7 = 0.00122874
    c8 = 0.00085282
    c9 = -0.00000199

    # Calculate heat index
    heat_index = (c1 + (c2 * temperature) + (c3 * humidity) + (c4 * temperature * humidity) +
                  (c5 * temperature**2) + (c6 * humidity**2) + (c7 * temperature**2 * humidity) +
                  (c8 * temperature * humidity**2) + (c9 * temperature**2 * humidity**2))

    # Convert back to celcius
    heat_index = (heat_index - 32) * 5/9
    return round(heat_index, 2)

def draw_screen(hi):
    
    if screen_on:
        if hi < COLD:
            sense.set_pixels(snowflake)
        
        elif hi > HOT: 
            sense.set_pixels(flame)
        
        else:
            sense.set_pixels(happy)
    

def get_sense_data():

    temp = sense.get_temperature()
    humi = sense.get_humidity()
    pressure = sense.get_pressure()
    hi = calculate_heat_index(temp, humi)
    
    # Round the values for display
    temp = round(temp, 2)
    humi = round(humi, 2)
    pressure = round(pressure, 2)
    hi = round(hi, 2)
    
    return [temp, humi, hi, pressure]
    
def control_led_brigthness(clear):
    
    if clear < 50:
        sense.low_light=True
    else:
        sense.low_light=False
        
def pushed_up(event):
    global screen_on
    if event.action != ACTION_RELEASED and screen_on:
        sense.clear()  # turn off the screen
        sense.show_message("Off", scroll_speed=0.03) # display "OFF" message
        screen_on = False
    elif event.action != ACTION_RELEASED and (not screen_on):
        sense.show_message("On", scroll_speed=0.03)
        screen_on = True
    
def refresh():
    get_sense_data()
    
def send_data():
    """ Sends measurement data to the monitor website as a get request. The monitor
    site is only responsible for displaying the data, and so it will receive
    measurements fairly continuously """
    measurement = {'temperature': temp,
            'humidity': humi,
            'heat_index': hi,
            'pressure':pressure,
            'time':datetime.now(),
            'sensor':'Sensehat'
            }
    r = requests.get(SITE, params=measurement)
   
   
##### Main Program #####

   
sense = SenseHat()
prev_min = datetime.now().minute

sense.color.gain = 64
sense.color.integration_cycles = 256
screen_on = True  
        
while True:
    ######## Sensor data ###########

    # Get temperature and humidity information.
    sense_data = get_sense_data()
    temp = sense_data[0]
    humi = sense_data[1]
    hi = sense_data[2]
    pressure = sense_data[3]

    # Only record data once per minute
    min_now = datetime.now().minute
    if min_now != prev_min:
        try:
            send_data()
        except:
            print("server not found")
        prev_min = min_now

    ########## Screen ###########
    # Change image according to sensedata
    draw_screen(hi)
    # Pause for integrating light values
    time.sleep(3 * sense.colour.integration_time)
    # Get brightness from enviornment.
    red, green, blue, clear = sense.colour.colour
    control_led_brigthness(clear)

    # Read if stick has been pressed to turn screen on or off.
    sense.stick.direction_up = pushed_up
    sense.stick.direction_any = refresh
    refresh()


    


