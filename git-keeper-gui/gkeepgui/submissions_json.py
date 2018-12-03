# Copyright 2018 Thuy Dinh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Provides the SubmissionsPaths class for managing paths previously fetched
to.

This module stores an instance of SubmissionsPaths in the module-level
variable named submissions_paths."""

import json
import os


class SubmissionsPaths:
    """
    Provides functionality for creating JSON file to store fetched paths and
    accessing and modifying its contents.
    """
    def __init__(self):
        """
        Constructor.

        Set the path to the JSON file and call the create_json() method.
        """

        self.json_path = \
            os.path.expanduser('~/.config/git-keeper/submissions_path.json')
        self.create_json()

    def create_json(self):
        """
        Check if a JSON file already exists and create one if not.

        :return: none
        """
        if not self.json_exists():
            with open(self.json_path, 'w'):
                pass

        if os.path.getsize(self.json_path) == 0:
            paths = {}
            with open(self.json_path, 'w') as f:
                json.dump(paths, f)

    def json_exists(self) -> bool:
        """
        Check if a JSON file exists at the set path.

        :return: True if file exists, False otherwise
        """
        return os.path.isfile(self.json_path)

    def get_path(self, assignment: str, class_name: str):
        """
        Get the path of the fetched directory for an assignment.

        :param assignment: name of assignment
        :param class_name: name of class

        :return: Path to fetched directory. None if fetched path is not in the
        file
        """

        # to do: catch exception OSError
        with open(self.json_path, 'r') as f:
            paths = json.load(f)

        if class_name in paths.keys():

            if assignment in paths[class_name].keys():
                path = paths[class_name][assignment]

                return path
            else:
                return None
        else:
            return None

    def set_path(self, assignment: str, class_name: str, path):
        """
        Set submissions path in the json file at
        '~/.config/git-keeper/submissions_path.json'.

        :param assignment: name of the assignment
        :param class_name: name of the class
        :param path: path to set in JSON file

        :return: none
        """

        with open(self.json_path, 'r') as f:
            paths = json.load(f)

        if class_name not in paths.keys():
            paths[class_name] = {}

        paths[class_name][assignment] = path

        with open(self.json_path, 'w') as f:
            json.dump(paths, f)


# module-level instance for accessing fetched assignments
submissions_paths = SubmissionsPaths()
