#!/usr/bin/python3

import os

from Alfred3 import AlfJson, Tools
from WindowManager import Dimensions, Screen, Window


def get_dock_position() -> str:
    return os.popen('defaults read com.apple.dock orientation').read().strip()


def get_dock_size() -> int:
    ts = int(os.popen('defaults read com.apple.dock tilesize').read().strip())
    autohide = int(os.popen('defaults read com.apple.dock autohide').read().strip())
    return int((ts+20)/2) if autohide == 0 else 0


cache_dir = Tools.getCacheDir()
cache_file = os.path.join(cache_dir, "dimensions.json")
Tools.log(f"Cache File: {cache_file}")
app_id = Tools.getEnv("app_id")
Tools.log(f"App ID: {app_id}")


window_postion = Tools.getArgv(1)
# window_postion = '{"x":521,"y":404,"width":1073,"height":565}'  # uncomment for testing
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

dock_position = get_dock_position()
dock_size = get_dock_size()

# Calculate new Window dimensions based on window move direction and Dock position
window_x_new = 0
window_y_new = 0
if direction == "left":  # calculate dimensions for moving right side of the screen
    window_width_new = int(screen_width/2)
    window_height_new = screen_height
    if dock_position == "left":
        window_x_new = dock_size
        window_width_new -= 2 * dock_size

if direction == "right":  # calculate dimensions for moving  right side of the screen
    window_x_new = int(screen_width/2)
    window_width_new = int(screen_width/2)
    window_height_new = int(screen_height)
    if dock_position == "right":
        window_x_new = screen_width - dock_size
        window_width_new -= - 2 * dock_size

vars = {"x": window_x_new,
        "y": window_y_new,
        "width": window_width_new,
        "height": window_height_new
        }
aj = AlfJson()
aj.add_variables(vars)
aj.write_json()
