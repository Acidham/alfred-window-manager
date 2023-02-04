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
        self.file = self._check_file(file)

    def _check_file(self, file):
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)
        return file

    def add_dimension(self, app_id: str, dim: dict, prev_action: str = '') -> None:
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
        dim.update({'prev_action': prev_action})
        jsn[app_id] = dim
        self._save_json_file(jsn)

    def get_dimension(self, app_id: str, delete: bool = False) -> dict:
        """
        get dimension for an app id

        Args:

            app_id (str): app bundle id


        Returns:

            dict: _description_

        """
        jsn = self._read_json_file()
        dimension = jsn.get(app_id, {})
        if delete:
            # self.delete_dimension(app_id)
            dimension['prev_action'] = ""
            self.add_dimension(app_id, dimension)
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

    def _read_json_file(self) -> dict:
        """
        Read json file

        Returns:

            dict: json of the file

        """
        jsn = dict()
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                jsn: dict = json.load(f)
        return jsn

    def _save_json_file(self, jsn: dict) -> None:
        """
        Save the json to a file

        Args:

            jsn (dict): json with dimensions

        """
        with open(self.file, "w") as f:
            f.seek(0)
            json.dump(jsn, f)
            f.truncate()


class Window(object):

    def __init__(self, dim: str()) -> None:
        self.dimension = json.loads(dim)

    def x_pos(self) -> int:
        """
        Get x position of the window from a str represenation of a dimension

        Returns:

            int: x postition

        """
        return int(self.dimension.get('x', None))

    def y_pos(self) -> int:
        """
        Get y position of the window from a str represenation of a dimension

        Returns:

            int: y postition

        """
        return int(self.dimension.get('y', None))

    def width(self) -> int:
        """
        Get width of the window from a str represenation of a dimension

        Returns:

            int: window width

        """
        return int(self.dimension.get('width', None))

    def height(self) -> int:
        """
        Get height of the window from a str represenation of a dimension

        Returns:

            int: window height

        """
        return int(self.dimension.get('height', None))

    def get_dimensions(self) -> dict:
        """
        Get dimension from dimension provided as string

        Returns:

            int: dimension

        """
        return self.dimension


class Screen(object):

    def __init__(self) -> None:
        self.screen_res = self._sys_profiler()

    def screen_width(self) -> int:
        """
        Get screen width

        Returns:

            int: screen width

        """
        return self.screen_res[0]

    def screen_height(self) -> int:
        """
        Get Screen height

        Returns:

            int: screen height

        """
        return self.screen_res[1]

    def _sys_profiler(self) -> tuple:
        sysinfo: dict = json.loads(os.popen("system_profiler SPDisplaysDataType -json").read())
        screen_dimensions = sysinfo.get('SPDisplaysDataType')[0].get('spdisplays_ndrvs')[0].get('_spdisplays_resolution')
        res, freq = screen_dimensions.split(" @ ")
        screen_width, screen_height = res.split(" x ")
        return (int(screen_width), int(screen_height))
