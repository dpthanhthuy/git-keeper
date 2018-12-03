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

"""
Provides configuration for the GUI.

Configuration options currently include the background colors for rows of
fetched, unfetched, and unsubmitted student's assignments.

This module contains module-level variable gui_config for accessing the
configuration.

"""


class Config:
    """
    Provide methods for configuring the GUI.
    """

    def __init__(self):
        """
        Constructor

        Set the background colors for rows of submissions.

        Tuple submission_color stores the RGB values of the color.
            submission_color[0]: no submission
            submission_color[1]: fetched
            submission_color[2]: submitted but not fetched

        """
        # red, green, blue
        self.submission_color = ((255, 192, 203), (208, 240, 192),
                                 (240, 248, 255))


# module-level instance for accessing the GUI configurations
gui_config = Config()
