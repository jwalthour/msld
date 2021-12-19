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
from nfl.data.scoreboard_config import ScoreboardConfig
from nfl.renderer.main import MainRenderer

from nfl.utils import add_nfl_args, add_rpi_display_args, led_matrix_options


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format=" %(levelname)-8s %(asctime)s %(message)s")

    # Get supplied command line arguments
    parser = argparse.ArgumentParser()
    add_rpi_display_args(parser)
    add_nfl_args(parser)
    args = parser.parse_args()

    # Check for led configuration arguments
    matrixOptions = led_matrix_options(args)

    # Initialize the matrix
    matrix = RGBMatrix(options = matrixOptions)

    cur_sport = 'none'
    requested_sport = 'nfl'

    # Initialize NFL
    nfl_config = ScoreboardConfig("../nfl_config", args)
    nfl_data = Data(nfl_config)
    nfl_renderer = MainRenderer(matrix, nfl_data)

    renderers = {
        'nfl':nfl_renderer
    }

    nfl_renderer.init()
    while True:
        delay = nfl_renderer.retrieve_data()
        nfl_renderer.render()
        time.sleep(delay)
