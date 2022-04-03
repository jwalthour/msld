#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Menu UI for selecting sport or other renderer
"""

from renderer import Renderer


class Menu(Renderer):
    def init(self) -> None:
        """
        Prepare to loop (should be called every time this renderer is brought to the foreground)
        """
        raise NotImplementedError

    def retrieve_data(self) -> float:
        """
        Poll server for data
        return how long to wait (in secsonds, after next render) before next reder/draw cycle
            if no button is pressed
        """
        raise NotImplementedError

    def render(self) -> None:
        """
        Draw to the matrix
        """
        raise NotImplementedError