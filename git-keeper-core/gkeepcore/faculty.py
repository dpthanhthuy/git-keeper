# Copyright 2016 Nathan Sommer and Ben Coleman
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
Provides a class for representing a faculty member.

"""
import csv

from gkeepcore.gkeep_exception import GkeepException


class FacultyError(GkeepException):
    pass


class Faculty:
    """
    Stores a faculty member's attributes.

    Attributes stored::
        last_name
        first_name
        username
        email_address

    """
    def __init__(self, last_name: str, first_name: str, username: str,
                 email_address: str):
        """
        Constructor.

        Simply set the attributes from the parameters.

        """
        self.last_name = last_name
        self.first_name = first_name
        self.username = username
        self.email_address = email_address

    @classmethod
    def from_csv_row(cls, csv_row: list):
        """
        Build a Faculty object from a CSV file row as a list

        :param csv_row: the CSV file row as a list
        :return: a new Faculty object

        """

        if len(csv_row) != 3:
            raise FacultyError('Not a valid faculty row: {0}'
                               .format(str(csv_row)))

        last_name, first_name, email_address = csv_row

        # the faculty's username is their email address username
        try:
            username, domain = email_address.split('@')
        except ValueError:
            raise FacultyError('Not a valid email address: {0}'
                               .format(email_address))

        return cls(last_name, first_name, username, email_address)

    def __repr__(self):
        """
        Build a string representation of a faculty member.

        Format::
            Last, First (username) <username@email.com>

        :return: string representation of the ojbect
        """

        return '{0}, {1} ({2}) <{3}>'.format(self.last_name, self.first_name,
                                             self.username, self.email_address)


def faculty_from_csv_file(csv_path: str):
    """
    Yield a Faculty object for each row in a CSV file.

    Raises FacultyError on a malformed row.

    :param csv_path: path to the CSV file
    :return: iterator over Faculty objects
    """
    try:
        with open(csv_path) as f:
            reader = csv.reader(f)

            for row in reader:
                # skip blank lines
                if len(row) > 0:
                    yield Faculty.from_csv_row(row)

    except (csv.Error, OSError) as e:
        raise FacultyError(e)