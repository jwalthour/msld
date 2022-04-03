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
from nfl.data.data import Data as NflData
from nfl.data.scoreboard_config import ScoreboardConfig as NflScoreboardConfig
from nfl.renderer.main import MainRenderer as NflMainRenderer
from nfl.utils import add_nfl_args, add_rpi_display_args, led_matrix_options
from mcb.data.data import Data as McbData
from mcb.data.scoreboard_config import ScoreboardConfig as McbScoreboardConfig
from mcb.renderer.main import MainRenderer as McbMainRenderer

from input_listener import InputListener
import threading
from enum import Enum

from display import Display

logger = logging.getLogger(__name__)

BTN_NFL = 0
BTN_MCB = 1
BTN_BRIGHTER = 2
BTN_DIMMER = 3

ERROR_RETRY_S = 10

class DisplayMode(Enum):
    NFL = 'NFL'
    MLB = "MLB"
    MCB = "MCB"
    MENU = "Menu"
    NONE = 'None'

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

    cur_sport: DisplayMode = DisplayMode.NONE
    requested_mode: DisplayMode = DisplayMode.MCB

    # For some reason, we get a raspberry pi GPIO error
    # if this is initialized after the RGBMatrix.
    # Everything seems happy to coexist as long as this one's started first.
    input_listener = InputListener(args.stdio_btns)
    def btn_pressed(btn: int) -> None:
        """
        A button was pressed
        btn: int, [0,3], 0 is topmost button
        """
        global requested_mode
        if btn == BTN_NFL:
            requested_mode = DisplayMode.NFL
        elif btn == BTN_MCB:
            requested_mode = DisplayMode.MCB
        btn_event.set()
    def exit() -> None:
        exit_event.set()
        btn_event.set()
    input_listener.btn_cb = btn_pressed
    input_listener.exit_cb = exit
    
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
    mcb_renderer = McbMainRenderer(matrix, mcb_data)

    renderer_for_sport = {
        DisplayMode.NFL:nfl_renderer,
        DisplayMode.MCB:mcb_renderer,
    }
    menu_renderer = Menu()
    btn_event: threading.Event = threading.Event()
    exit_event: threading.Event = threading.Event()


    nfl_renderer.init()
    mcb_renderer.init()
    cur_renderer: Display = None
    while not exit_event.is_set():
        if requested_mode != cur_sport:
            logger.info("Changing sport from %r to %r."%(cur_sport, requested_mode))
            try:
                renderer_for_sport[requested_mode].retrieve_data()
                renderer_for_sport[requested_mode].init()
                cur_sport = requested_mode
                cur_renderer = renderer_for_sport[requested_mode]
            except:
                logger.error("Uncaught exception in renderer.init(): ", exc_info=True)

        try:
            delay = cur_renderer.retrieve_data()
        except:
            logger.error("Uncaught exception in renderer.retrieve_data(): ", exc_info=True)
            delay = ERROR_RETRY_S

        try:
            cur_renderer.render()
        except:
            logger.error("Uncaught exception in renderer.render(): ", exc_info=True)
            
        btn_event.wait(delay)
        if btn_event.is_set():
            btn_event.clear()
