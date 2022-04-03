#!/usr/bin/python3
# -*- coding: utf-8 -*-
import abc

class Display(abc.ABC):
    @abc.abstractmethod
    def init(self) -> None:
        """
        Prepare to loop (should be called every time this renderer is brought to the foreground)
        """
        raise NotImplementedError
    @abc.abstractmethod
    def poll(self) -> float:
        """
        Poll server for data
        return how long to wait (in secsonds, after next render) before next reder/draw cycle
            if no button is pressed
        """
        raise NotImplementedError
    @abc.abstractmethod
    def render(self) -> None:
        """
        Draw to the matrix
        """
        raise NotImplementedError