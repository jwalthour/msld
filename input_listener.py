#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import typing
import RPi.GPIO as GPIO
import readchar
import threading
import logging
logger = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)

BCM_PIN_FOR_BTN = [14,15,25,19]
CHAR_FOR_BTN = ['a','s','d','f']


class InputListener():
    """
    Class that listens for either keystrokes on stdin or physical button presses,
    and reports either as a callback
    """
    _kt: threading.Thread = None
    exit_cb:typing.Callable[[],None] = None
    btn_cb:typing.Callable[[int], None] = None

    def __init__(self, listen_to_stdio: bool = False) -> None:
        for pin in BCM_PIN_FOR_BTN:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self._falling_edge)
        if listen_to_stdio:
            self._kt = threading.Thread(target=self._key_listener_thread, daemon=True)
            self._kt.start()

    def _key_listener_thread(self):
        logger.info("Listening for keys")
        while True:
            input_char = readchar.readchar()
            if input_char in CHAR_FOR_BTN:
                btn = CHAR_FOR_BTN.index(input_char)
                logger.debug("Got button %d"%btn)
                if self.btn_cb != None:
                    self.btn_cb(btn)
            elif input_char == '\x03':
                logger.debug("^C")
                break
            elif input_char == '\x1a':
                logger.debug("^Z")
                break
            else:
                logger.debug("Char %r isn't a button."%input_char)
        if self.exit_cb != None:
            self.exit_cb()

    def _falling_edge(self, channel):
        logger.debug("Falling edge: %r"%channel)
        if channel in BCM_PIN_FOR_BTN:
            btn = BCM_PIN_FOR_BTN.index(channel)
            if self.btn_cb != None:
                self.btn_cb(btn)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    il = InputListener()

    run = True
    def ex():
        global run
        logger.info("Exiting")
        run = False

    def btn(btn: int):
        logger.info("Got button: %d"%btn)

    il.btn_cb = btn
    il.exit_cb = ex

    while run:
        time.sleep(.1)