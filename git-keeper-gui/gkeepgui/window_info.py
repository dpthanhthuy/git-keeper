import json

import os

from gkeepclient import fetch_submissions
from gkeepclient.server_interface import ServerInterfaceError
from gkeepgui.class_information import FacultyClass, Assignment, Submission
from gkeepgui.gui_configuration import gui_config

from gkeepgui.global_info import global_info
from gkeepgui.gui_exception import GuiException
# from gkeepgui.mock_server_interface import ServerInterfaceError


class ClassWindowInfo:
    def __init__(self):

        self.class_list = []
        self.connect()

        self.title = 'Class Window'
        self.current_class = None
        self.current_assignment_table = None
        self.current_submission_table = None
        self.sorting_order = (0, 0)
        self.config = gui_config
        self.build_tables()
        self.change_class(0)
        self.set_description()

    def connect(self):
        if not global_info.is_connected():
            global_info.connect()

        self.info = global_info.info

    def refresh(self):
        global_info.refresh()
        self.info = global_info.info
        self.class_list = []
        current_row = self.current_assignment_table.selected_row
        self.current_assignment_table = AssignmentTable(self.current_class)

        if self.current_submission_table is not None:
            self.current_assignment_table.select_row(current_row)
            self.current_submission_table = SubmissionTable(
                self.current_assignment_table.current_assignment)

    def build_tables(self):
        for a_class in self.info.class_list():
            self.class_list.append(FacultyClass(a_class))

    def change_class(self, index: int):
        self.current_class = self.class_list[index]
        self.current_assignment_table = AssignmentTable(self.current_class)
        self.current_submission_table = None

    def select_assignment(self, row: int):
        self.current_assignment_table.select_row(row)
        assignment = self.current_assignment_table.current_assignment

        if assignment is not None and assignment.is_published:
            self.current_submission_table = SubmissionTable(assignment)

    def select_submission(self, row):
        self.current_submission_table.select_row(row)

    def set_description(self):
        student_count = self.current_class.student_count
        assignment_count = self.current_class.assignment_count
        description = ('Number of students: {} \n' +
                       'Number of assignments: {}').format(student_count,
                                                          assignment_count)
        return description

    def set_submissions_path(self, assignment: str, path):
        with open(gui_config.json_path, 'r') as f:
            paths = json.load(f)

        if self.current_class.name not in paths.keys():
            paths[self.current_class.name] = {}

        paths[self.current_class.name][assignment] = path

        with open(self.config.json_path, 'w') as f:
            json.dump(paths, f)

    def fetch_assignment(self, assignment):

        path = assignment.get_path_from_json()
        fetch_submissions.fetch_submissions(self.current_class.name,
                                            assignment.name, path)
        assignment.set_fetched_path(path)

    def fetch_assignments(self):
        for assignment in self.current_class.get_assignment_list():
            self.fetch_assignment(assignment)

    def fetch(self):

        if self.current_assignment_table.current_assignment is not None:
            self.fetch_assignment(self.current_assignment_table.current_assignment)
            self.refresh()
        else:
            self.fetch_assignments()
            self.refresh()

    def change_submissions_sorting_order(self, col):
        if self.sorting_order[0] == col:
            if self.sorting_order[1] == 0:
                self.sorting_order = (col, 1)
            else:
                self.sorting_order = (col, 0)
        else:
            self.sorting_order = (col, 0)

        self.current_submission_table.set_sorting_order(col, self.sorting_order[1])

    def change_assignments_sorting_order(self, col):
        if self.sorting_order[0] == col:
            if self.sorting_order[1] == 0:
                self.sorting_order = (col, 1)
            else:
                self.sorting_order = (col, 0)
        else:
            self.sorting_order = (col, 0)

        self.current_assignment_table.set_sorting_order(col, self.sorting_order[1])


class StudentWindowInfo:
    def __init__(self, a_class: str, student: str):
        try:
            global_info.refresh()
            self.info = global_info.info

        except ServerInterfaceError:
            pass

        self.title = 'Student Window'
        self.class_name = a_class
        self.username = student

    def set_description(self):
        first_name = self.info.student_first_name(self.class_name,
                                                  self.username)
        last_name = self.info.student_last_name(self.class_name, self.username)
        email = self.info.student_email_address(self.class_name, self.username)
        average_submission_count = \
            self.info.average_student_submission_count(self.class_name,
                                                       self.username)
        description = \
            ('First Name: {} \n' +
             'Last Name: {} \n' +
             'Email: {} \n'
             'Average Submission Count: {}').format(first_name, last_name,
                                                    email,
                                                    average_submission_count)

        return description


class AssignmentWindowInfo:
    def __init__(self, a_class: str, assignment: str):
        try:
            global_info.connect()
            self.info = global_info.info

        except ServerInterfaceError:
            pass

        self.title = 'Assignment Window'
        self.class_name = a_class
        self.assignment = assignment


class Table:
    """
    Table is a base class which stores attributes and methods for the table
    representation of information. This is used to draw tables in the graphical
    or command line interfaces.

    Attributes stored:
        row_count: row count
        col_count: column count
        col_headers: list of all column headers
        rows_content: list of all the rows including their contents
        selected_row: index of the selected row
    """

    def __init__(self):
        """
        Constructor.

        Declare all attributes and set their values to 0 or None. Set the
        sorting order of the table to the default value (descending).
        """
        self.row_count = 0
        self.col_count = 0
        self.col_headers = []
        self.rows_content = []
        self.selected_row = None

    def set_row_count(self, count: int):
        """
        Set row count.

        :param count: number of rows
        :return: none
        """
        self.row_count = count
        for row in range(self.row_count):
            self.rows_content.append([])

    def set_column_count(self, count: int):
        """
        Set column count. Set all column headers to None, all rows' contents to
        None, and all columns' sorting orders to ascending.

        :param count: number of columns
        :return: none
        """
        self.col_count = count

        for col in range(self.col_count):
            self.col_headers.append('')

        for row in self.rows_content:
            for cell in range(self.col_count):
                row.append('')

    def set_column_headers(self, headers: list):
        """
        Set the headers of all columns.

        :param headers: list of all headers in its correct order
        :return: none
        """
        if len(headers) != self.col_count:
            raise GuiException('Number of headers do not match number of '
                               'columns')

        for index in range(self.col_count):
            self.set_column_header(index, headers[index])

    def set_column_header(self, col: int, header: str):
        """
        Set the header of the column with index col.

        :param col: index of the column
        :param header: string of new header
        :return: none
        """
        self.col_headers[col] = header

    def set_rows_content(self, contents: list):
        """
        Set the contents of all rows.

        :return: none
        """
        pass

    def set_row_content(self, row: int, content_list: list):
        """
        Set the content of a row.

        :param row: index of row
        :param content_list: list of each cell's contents in its correct order
        :return: none
        """
        if len(content_list) != self.col_count:
            raise GuiException('Number of cells in this row do not match'
                               'number of columns')
        for col in range(self.col_count):
            self.rows_content[row][col] = content_list[col]

    def select_row(self, row):
        """
        Select a row.

        :param row: index of selected row, None if no row is selected
        :return: none
        """
        self.selected_row = row

    def get_selected_row_content(self) -> list:
        """
        Get the contents of the selected row

        :return: list of each cell's contents in selected row
        """
        return self.rows_content[self.selected_row]

    def _show_table(self):
        pass


class AssignmentTable(Table):
    """
    This Table provides the table representation of all the assignments for
    a class.

    An example visual representation of the table:
        Assignment Name | Students Submitted
        ------------------------------------
          homework_1    |       20
          homework_2    |    Unpublished
    """
    def __init__(self, a_class: FacultyClass):
        """
        Constructor.

        Set all attributes (including rows' contents). Set the type of
        selection to all the cells of a row. Sort the table by the 'Assignment
        Name' column in ascending order.

        :param a_class: parent class of the assignment
        """
        super().__init__()
        self._class = a_class
        self.current_assignment = None
        self.sorting_order = None
        self.set_row_count(a_class.assignment_count)
        self.set_column_count(2)
        self.set_column_headers(['Assignment Name', 'Students Submitted'])
        self.set_sorting_order(0,
                               0)  # first attribute for column, second for order

    def set_rows_content(self, assignments: list):
        """
        Set all the rows' contents to their matching values. Set the 'Students
        Submitted' cell to 'Unpublished' if the assignment has not been
        published.
        :return:
        """
        for row in range(self.row_count):
            assignment = assignments[row]

            if assignment.is_published:
                content = [assignment.name, str(assignment.students_submitted_count)]
            else:
                content = [assignment.name, 'Unpublished']

            self.set_row_content(row, content)

    def select_row(self, row):
        self.selected_row = row

        if row is not None:
            for assignment in self._class.get_assignment_list():
                if assignment.name == self.rows_content[row][0]:
                    self.current_assignment = assignment
                    break
        else:
            self.current_assignment = None

    def update_current_assignment(self):
        if self.current_assignment is not None:

            for assignment in self._class.get_assignment_list():

                if self.current_assignment.name == assignment.name:
                    self.current_assignment = assignment

    def set_sorting_order(self, col, order):
        # order = 0 for descending, = 1 for ascending
        self.sorting_order = (col, order)

        if col == 0:
            if order == 0:
                assignments = sorted(self._class.get_assignment_list(), key=lambda assignment: assignment.name)
            else:
                assignments = sorted(self._class.get_assignment_list(),
                                     key=lambda assignment: assignment.name, reverse=True)

        else:
            if order == 0:
                assignments = sorted(self._class.get_assignment_list(), key=lambda assignment: assignment.students_submitted_count)
            else:
                assignments = sorted(self._class.get_assignment_list(),
                                     key=lambda
                                         assignment: assignment.students_submitted_count, reverse=True)

        self.set_rows_content(assignments)

    def _show_table(self):
        headers = ''

        for header in self.col_headers:
            headers += header + '   '
        print(headers)

        for row in self.rows_content:
            content = ''

            for cell in row:
                content += str(cell) + '        '
            print(content)

        print()


class SubmissionTable(Table):
    """
    This Table provides the table representation of all the submissions for an
    assignment.

    An example visual representation of the table:
          Student   | Last Submission Time | Submission Count
        -----------------------------------------------------
        'alovelace' |    18/2/3 13:37:25   |        2
        'igrant'    |    18/3/3 7:0:1      |        0
    """
    def __init__(self, assignment: Assignment):
        """
        Constructor.

        Set all attributes (including rows' contents). Set the type of
        selection to all the cells of a row. Sort the table by the Student
        column in ascending order.

        :param assignment: parent assignment of the submission
        """
        super().__init__()
        self._assignment = assignment
        self.row_color = {}
        self.sorting_order = None
        self.current_student = None
        self.set_row_count(assignment.parent_class.student_count)
        self.set_column_count(3)
        self.set_column_headers(['Student', 'Last Submission Time',
                                 'Submission Count'])
        self.set_sorting_order(0, 0)

    def set_row_count(self, count: int):
        """
        Set row count.

        :param count: number of rows
        :return: none
        """
        self.row_count = count

        for row in range(self.row_count):
            self.rows_content.append([])

    def set_rows_content(self, submissions):
        """
        Set all the rows' contents to their matching values.
        :return: none
        """
        if not self._assignment.is_published:
            pass
        else:
            for row in range(self.row_count):
                submission = submissions[row]
                content = [submission.student.username,
                           submission.time, str(submission.submission_count)]
                self.set_row_content(row, content)
                self.set_row_color(submission)

    def set_row_color(self, submission: Submission):

        if submission.submission_count == 0:
            self.row_color[submission.student.username] = 0 # red
        elif submission.is_fetched():
            self.row_color[submission.student.username] = 1 # green
        else:
            self.row_color[submission.student.username] = 2 # blue

    def set_sorting_order(self, col, order):
        self.sorting_order = (col, order)

        if col == 0:
            if order == 0:
                submissions = sorted(self._assignment.get_submission_list(), key=lambda submission: submission.student.username)
            else:
                submissions = sorted(self._assignment.get_submission_list(),
                                     key=lambda submission: submission.student.username, reverse=True)
        elif col == 1:
            if order == 0:
                submissions = sorted(self._assignment.get_submission_list(), key=lambda submission: submission.time)
            else:
                submissions = sorted(self._assignment.get_submission_list(),
                                     key=lambda submission: submission.time, reverse=True)
        else:
            if order == 0:
                submissions = sorted(self._assignment.get_submission_list(), key=lambda submission: submission.submission_count)
            else:
                submissions = sorted(self._assignment.get_submission_list(),
                                     key=lambda
                                         submission: submission.submission_count, reverse=True)
        self.set_rows_content(submissions)

    def select_row(self, row):
        self.selected_row = row

        if row is not None:
            for student in self._assignment.parent_class.get_student_list():
                if self.rows_content[row][0] == student.username:
                    self.current_student = student
                    break
        else:
            self.current_student = None

    def _show_table(self):
        headers = ''
        for header in self.col_headers:
            headers += header + '        '

        print(headers)

        for row in self.rows_content:
            content = ''

            for cell in row:
                content += cell + '     '

            print(content)

        print()

        for row in self.row_color.values():
            print(row)
