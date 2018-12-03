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
Provides an interface for accessing the global information for a faculty's
classes.

This module stores a module-level variable global_info to access the interface
for global information.
"""

import sys

import os

from gkeepclient.client_configuration import config
from gkeepclient.server_interface import server_interface


class GlobalInfo:
    """
    Provide a global interface for accessing a faculty's class information.
    Store a FacultyClassInfo instance as an attribute.

    Call the connect() method to start.
    """

    def __init__(self):
        """
        Constructor.

        Set the path to the client configuration file and call parse() on the
        configuration instance.
        """
        self._connected = False

        if len(sys.argv) < 2:
            path = os.path.expanduser('~/.config/git-keeper/client.cfg')
        else:
            path = os.path.expanduser(sys.argv[1])

        config.set_config_path(path)
        config.parse()

    def refresh(self):
        """
        Update the FacultyClassInfo instance.

        :return: none
        """
        self.info = server_interface.get_info(freshness_threshold=0)

    def connect(self):
        """
        Call connect() on server interface and updates the global interface.

        :return: none
        """
        server_interface.connect()
        self._connected = True
        self.refresh()

    def is_connected(self) -> bool:
        """
        Check if server interface is connected.

        :return: True if connected, False otherwise
        """
        return self._connected


# module-level GlobalInfo instance for accessing global information
global_info = GlobalInfo()