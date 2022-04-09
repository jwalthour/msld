#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Multi-sport LED Display entry point
"""

import argparse
import time
import logging
from rgbmatrix import RGBMatrix
from menu.menu import Menu
from misc_displays.blank import Blank
from nfl.data.data import Data as NflData
from nfl.data.scoreboard_config import ScoreboardConfig as NflScoreboardConfig
from nfl.renderer.main import MainRenderer as NflMainRenderer
from nfl.utils import add_nfl_args, add_rpi_display_args, led_matrix_options
from mcb.data.data import Data as McbData
from mcb.data.scoreboard_config import ScoreboardConfig as McbScoreboardConfig
from mcb.renderer.main import MainRenderer as McbMainRenderer
from enums import DisplayType, MenuButton
from input_listener import InputListener
import threading

from display import Display

logger = logging.getLogger(__name__)

ERROR_RETRY_S = 10


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)#, datefmt="%H:%M:%S")#, format=" %(levelname)-8s %(asctime)s %(message)s")
    logging.getLogger('mcb.data.data').setLevel(logging.DEBUG)
    logging.getLogger('input_listener').setLevel(logging.DEBUG)
    # Get supplied command line arguments
    parser = argparse.ArgumentParser()
    add_rpi_display_args(parser)
    add_nfl_args(parser)
    parser.add_argument('--stdio-btns', action='store_true')
    args = parser.parse_args()

    cur_type: DisplayType = DisplayType.BLANK
    requested_type: DisplayType = DisplayType.MCB

    # For some reason, we get a raspberry pi GPIO error
    # if this is initialized after the RGBMatrix.
    # Everything seems happy to coexist as long as this one's started first.
    input_listener = InputListener(args.stdio_btns)
    def button_pressed(button: int) -> None:
        """
        A button was pressed
        btn: int, [0,3], 0 is topmost button
        """
        global requested_type
        if button == MenuButton.A:
            requested_type = DisplayType.NFL
        elif button == MenuButton.B:
            requested_type = DisplayType.MCB
        button_event.set()
    def exit() -> None:
        exit_event.set()
        button_event.set()
    input_listener.button_callback = button_pressed
    input_listener.exit_callback = exit
    
    # Check for led configuration arguments
    matrixOptions = led_matrix_options(args)

    # Initialize the matrix
    matrix = RGBMatrix(options = matrixOptions)
    # Initialize NFL
    nfl_config = NflScoreboardConfig("../nfl_config", args)
    nfl_data = NflData(nfl_config)
    nfl_renderer = NflMainRenderer(matrix, nfl_data)
    # Initialize Mens College Basketball
    mcb_config = McbScoreboardConfig("../mcb_config", args)
    mcb_data = McbData(mcb_config)
    mcb = McbMainRenderer(matrix, mcb_data)
    menu = Menu()
    blank = Blank()

    display = {
        DisplayType.NFL:nfl_renderer,
        DisplayType.MCB:mcb,
        DisplayType.MENU:menu,
        DisplayType.BLANK:blank,
    }
    button_event: threading.Event = threading.Event()
    exit_event: threading.Event = threading.Event()

    for key,disp in display.items():
        disp.init()

    while not exit_event.is_set():
        if requested_type != cur_type:
            logger.info("Changing sport from %r to %r."%(cur_type, requested_type))
            try:
                display[requested_type].poll()
                display[requested_type].init()
                cur_type = requested_type
            except:
                logger.error("Uncaught exception in renderer.init(): ", exc_info=True)

        try:
            delay = display[cur_type].poll()
        except:
            logger.error("Uncaught exception in renderer.poll(): ", exc_info=True)
            delay = ERROR_RETRY_S

        try:
            display[cur_type].render()
        except:
            logger.error("Uncaught exception in renderer.render(): ", exc_info=True)
            
        button_event.wait(delay)
        if button_event.is_set():
            button_event.clear()
