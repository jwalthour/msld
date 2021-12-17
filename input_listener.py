#!/usr/bin/python
import RPi.GPIO as GPIO
import readchar
import time

GPIO.setmode(GPIO.BCM)

bcm_pin_for_btn = [14,15,25,19]
char_for_btn = ['a','s','d','f']

def falling_edge(channel):
    print("Falling edge: %r"%channel)
    if channel in char_for_btn:
        btn = bcm_pin_for_btn.index(channel)


for pin in bcm_pin_for_btn:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.add_event_detect(pin, GPIO.RISING, callback=rising_edge)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=falling_edge)

print("Listening for keys")
while True:
    input_char = readchar.readchar()
    if input_char in char_for_btn:
        btn = char_for_btn.index(input_char)
        print("Got button %d"%btn)
    elif input_char == '\x03':
        print("^C")
        break
    elif input_char == '\x1a':
        print("^Z")
        break
    else:
        print("Char %r isn't a button."%input_char)
