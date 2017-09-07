from time import localtime


class JsonInfo:
    """Provides methods for extracting information from the info dictionary."""

    def __init__(self, info_dict: dict):
        """
        Create the object
        :param info_dict: dictionary of info
        """

        self.info_dict = info_dict

    def class_count(self) -> int:
        """
        Get the number of classes.

        :return: number of classes
        """

        return len(self.info_dict)

    def class_list(self) -> list:
        """
        Get the list of classes.

        :return: list of classes
        """

        return list(self.info_dict.keys())

    def student_count(self, class_name: str) -> int:
        """
        Get the number of students in a class.

        :param class_name: name of a class
        :return: number of students in the class
        """

        return len(self.info_dict[class_name]['students'])

    def student_list(self, class_name: str) -> list:
        """
        Get the list of the students in a class.

        :param class_name: name of a class
        :return: list of students in the class
        """

        return list(self.info_dict[class_name]['students'])

    def assignment_count(self, class_name: str) -> int:
        """
        Get the number of assignments for a class.

        :param class_name: name of a class
        :return: number of assignments for the class
        """

        return len(self.info_dict[class_name]['assignments'])

    def assignment_list(self, class_name: str) -> list:
        """
        Get the info dictionary of assignments for a class.

        :param class_name: name of a class
        :return: info dictionary of assignments for a class
        """

        return list(self.info_dict[class_name]['assignments'])

    def is_published(self, class_name: str, assignment: str) -> bool:
        """
        Determine if an assignment is published.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: True if the assignment is published, False otherwise
        """

        return self.info_dict[class_name][assignment]['published']

    def assignment_hash(self, class_name: str, assignment: str) -> str:
        """
        Get the hash of an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: assignment's hash
        """

        return self.info_dict[class_name][assignment]['hash']

    def assignment_path(self, class_name: str, assignment: str) -> str:
        """
        Get the path of an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: assignment's path
        """

        return self.info_dict[class_name][assignment]['path']

    def student_submitted_count(self, class_name: str, assignment: str) -> int:
        """
        Get the number of students who submitted an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: number of students who submitted the assignment
        """

        students_submitted = 0
        for student in self.student_list(class_name):
            if self.submission_count(class_name, assignment, student) != 0:
                students_submitted += 1
        return students_submitted

    def students_submitted_list(self, class_name: str, assignment: str) \
            -> list:
        """
        Get the info dictionary of students who submitted an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: info dictionary of students who submitted an assignment
        """

        students_submitted = []
        for student in self.student_list(class_name):
            if self.submission_count(class_name, assignment, student) != 0:
                students_submitted.append(student)
        return students_submitted

    def email_address(self, class_name: str, username: str) -> str:
        """
        Get the email address of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's email address
        """

        return self.info_dict[class_name]['students'][username][
            'email_address']

    def first_name(self, class_name: str, username: str) -> str:
        """
        Get the first name of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's first name
        """

        return self.info_dict[class_name]['students'][username]['first']

    def home_dir(self, class_name: str, username: str) -> str:
        """
        Get the home directory of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's home directory
        """

        return self.info_dict[class_name]['students'][username]['home_dir']

    def last_name(self, class_name: str, username: str) -> str:
        """
        Get the last name of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's last name
        """

        return self.info_dict[class_name]['students'][username]['last']

    def assignments_by_student_list(self, class_name: str, username: str) \
            -> list:
        """
        Get all the assignments for a student.

        :param class_name: name of a student
        :param username: username of a student
        :return: an info dict of all the assignments for a student
        """

        student_assignments = []
        for an_assignment in self.assignment_list(class_name):
            student_assignment = self.info_dict[class_name]['assignments'][
                an_assignment]['students_repos'][username]
            if student_assignment is not None:
                student_assignments.append(an_assignment)
        return student_assignments

    def assignment_by_student_hash(self, class_name: str, assignment: str,
                                   username: str) -> str:
        """
        Get the hash of a student's assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: the hash of a student's assignment
        """
        return self.info_dict[class_name]['assignments'][assignment][
            'students_repos'][username]['hash']

    def assignment_by_student_path(self, class_name: str, assignment: str,
                                   username: str) -> str:
        """
        Get the path of a student's assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: the path of a student's assignment
        """

        return self.info_dict[class_name]['assignments'][assignment][
            'students_repos'][username]['path']

    def submission_count(self, class_name: str, assignment: str,
                         username: str) -> int:
        """
        Get the submission count of a student for an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: student's submission count for an assignment
        """

        return self.info_dict[class_name]['assignments'][assignment][
            'students_repos'][username]['submission_count']

    def time(self, class_name: str, assignment: str, username: str):
        """
        Get the Unix time a student last submitted an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: the Unix time a student last submitted an assignment.
        """

        return self.info_dict[class_name]['assignments'][assignment][
            'students_repos'][username]['time']

    def time_converted(self, class_name: str, assignment: str, username: str)\
            -> str:
        """
        Get a string of the time a student last submitted an assignment
        (month/day/year hour:min:second)

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: a string of the time a student last submitted an assignment
        """

        time = localtime(self.time(class_name, assignment, username))
        return '{0}/{1}/{2} {3}:{4}:{5}'.\
            format(time.tm_mon, time.tm_mday, time.tm_year,
                   time.tm_hour, time.tm_min, time.tm_sec)

    def get_username_from_name(self, class_name: str, name: str) -> str:
        """
        Get the username of a student from his/her full name.

        :param class_name: name of a class
        :param name: a student's full name in the format
        "last name, first name"
        :return: student's username
        """

        for username in self.student_list(class_name):
            name_form = '{0}, {1}'.format(
                self.last_name(class_name, username),
                self.first_name(class_name, username))
            if name_form == name:
                return username

    def last_first_username(self, class_name: str, username: str) -> str:
        """
        Get the last name, first name, and username of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: a string in the format "last name, first name, username"

        """
        return self.info_dict[class_name]['students'][username][
            'last_first_username']
