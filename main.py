#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Multi-sport LED Display entry point
"""

import argparse
import time
import logging
from rgbmatrix import RGBMatrix
from nfl.data.data import Data
from nfl.data.scoreboard_config import ScoreboardConfig as NflScoreboardConfig
from nfl.renderer.main import MainRenderer as NflMainRenderer
from nfl.utils import add_nfl_args, add_rpi_display_args, led_matrix_options
from input_listener import InputListener
import threading
from enum import Enum

logger = logging.getLogger(__name__)

BTN_NFL = 0
BTN_MLB = 1
BTN_BRIGHTER = 2
BTN_DIMMER = 3

class Sport(Enum):
    NFL = 'NFL'
    MLB = "MLB"
    NONE = 'None'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format=" %(levelname)-8s %(asctime)s %(message)s")

    # Get supplied command line arguments
    parser = argparse.ArgumentParser()
    add_rpi_display_args(parser)
    add_nfl_args(parser)
    parser.add_argument('--stdio-btns', action='store_true')
    args = parser.parse_args()

    cur_sport: Sport = Sport.NONE
    requested_sport: Sport = Sport.NFL

    # For some reason, we get a raspberry pi GPIO error
    # if this is initialized after the RGBMatrix.
    # Everything seems happy to coexist as long as this one's started first.
    input_listener = InputListener(args.stdio_btns)
    def btn_pressed(btn: int) -> None:
        """
        A button was pressed
        btn: int, [0,3], 0 is topmost button
        """
        global requested_sport
        if btn == BTN_NFL:
            requested_sport = Sport.NFL
        elif btn == BTN_MLB:
            requested_sport = Sport.MLB
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
    nfl_data = Data(nfl_config)
    nfl_renderer = NflMainRenderer(matrix, nfl_data)

    renderers = {
        Sport.NFL:nfl_renderer
    }

    btn_event: threading.Event = threading.Event()
    exit_event: threading.Event = threading.Event()


    nfl_renderer.init()
    while not exit_event.is_set():
        if requested_sport != cur_sport:
            logger.info("Changing sport from %r to %r."%(cur_sport, requested_sport))
            renderers[requested_sport].init()
            cur_sport = requested_sport

        delay = renderers[cur_sport].retrieve_data()
        renderers[cur_sport].render()
        btn_event.wait(delay)
        if btn_event.is_set():
            btn_event.clear()
