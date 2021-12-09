#!/usr/bin/python3
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

def rising_edge(channel):
    print("Rising edge: %r"%channel)

def falling_edge(channel):
    print("Falling edge: %r"%channel)



bcm_pin_for_btn = [17, 22, 23, 24]
for pin in bcm_pin_for_btn:
    GPIO.setup(pin, GPIO.IN)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=rising_edge)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=falling_edge)
