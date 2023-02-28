#!/usr/bin/python3

import json
import os

from Alfred3 import Tools
from WindowManager import Dimensions

# Following actions are will ignore save_dimension command
IGNORE_PREV_ACTIONS = (
    'left',
    'right',
    'maximize',
    'center_two_thirds',
    'left_third',
    'center_third',
    'right_third'
)

app_id = Tools.getEnv('app_id')
direction = Tools.getEnv('direction')
window_dimensions = json.loads(Tools.getArgv(1))
cache_file = os.path.join(Tools.getCacheDir(), "dimensions.json")
Tools.log(f"Cache file: {cache_file}")

# Estbalish communication to dimension cache file
Dim = Dimensions(cache_file)
# get the dimension from prev action
pre_dim = Dim.get_dimension(app_id)
prev_action = pre_dim.get('prev_action', None)

if prev_action not in IGNORE_PREV_ACTIONS:  # Save only when previous action is not part of ignored action
    Dim.save_dimension(app_id, window_dimensions, prev_action=direction)
