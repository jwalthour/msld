#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Menu UI for selecting sport or other renderer
"""

from display import Display
from typing import Tuple
from enums import DisplayType, MenuButton


class Blank(Display):
    def init(self) -> None:
        """
        Prepare to loop (should be called every time this renderer is brought to the foreground)
        """
        pass

    def poll(self, button: MenuButton) -> Tuple[float, DisplayType]:
        """Retrieve data, make decisions about state

        Args:
            button (MenuButton): Button pressed since last poll - will be NONE most of the time

        Returns:
            Tuple[float, DisplayType]: 
                float: The number of seconds to wait before we'll have anything new to display, 
                DisplayType: the display type that should replace this one (or the same display type to remain here)
        """
        if button == MenuButton.A:
            return (0, DisplayType.MENU)
        else:
            return (1000000,DisplayType.BLANK)

    def render(self) -> None:
        """
        Draw to the matrix
        """
        pass
