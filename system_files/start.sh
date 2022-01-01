#!/bin/bash
cd /mnt/source/msld
sudo python main.py --led-gpio-mapping=adafruit-hat-pwm --led-rows 32 --led-cols 64 --led-slowdown-gpio=2 --led-row-addr-type 0 --led-brightness=50
