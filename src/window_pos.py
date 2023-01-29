#!/usr/bin/python3

import json
import os
import sys

from Alfred3 import AlfJson, Tools
from WindowManager import Dimensions, Screen, Window

cache_dir = Tools.getCacheDir()
cache_file = os.path.join(cache_dir, "dimensions.json")
Tools.log(f"Cache File: {cache_file}")
app_id = Tools.getEnv("app_id")
Tools.log(f"App ID: {app_id}")


window_postion = Tools.getArgv(1)
direction = Tools.getEnv("direction")

# Get Window positions of Frontmost app
Win = Window(window_postion)
actual_window_pos = Win.get_dimensions()
window_x = Win.x_pos()
window_y = Win.y_pos()
window_width = Win.width()
windov_height = Win.height()

# Persist Dimensions for frontmost app for reset
Dim = Dimensions(cache_file)
Dim.add_dimension(app_id, actual_window_pos)

# Get Screen width and height
Scr = Screen()
screen_width = Scr.screen_width()
screen_height = Scr.screen_height()

if direction == "left":  # calculate dimensions for moving  right side of the screen
    window_x_new = 10
    window_y_new = 10
    window_width_new = int(screen_width/2) - 60
    window_height_new = int(screen_height)
if direction == "right":  # calculate dimensions for moving  right side of the screen
    window_x_new = int(screen_width/2)
    window_y_new = 10
    window_width_new = int(screen_width/2)
    window_height_new = int(screen_height)

vars = {"x": window_x_new,
        "y": window_y_new,
        "width": window_width_new,
        "height": window_height_new
        }
aj = AlfJson()
aj.add_variables(vars)
aj.write_json()
