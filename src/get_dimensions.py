#!/usr/bin/python3

import json
import os

from Alfred3 import AlfJson, Tools
from WindowManager import Dimensions

cache_dir = Tools.getCacheDir()
cache_file = os.path.join(cache_dir, "dimensions.json")

app_id = Tools.getArgv(1)  # get app id from previous wf step

Dim = Dimensions(cache_file)
vars = Dim.get_dimension(app_id)

if vars == None:
    vars = json.loads('{"x":521,"y":404,"width":1073,"height":565}')  # fallback

aj = AlfJson()
aj.add_variables(vars)
aj.write_json()
