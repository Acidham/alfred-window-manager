#!/usr/bin/python3

import json
import os

from Alfred3 import AlfJson, Tools
from WindowManager import Dimensions

cache_dir = Tools.getCacheDir()  # get cache director
cache_file = os.path.join(cache_dir, "dimensions.json")  # get dimesion file


app_id = Tools.getEnv('app_id')  # get app id from previous wf step
post_action = Tools.getArgv(1)  # post action e.g 'delete' from prev step
reset_prev_action = True if post_action == 'delete' else False

# Get default settings from Workflow configuration
default_x = Tools.getEnv('default_x')
default_width = Tools.getEnv('default_width')
default_y = Tools.getEnv('default_y')
default_height = Tools.getEnv('default_height')

# Establish communication to dimension cache file
Dim = Dimensions(cache_file)
# read dimensionsn and delte the entry when post action == delete
vars = Dim.get_dimension(app_id, reset=reset_prev_action)

# fallback dimensions
if vars == None or vars == {}:
    fallback_dim = {
        "x": default_x,
        "y": default_height,
        "width": default_width,
        "height": default_height,
        "prev_action": ""
    }
    vars = fallback_dim
Tools.log(json.dumps(vars))

aj = AlfJson()
aj.add_variables(vars)
aj.write_json()
