#!/usr/bin/env python3

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

"""Provides a function for publishing an assignment on the server."""

import sys

from gkeepclient.server_response_poller import ServerResponsePoller,\
    ServerResponseType
from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepclient.client_configuration import config, ClientConfigurationError
from gkeepcore.gkeep_exception import GkeepException


class PublishAssignmentError(GkeepException):
    """Raised if there are any errors publishing the assignment."""
    pass


def publish_assignment(class_name: str, assignment_name: str,
                       response_timeout=20):
    """
    Publish an assignment on the server.

    The server will send emails to all students with clone URLs.

    Raises PublishAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param response_timeout: seconds to wait for server response
    """

    # parse the configuration file
    try:
        config.parse()
    except ClientConfigurationError as e:
        error = 'Configuration error:\n{0}'.format(str(e))
        raise PublishAssignmentError(error)

    # connect to the server
    try:
        server_interface.connect()
    except ServerInterfaceError as e:
        error = 'Error connecting to the server:\n{0}'.format(str(e))
        raise PublishAssignmentError(error)

    # path that the assignment is in on the server
    assignment_path = server_interface.my_assignment_dir_path(class_name,
                                                              assignment_name)

    # check to make sure the assignment path exists
    if not server_interface.is_directory(assignment_path):
        error = ('Assignment {0} does not exist in class {1}'
                 .format(assignment_name, class_name))
        raise PublishAssignmentError(error)

    print('Publishing assignment', assignment_name, 'in class', class_name)

    poller = ServerResponsePoller('PUBLISH', response_timeout)

    payload = '{0} {1}'.format(class_name, assignment_name)

    # log the event
    try:
        server_interface.log_event('PUBLISH', payload)
    except ServerInterfaceError as e:
        error = 'Error logging event: {0}'.format(str(e))
        raise PublishAssignmentError(error)

    try:
        for response in poller.response_generator():
            if response.response_type == ServerResponseType.SUCCESS:
                print('Assignment successfully published')
            elif response.response_type == ServerResponseType.ERROR:
                print('Error publishing response:')
                print(response.message)
            elif response.response_type == ServerResponseType.WARNING:
                print(response.message)
            elif response.response_type == ServerResponseType.TIMEOUT:
                print('Server response timeout. Publish status unknown.')
    except ServerInterfaceError as e:
        error = 'Server communication error: {0}'.format(e)
        raise PublishAssignmentError(error)

if __name__ == '__main__':
    publish_assignment(sys.argv[1], sys.argv[2])