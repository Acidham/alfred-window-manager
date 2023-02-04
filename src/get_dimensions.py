#!/usr/bin/python3

import json
import os

from Alfred3 import AlfJson, Tools
from WindowManager import Dimensions

cache_dir = Tools.getCacheDir()
cache_file = os.path.join(cache_dir, "dimensions.json")

app_id = Tools.getEnv('app_id')  # get app id from previous wf step
post_action = Tools.getArgv(1)  # post action e.g 'delete' from prev step
delete_entry = True if post_action == 'delete' else False

Dim = Dimensions(cache_file)
# read dimensionsn and delte the entry when post action == delete
vars = Dim.get_dimension(app_id, delete=delete_entry)

if vars == None or vars == {}:
    vars = json.loads('{"x":521,"y":404,"width":1073,"height":565}')  # fallback dimensions

aj = AlfJson()
aj.add_variables(vars)
aj.write_json()
