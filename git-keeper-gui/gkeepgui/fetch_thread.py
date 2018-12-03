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

"""Provides a thread which fetches assignments and updates the global
interface for accessing class information."""

from PyQt5.QtCore import QThread, QMutex

from gkeepgui.class_information import Assignment
from gkeepgui.window_info import ClassWindowInfo


class FetchThread(QThread):
    """
    Provides a thread which fetches an assignment in a thread-safe manner and
    updates the global interface.

    Usage:

    Use the add_assignment() method to add an Assignment object to fetch its
    submissions.

    Call the start() method to start the thread.
    """
    def __init__(self, window_info: ClassWindowInfo):
        """
        Construct the object.

        :param window_info: an instance of the running global interface
        ClassWindowInfo
        """
        super().__init__()
        self.info = window_info
        self.assignment = None
        self.lock = QMutex()

    def add_assignment(self, assignment: Assignment):
        """
        Add the assignment to be fetched.

        :param assignment: an Assignment object
        :return: none
        """
        self.assignment = assignment

    def run(self):
        """
        Fetch the assignment and updates the global interface.

        :return: none
        """
        if self.assignment is not None:
            self.lock.lock()
            self.info.fetch_assignment(self.assignment)
            self.info.refresh()
            self.lock.unlock()
            self.assignment = None
