#!/usr/bin/python3

from Alfred3 import AlfJson, Tools
from WindowManager import Window

dimensions = Tools.getArgv(1)
direction = Tools.getEnv("direction")
resize_factor = float(Tools.getEnv("resize_factor", 0.1))
move_steps = int(Tools.getEnv("move_steps", 80))

# Get window position from for frontmost app
Window = Window(dimensions)
x = Window.x_pos()
y = Window.y_pos()
width = Window.width()
height = Window.height()

# Size window up and down
if direction == "up_size" or direction == "down_size":
    resize_factor = resize_factor * -1 if direction == "down_size" else resize_factor
    width = width+width*resize_factor
    height = height+height*resize_factor
# Window bigger to the right
if direction == "right_size":
    width = width+width*resize_factor
# Window smaller to the left
if direction == "left_size":
    width = width - width*resize_factor
# Move Window left
if direction == "left":
    x = x-move_steps
# Move Window right
if direction == "right":
    x = x+move_steps
# Move Window up
if direction == "up":
    y = y-move_steps
# Move window down
if direction == "down":
    y = y+move_steps

vars = {
    "x": x,
    "y": y,
    "width": width,
    "height": height
}


aj = AlfJson()
aj.add_variables(vars)
aj.write_json()
