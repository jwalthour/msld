#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Menu UI for selecting sport or other renderer
"""

from display import Display
from typing import Tuple
from enums import DisplayType, MenuButton
from PIL import Image, ImageFont, ImageDraw, ImageSequence
import rgbmatrix
from mcb.utils import center_text, get_file


class Menu(Display):
    matrix: rgbmatrix.RGBMatrix = None

    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype(get_file("fonts/score_large.otf"), 16)
        self.font_mini = ImageFont.truetype(get_file("fonts/04B_24__.TTF"), 8)

    def init(self) -> None:
        """
        Prepare to loop (should be called every time this renderer is brought to the foreground)
        """
        raise NotImplementedError

    def poll(self, button: MenuButton) -> Tuple[float, DisplayType]:
        """Retrieve data, make decisions about state

        Args:
            button (MenuButton): Button pressed since last poll - will be NONE most of the time

        Returns:
            Tuple[float, DisplayType]: 
                float: The number of seconds to wait before we'll have anything new to display, 
                DisplayType: the display type that should replace this one (or the same display type to remain here)
        """
        raise NotImplementedError

    def render(self) -> None:
        """
        Draw to the matrix
        """
        raise NotImplementedError