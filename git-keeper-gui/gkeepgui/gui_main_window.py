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
Provides the graphical user interface for viewing classes, assignments,
submissions and fetching submissions from students.
"""

import os

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QBrush, QFocusEvent
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QComboBox, QPushButton, QLabel, QTableWidget, QMessageBox, \
    QAbstractItemView, QTableWidgetItem, QToolButton, QFileDialog, \
    QPlainTextEdit

from gkeepclient.client_configuration import config
from gkeepclient.server_interface import ServerInterfaceError
from gkeepcore.gkeep_exception import GkeepException
from gkeepgui.class_information import Assignment
from gkeepgui.fetch_thread import FetchThread
from gkeepgui.gui_configuration import gui_config
from gkeepgui.gui_exception import GuiFileException
from gkeepgui.submissions_json import submissions_paths

from gkeepgui.window_info import ClassWindowInfo, \
    StudentWindowInfo, AssignmentWindowInfo


class MainWindow(QMainWindow):
    """
    Draws the main window and provides three views for class, assignment, and
    student.

    Displays an error message if an exception is raised.
    """

    def __init__(self):
        """
        Constructor.

        Set the geometry of the window. Set the class view as the central
        widget.
        """

        super().__init__()
        self.setGeometry(50, 50, 1000, 1000)
        self.class_window_info = None
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setFocusPolicy(Qt.ClickFocus)
        self.show()
        self.show_class_window()

    def show_class_window(self):
        """
        Set the class view as the central widget. Store ClassWindowInfo as an
        attribute. Display the error message if an exception
        is raised.

        :return: none
        """

        try:
            self.class_window_info = ClassWindowInfo()
        except ServerInterfaceError as e:
            self.show_network_error_message(e)
        except GuiFileException as e:
            self.show_missing_dir_message(e.get_path())
        except GkeepException as e:
            self.show_error_message(e)

        if self.class_window_info is not None:
            self.setCentralWidget(ClassWindow(self.class_window_info))

    def show_student_window(self, class_name: str, username: str):
        """
        Set the student view as the central widget.
        Display the popup error message if a ServerInterfaceError
        is raised.

        :param class_name: name of the class
        :param username: username of the student

        :return: none
        """

        try:
            student_window_info = StudentWindowInfo(class_name, username)
            self.setCentralWidget(StudentWindow(student_window_info))
        except ServerInterfaceError as e:
            self.show_network_error_message(e)
        except GkeepException as e:
            self.show_error_message(e)

    def show_assignment_window(self, class_name: str, assignment: str):
        """
        Set the assignment view as the central widget.
        Display the popup error message if a ServerInterfaceError
        is raised.

        :param class_name: name of the class
        :param assignment: name of the assignment

        :return: none
        """
        try:
            assignment_window_info = AssignmentWindowInfo(class_name,
                                                          assignment)
            self.setCentralWidget(AssignmentWindow(assignment_window_info))
        except ServerInterfaceError as e:
            self.show_network_error_message(e)

    def show_error_message(self, e):
        """
        Pop up a message box displaying the exception raised.

        :param e: exception raised

        :return: none
        """
        message_box = QMessageBox()
        message_box.setText(e)
        message_box.addButton(QMessageBox.Close)
        message_box.show()
        message_box.exec()

    def show_network_error_message(self, e):
        """
        Display the network error message.
        Try to connect if press Retry.
        Quit if press close.

        :param e: ServerInterfaceError exception raised

        :return: none
        """

        message_box = QMessageBox()
        message_box.setText(e)
        retry_button = message_box.addButton('Retry', QMessageBox.AcceptRole)
        close_button = message_box.addButton(QMessageBox.Close)
        message_box.show()
        message_box.exec()

        if message_box.clickedButton() == retry_button:
            try:
                self.class_window_info = ClassWindowInfo()
            except ServerInterfaceError as e:
                message_box.close()
                self.show_network_error_message(e)

        if message_box.clickedButton() == close_button:
            self.hide()

    def show_missing_dir_message(self, path):
        """
        Display the error message for directory specified in the JSON file
        but does not exist.

        :param path: path in JSON file

        :return: none
        """
        message_box = QMessageBox(self)
        message_box.setText('Path from submissions_path.json does not '
                            'exist: {}'.format(path))

        close_button = message_box.addButton(QMessageBox.Close)
        message_box.show()
        message_box.exec()

        if message_box.clickedButton() == close_button:
            self.hide()


class Table(QTableWidget):
    """
    Base class for the table widgets displaying the assignments and
    submissions.

    Provide method for redrawing the previous states of the table widgets when
    the keyboard/mouse focus leaves them.
    """

    def __init__(self):
        """
        Constructor.

        The inWindowClick attribute stores whether the focusOutEvent was
        caused by a click inside the main window.
        """
        super().__init__()
        self.inWindowClick = True

    def focusOutEvent(self, e: QFocusEvent):
        """
        Redraw the tables when they lose focus. If the focusOutEvent was
        caused by a click inside the main window, do nothing.

        :param e: focusOutEvent

        :return: none
        """
        super(Table, self).focusOutEvent(e)

        if not self.inWindowClick:
            self.parentWidget().show_assignments_table()
            self.parentWidget().show_submissions_table()
            self.parentWidget().show_submissions_state()
        else:
            self.inWindowClick = False


class ClassWindow(QWidget):
    """
    Provide the widget and functionality for viewing classes, assignments,
    submissions.
    """

    def __init__(self, window_info: ClassWindowInfo):
        """
        Constructor.

        Set the attributes for the widget and creates layouts, labels, and
        buttons.

        :param window_info: ClassWindowInfo object storing information for
        making the window
        """

        super().__init__()
        self.window_info = window_info

        self.setWindowTitle(window_info.title)

        self.layout = QVBoxLayout()
        self.toolbar_layout = QHBoxLayout()
        self.table_layout = QHBoxLayout()
        self.class_menu = QComboBox(self)

        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.setFixedSize(80, 40)
        self.refresh_button.setCheckable(True)

        self.fetch_button = QPushButton('Fetch Selected')
        self.fetch_button.setFixedSize(120, 40)
        self.fetch_button.setCheckable(True)

        self.fetch_all_button = QPushButton('Fetch All')
        self.fetch_all_button.setFixedSize(100, 40)
        self.fetch_all_button.setCheckable(True)

        self.description_text = QLabel()
        self.assignments_table = Table()
        self.submissions_table = Table()

        self.fetch_message = QPlainTextEdit()
        self.fetch_message.setMinimumWidth(500)
        self.fetch_message.setReadOnly(True)

        # number of fetch threads active
        self.thread_count = 0

        self.toolbar_layout.addWidget(self.class_menu, Qt.AlignLeft)
        self.toolbar_layout.addWidget(self.refresh_button, Qt.AlignRight)
        self.toolbar_layout.addWidget(self.fetch_button, Qt.AlignRight)
        self.toolbar_layout.addWidget(self.fetch_all_button, Qt.AlignRight)
        self.toolbar_layout.insertStretch(1, 10)

        self.layout.addLayout(self.toolbar_layout)
        self.layout.addWidget(self.description_text)
        self.layout.addLayout(self.table_layout)

        self.setLayout(self.layout)

        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()

        self.create_class_menu()
        self.refresh_button.clicked.connect(self.refresh_button_clicked)
        self.fetch_button.clicked.connect(self.fetch_button_clicked)
        self.fetch_all_button.clicked.connect(self.fetch_all_button_clicked)

    @pyqtSlot(bool)
    def refresh_button_clicked(self, checked: bool):
        """
        PyQT slot for the signal emitted when the refresh button is clicked.
        Refresh the window and update information.

        :param checked: True if refresh button is clicked, False otherwise
        :return: none
        """

        if checked:
            self.refresh_button.setChecked(False)
            try:
                self.window_info.refresh()
                self.class_menu.clear()
                self.create_class_menu()
                self.show_assignments_table()
                self.show_submissions_table()
                self.show_submissions_state()
            except ServerInterfaceError as e:
                self.close()
                self.parentWidget().network_error_message(e)
            except GkeepException as e:
                self.display_error_message(e)

    @pyqtSlot(bool)
    def fetch_button_clicked(self, checked: bool):
        """
        PyQT slot for the signal emitted when the fetch button is clicked.
        Grab the path from the json file. If the path is not in there, look
        for it in ClientConfiguration. Otherwise, display the popup file
        dialog for the user to choose which directory to fetch to.

        Fetch the selected assignment, or fetch all if no assignment is
        selected.

        Redraw the window.

        :param checked: True if fetch button is clicked, False otherwise
        :return: none
        """

        if checked:
            self.fetch_button.setChecked(False)
            assignments = \
                self.window_info.current_assignments_table.current_assignment
            self.fetch(assignments)
            self.refresh_button_clicked(True)

    def fetch(self, assignments: list):
        """
        Fetch a list of assignments
        :param assignments: list of Assignment objects

        :return: none
        """
        if assignments is not None and len(assignments) > 0:
            for assignment in assignments:
                if assignment.is_published:
                    try:
                        path = submissions_paths.get_path(
                            assignment.name,
                            self.window_info.current_class.name)
                    except FileNotFoundError:
                        # If the JSON file does not exist, create it
                        try:
                            submissions_paths.create_json()
                        except ValueError as e:
                            self.display_error_message(e)

                        path = None
                    except OSError as e:
                        self.display_error_message(e)

                    # If no path has been specified for the assignment, look in
                    # config file
                    if path is None:
                        try:
                            if config.submissions_path is not None:
                                path = os.path.join(
                                    config.submissions_path,
                                    assignment.parent_class.name)
                        except GkeepException as e:
                            self.display_error_message(e)

                        # If no path has been specified in the config file,
                        # display the file explorer.
                        if path is None:
                            file_dialog = QFileDialog(self, Qt.Popup)
                            path = file_dialog.getExistingDirectory()

                            # If the file is explorer is closed without any
                            # directory chosen, set path to None
                            if path == '':
                                path = None

                    if path is not None:
                        try:
                            # Log the path of the directory to be fetched to
                            # in the JSON file.
                            submissions_paths.set_path(
                                assignment.name,
                                self.window_info.current_class.name, path)
                        except FileNotFoundError:
                            # JSON file has been deleted.
                            try:
                                submissions_paths.create_json()
                            except ValueError as e:
                                self.display_error_message(e)

                            submissions_paths.set_path(
                                assignment.name,
                                self.window_info.current_class.name, path)

                        try:
                            # In the focusOutEvent, the tables are not redrawn
                            self.assignments_table.inWindowClick = True

                            # If there are no active fetch threads, clear the
                            # pop-up fetch message.
                            if self.thread_count == 0:
                                self.fetch_message.clear()

                            self.fetch_message.show()

                            # Show fetch message on top of main window
                            self.fetch_message.raise_()

                            self.print_fetch_message(assignment)

                            # Create the thread to fetch the message
                            fetch_thread = FetchThread(self.window_info)
                            self.thread_count += 1
                            fetch_thread.add_assignment(assignment)
                            # When the thread exits, call the
                            # show_succes_fetch_message() method
                            fetch_thread.finished.connect(
                                self.show_success_fetch_message)
                            fetch_thread.start()
                            # After 100ms, time out to redraw fetch message
                            fetch_thread.wait(100)

                            # Refresh after fetching
                            self.refresh_button_clicked(True)

                        # The directory to be fetched to does not exist
                        except GuiFileException as e:
                            self.no_dir_message(e.get_path(), assignment)
                        except GkeepException as e:
                            self.display_error_message(e)
                        except OSError as e:
                            self.display_error_message(e)

    @pyqtSlot(bool)
    def fetch_all_button_clicked(self, checked: bool):
        """
        PyQT slot that handles the event of clicking the Fetch All button.

        :param checked: whether the button is checked

        :return: none
        """

        if checked:
            self.fetch_all_button.setChecked(False)

            try:
                assignments = \
                    self.window_info.current_class.get_assignment_list()
                self.fetch(assignments)
            except OSError as e:
                self.display_error_message(e)

            self.refresh_button_clicked(True)

    def print_fetch_message(self, assignment: Assignment):
        """
        Display the fetching message.

        :param assignment: Assignment object of the assignment to be fetched

        :return: none
        """
        text = 'Fetching submissions for {} in class {}'.\
            format(assignment.name, assignment.parent_class.name)
        self.fetch_message.appendPlainText(text)

    def show_success_fetch_message(self):
        """
        Display 'Success' after fetching successfully.

        :return: none
        """
        self.fetch_message.appendPlainText('Success!')
        self.thread_count -= 1

    def no_dir_message(self, path, assignment=None):
        """
        Display the popup message for directory not found. Ask to create the
        directory.

        :param path: path of missing directory
        :param assignment: assignment to store in directory

        :return: none
        """
        message_box = QMessageBox(self)
        message_box.setText(path + ' does not exist. Create it now?')
        yes_button = message_box.addButton('Yes', QMessageBox.YesRole)
        no_button = message_box.addButton('No', QMessageBox.NoRole)
        message_box.setDefaultButton(yes_button)
        message_box.exec()

        if message_box.clickedButton() == yes_button:
            os.makedirs(path)

            try:
                if assignment is not None:
                    self.window_info.fetch_assignment(assignment)
                else:
                    self.window_info.fetch_assignments()
            except GkeepException as e:
                self.display_error_message(e)
            except OSError as e:
                self.display_error_message(e)
        else:
            message_box.hide()
            message_box.close()
            self.refresh_button_clicked(True)

    @pyqtSlot()
    def assignments_table_selection_changed(self):
        """
        PyQT slot for the signal emitted when row selection in the assignments
        table changes.

        Show the corresponding submissions table.

        :return: none
        """
        selected_items = self.assignments_table.selectedItems()
        current_rows = []

        for item in selected_items:
            if item.row() not in current_rows:
                current_rows.append(item.row())

        if len(current_rows) > 0:
            try:
                self.window_info.select_assignment(current_rows)
            except GkeepException as e:
                self.display_error_message(e)

        self.show_submissions_table()

    @pyqtSlot()
    def submissions_table_selection_changed(self):
        """
        PyQT slot for the signal emitted when row selection in the submissions
        table changes. This includes the case where no row is selected.

        :return: none
        """
        try:
            self.window_info.select_submission(
                [self.submissions_table.currentRow()])
        except GkeepException as e:
            self.display_error_message(e)

    def create_class_menu(self):
        """
        Create the class menu and select the current class to the first class
        in the list.

        :return: none
        """
        self.class_menu.setFixedSize(100, 30)

        for a_class in self.window_info.class_list:
            self.class_menu.addItem(a_class.name)

        self.class_menu.setCurrentIndex(0)

        self.class_changed(0)
        self.class_menu.currentIndexChanged.connect(self.class_changed)

    @pyqtSlot(int)
    def class_changed(self, index: int):
        """
        PyQT slot for the signal emitted when the current class is changed in
        the class menu.

        Change the content of the assignments and submissions table and the
        description text accordingly.

        :param index: index of the new class

        :return: none
        """
        self.window_info.change_class(index)
        self.set_label()
        self.show_assignments_table()

    def set_label(self):
        """
        Set the description text for the current class.

        :return: none
        """

        self.description_text.setText(self.window_info.set_description())

    def show_assignments_table(self):
        """
        Draw the assignments table for the current class.

        :return: none
        """
        self.assignments_table.destroy()
        self.assignments_table.hide()
        self.table_layout.removeWidget(self.assignments_table)
        self.assignments_table = Table()
        info = self.window_info.current_assignments_table
        self.assignments_table.setRowCount(info.row_count)
        self.assignments_table.setColumnCount(info.col_count)
        index = 0
        current_order = info.sorting_order

        for header in info.col_headers:
            header_item = QTableWidgetItem(header)
            self.assignments_table.setHorizontalHeaderItem(index, header_item)
            index += 1

        # Set the sorting order symbol
        if current_order[1] == 0:
            symbol = '▲'
        else:
            symbol = '▼'

        col_name = '{} {}'.format(
            self.assignments_table.horizontalHeaderItem(
                current_order[0]).text(), symbol)
        self.assignments_table.setHorizontalHeaderItem(current_order[0],
                                                       QTableWidgetItem(
                                                           col_name))
        row_index = 0
        col_index = 0

        # set the contents of the table
        for row in info.rows_content:
            for col in row:
                self.assignments_table.setItem(row_index,
                                               col_index,
                                               QTableWidgetItem(col))
                col_index += 1

            col_index = 0
            row_index += 1

        self.assignments_table.setCornerButtonEnabled(False)
        self.assignments_table.resizeColumnsToContents()

        # set the selection mode to single row only
        self.submissions_table.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.assignments_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)

        # set the flags of each cell so that they are selectable
        for row in range(self.assignments_table.rowCount()):
            for col in range(self.assignments_table.columnCount()):
                self.assignments_table.item(row, col).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        # sort the table when the header is clicked
        self.assignments_table.horizontalHeader().sectionClicked.connect(
            self.sort_assignments_table)

        self.table_layout.addWidget(self.assignments_table)
        self.assignments_table.itemSelectionChanged.connect(
            self.assignments_table_selection_changed)

        # automatically select the first row
        if info.selected_row is not None:
            self.assignments_table.selectRow(info.selected_row[0])
        else:
            self.assignments_table.selectRow(0)

        self.assignments_table.doubleClicked.connect(
            self.assignments_table_double_clicked)

    def show_submissions_table(self):
        """
        Draw the submissions table for the selected assignment.

        :return: none
        """
        self.submissions_table.destroy()
        self.submissions_table.hide()
        self.table_layout.removeWidget(self.submissions_table)
        self.submissions_table = Table()
        info = self.window_info.current_submissions_table
        self.table_layout.addWidget(self.submissions_table)

        if info is not None:  # check if there is a current submissions table
            self.submissions_table.setRowCount(info.row_count)
            self.submissions_table.setColumnCount(info.col_count)
            index = 0

            for header in info.col_headers:
                self.submissions_table.setHorizontalHeaderItem(
                    index, QTableWidgetItem(header))
                index += 1

            current_order = info.sorting_order

            # Set the sorting order symbol
            if current_order[1] == 0:
                symbol = '▲'
            else:
                symbol = '▼'

            col_name = '{} {}'.format(
                self.submissions_table.horizontalHeaderItem(
                    current_order[0]).text(), symbol)
            self.submissions_table.setHorizontalHeaderItem(
                current_order[0], QTableWidgetItem(col_name))

            row_index = 0
            col_index = 0

            # set the contents of the table
            for row in info.rows_content:
                for col in row:
                    self.submissions_table.setItem(row_index, col_index,
                                                   QTableWidgetItem(col))
                    col_index += 1

                col_index = 0
                row_index += 1

            self.submissions_table.setCornerButtonEnabled(False)
            self.submissions_table.resizeColumnsToContents()

            # set the selection mode to single row only
            self.submissions_table.setSelectionMode(
                QAbstractItemView.SingleSelection)
            self.submissions_table.setSelectionBehavior(
                QAbstractItemView.SelectRows)

            # set each cell to be selectable
            for row in range(self.submissions_table.rowCount()):
                for col in range(self.submissions_table.columnCount()):
                    self.submissions_table.item(row, col).setFlags(
                        Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            # sort the table when clicking on the header
            self.submissions_table.horizontalHeader().sectionClicked.connect(
                self.sort_submissions_table)

            self.show_submissions_state()

            self.submissions_table.itemSelectionChanged.connect(
                self.submissions_table_selection_changed)
            self.submissions_table.doubleClicked.connect(
                self.submissions_table_double_clicked)
        else:
            self.submissions_table.hide()

    @pyqtSlot(int)
    def sort_submissions_table(self, col: int):
        """
        PyQT slot for signal emitted when clicking on the submission's table
        header.
        Sort the selected column.

        :param col: index of selected column

        :return: none
        """
        current_order = self.window_info.change_submissions_sorting_order(col)
        self.submissions_table.inWindowClick = True

        self.show_submissions_table()

    @pyqtSlot(int)
    def sort_assignments_table(self, col: int):
        """
        PyQT slot for the signal emitted when clicking on the assignment's
        table header.
        Sort the selected column.

        :param col: index of selected column

        :return: none
        """
        self.window_info.change_assignments_sorting_order(col)
        self.assignments_table.inWindowClick = True
        self.show_assignments_table()

    def show_submissions_state(self):
        """
        Draw the background colors of the submissions table.

        :return: none
        """
        info = self.window_info.current_submissions_table

        if info is not None:

            for row in range(self.submissions_table.rowCount()):
                username = self.submissions_table.item(row, 0).text()
                color = QColor(
                    *gui_config.submission_color[info.row_color[username]])
                brush = QBrush(color)

                for col in range(self.submissions_table.columnCount()):
                    cell = self.submissions_table.item(row, col)
                    cell.setBackground(brush)

    @pyqtSlot()
    def assignments_table_double_clicked(self):
        """
        PyQT slot for signal emitted when double clicking on a row in the
        assignments table.

        :return: none
        """
        self.close()
        class_name = self.window_info.current_class.name
        assignment = \
            self.window_info.current_assignments_table.current_assignment
        self.parentWidget().show_assignment_window(class_name, assignment)

    @pyqtSlot()
    def submissions_table_double_clicked(self):
        """
        PyQT slot for signal emitted when double clicking on a row in the
        submissions table.

        :return: none
        """
        self.close()
        class_name = self.window_info.current_class.name
        username = \
            self.window_info.current_submissions_table.current_student.username
        self.parentWidget().show_student_window(class_name, username)

    def display_error_message(self, e):
        """
        Display the error message for the exception raised.

        :param e: exception raised

        :return: none
        """
        message_box = QMessageBox()
        message_box.setText(e)
        close_button = message_box.addButton(QMessageBox.Close)
        message_box.show()
        message_box.exec()


class StudentWindow(QWidget):
    """
    Provide the widget for viewing information about a student.
    """

    def __init__(self, info: StudentWindowInfo):
        """
        Constructor.
        Create and set the necessary attributes for the widget.

        :param info: a StudentWindowInfo instance that stores information
        about the student window
        """
        super().__init__()

        try:
            self.student_window_info = info
        except ServerInterfaceError:
            pass

        self.setWindowTitle(self.student_window_info.title)
        self.layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        self.back_button = QToolButton()
        self.back_button.setArrowType(Qt.LeftArrow)
        self.back_button.setCheckable(True)
        self.back_button.setFixedSize(30, 30)
        self.buttons_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        self.label = QLabel(self.student_window_info.set_description())
        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.label, alignment=Qt.AlignTop)
        self.setLayout(self.layout)
        self.back_button.clicked.connect(self.back_button_clicked)

    @pyqtSlot(bool)
    def back_button_clicked(self, checked: bool):
        """
        PyQT slot for handling the signal emitted when the back button is
        checked.

        :param checked: True if the back button is checked, False otherwise

        :return: none
        """
        if checked:
            self.close()
            self.parentWidget().show_class_window()


class AssignmentWindow(QWidget):
    """
    Provide the widget for viewing information about an assignment.
    """

    def __init__(self, info: AssignmentWindowInfo):
        """
        Constructor.
        Create and set the necessary attributes for the widget.

        :param info: an AssignmentWindowInfo instance storing information
        about the assignment window
        """
        super().__init__()
        self.assignment_window_info = info
        self.setWindowTitle(self.assignment_window_info.title)
        self.layout = QVBoxLayout()
        self.back_button = QToolButton()
        self.back_button.setArrowType(Qt.LeftArrow)
        self.back_button.setCheckable(True)
        self.back_button.setFixedSize(30, 30)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignTop)
        self.setLayout(self.layout)
        self.back_button.clicked.connect(self.back_button_clicked)

    @pyqtSlot(bool)
    def back_button_clicked(self, checked: bool):
        """
        PyQT slot for handling the signal emitted when the back button is
        checked.

        :param checked: rue if the back button is checked, False otherwise

        :return: none
        """
        if checked:
            self.close()
            self.parentWidget().show_class_window()
