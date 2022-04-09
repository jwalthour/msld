#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum


class DisplayType(Enum):
    NFL = 'NFL'
    MLB = "MLB"
    MCB = "MCB"
    MENU = "Menu"
    BLANK = 'None'

class MenuButton(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    NONE = 4