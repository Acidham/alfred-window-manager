#!/usr/bin/python3

import os

from Alfred3 import Tools
from WindowManager import Dimensions
import json

app_id = Tools.getEnv('app_id')
window_dimensions = json.loads(Tools.getArgv(1))
cache_file = os.path.join(Tools.getCacheDir(), "dimensions.json")

Dim = Dimensions(cache_file)
Dim.add_dimension(app_id, window_dimensions)
