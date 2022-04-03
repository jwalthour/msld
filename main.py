#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Multi-sport LED Display entry point
"""

import argparse
import time
import logging
from rgbmatrix import RGBMatrix
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

logger = logging.getLogger(__name__)

BTN_NFL = 0
BTN_MCB = 1
BTN_BRIGHTER = 2
BTN_DIMMER = 3

ERROR_RETRY_S = 10

class Sport(Enum):
    NFL = 'NFL'
    MLB = "MLB"
    MCB = "MCB"
    NONE = 'None'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format=" %(levelname)-8s %(asctime)s %(message)s")
    logging.getLogger('mcb.data.data').setLevel(logging.DEBUG)
    logging.getLogger('input_listener').setLevel(logging.DEBUG)
    # Get supplied command line arguments
    parser = argparse.ArgumentParser()
    add_rpi_display_args(parser)
    add_nfl_args(parser)
    parser.add_argument('--stdio-btns', action='store_true')
    args = parser.parse_args()

    cur_sport: Sport = Sport.NONE
    requested_sport: Sport = Sport.MCB

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
        elif btn == BTN_MCB:
            requested_sport = Sport.MCB
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

    renderers = {
        Sport.NFL:nfl_renderer,
        Sport.MCB:mcb_renderer,
    }

    btn_event: threading.Event = threading.Event()
    exit_event: threading.Event = threading.Event()


    nfl_renderer.init()
    mcb_renderer.init()
    while not exit_event.is_set():
        if requested_sport != cur_sport:
            logger.info("Changing sport from %r to %r."%(cur_sport, requested_sport))
            try:
                renderers[requested_sport].retrieve_data()
                renderers[requested_sport].init()
                cur_sport = requested_sport
            except:
                logger.error("Uncaught exception in renderer.init(): ", exc_info=True)

        try:
            delay = renderers[cur_sport].retrieve_data()
        except:
            logger.error("Uncaught exception in renderer.retrieve_data(): ", exc_info=True)
            delay = ERROR_RETRY_S

        try:
            renderers[cur_sport].render()
        except:
            logger.error("Uncaught exception in renderer.render(): ", exc_info=True)
            
        btn_event.wait(delay)
        if btn_event.is_set():
            btn_event.clear()
