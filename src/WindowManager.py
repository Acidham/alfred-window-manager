#!/usr/bin/python3

import json
import os


class Dimensions(object):

    def __init__(self, file: str) -> None:
        """
        Handles dimension.json file storage

        Args:

            file (str): path to .json

        """
        self.file = file

    def add_dimension(self, app_id: str, dim: dict) -> None:
        """
        Add dimension app setting

        Args:

            app_id (str): Bundle ID of the app
            dim (dict): Dimension Dictonary

        """
        jsn = dict()
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                jsn: dict = json.load(f)
            jsn.pop(app_id, False)
        jsn[app_id] = dim
        self._save_json_file(jsn)

    def get_dimension(self, app_id: str) -> dict:
        """
        get dimension for an app id

        Args:

            app_id (str): app bundle id


        Returns:

            dict: _description_

        """
        jsn = self._read_json_file()
        dimension = jsn.get(app_id, None)
        return dimension

    def delete_dimension(self, app_id: str) -> None:
        """
        Delete a dimension for an app id

        Args:

            app_id (str): _description_

        """
        jsn = self._read_json_file()
        jsn.pop(app_id, False)
        self._save_json_file(jsn)

    def _file_check(self, file: str) -> str:
        if not os.path.exists(file):
            with open(file, "w") as f:
                pass
        return file

    def _read_json_file(self) -> dict:
        jsn = dict()
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                jsn: dict = json.load(f)
        return jsn

    def _save_json_file(self, jsn: dict) -> None:
        with open(self.file, "w") as f:
            f.seek(0)
            json.dump(jsn, f)
            f.truncate()


class Window(object):

    def __init__(self, dim: str()) -> None:
        self.dimension = json.loads(dim)

    def x_pos(self) -> int:
        return int(self.dimension.get('x', None))

    def y_pos(self) -> int:
        return int(self.dimension.get('y', None))

    def width(self) -> int:
        return int(self.dimension.get('width', None))

    def height(self) -> int:
        return int(self.dimension.get('height', None))

    def get_dimensions(self) -> dict:
        return self.dimension


class Screen(object):

    def __init__(self) -> None:
        self.screen_res = self._sys_profiler()

    def screen_width(self) -> int:
        return self.screen_res[0]

    def screen_height(self) -> int:
        return self.screen_res[1]

    def _sys_profiler(self) -> tuple:
        sysinfo: dict = json.loads(os.popen("system_profiler SPDisplaysDataType -json").read())
        screen_dimensions = sysinfo.get('SPDisplaysDataType')[0].get('spdisplays_ndrvs')[0].get('_spdisplays_resolution')
        res, freq = screen_dimensions.split(" @ ")
        screen_width, screen_height = res.split(" x ")
        return (int(screen_width), int(screen_height))
