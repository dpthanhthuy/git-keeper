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
Base class for GUI exceptions and exception for missing directories.
"""
from gkeepcore.gkeep_exception import GkeepException


class GuiException(GkeepException):
    """
    Base class for GUI exceptions.
    """
    pass


class GuiFileException(GuiException):
    """
    GUI exception for missing directories.
    """

    def set_path(self, path):
        """
        Set the path of the missing directory.

        :param path: path of missing directory

        :return: none
        """

        self.path = path

    def get_path(self):
        """
        Get the path of the missing directory.

        :return: none
        """

        return self.path
