#!/usr/bin/python3
# -*- coding: utf-8 -*-
import abc
from typing import Tuple
from enums import DisplayType, MenuButton

class Display(abc.ABC):
    @abc.abstractmethod
    def init(self) -> None:
        """
        Prepare to loop (should be called every time this renderer is brought to the foreground)
        """
        raise NotImplementedError
    @abc.abstractmethod
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
    @abc.abstractmethod
    def render(self) -> None:
        """
        Draw to the matrix
        """
        raise NotImplementedError