#!/usr/bin/env python

'''
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import sys
import re
"""
This class will trap trap stdout and redirects the message to logfile and stdout
It takes console_logfile and write_to_stdout ( boolean flag) as arguments.
"""


def print_main(message, print_type, con_log, pr_log_name, color_message=None,
               *kwargs):
    """The main print function will be called by other print functions

    :Arguments:

    1. color_message = color of the message (currently non functional)
    2. pr_log_name (str) = Name of the print_log file
    3. con_log (str) = Name of the console_log file
    4. print_type (str) = Type of print message (-I-, -W-, -E-, etc.)
    5. message (object) = message that needs to be printed.

    :Returns:

    """
    if color_message is not None:
        print_string = print_type + " " + str(color_message)
    elif color_message is None:
        print_string = print_type + " " + str(message)
    if len(kwargs) > 0:
        print_string = (print_type + " " + str(message) + str(kwargs))

    print print_string
    pr_log = open(pr_log_name, "a")
    pr_log.write(print_string + "\n")
    pr_log.close()
    try:
        con_log.write(print_string + "\n")
        con_log.flush()
    except ValueError:
        print print_string + "\n"
    return print_string


class RedirectPrint(object):
    """Class that has methods to redirect prints
    from stdout to correct console log files """
    def __init__(self, console_log):
        """Constructor"""
        self.file = console_log
        self.get_file()
        self.write_to_stdout = self.write_to_stdout
        self.stdout = sys.stdout

    def get_file(self):
        """If the console logfile is not None redirect sys.stdout to
        console logfile"""
        if self.file is not None:
            sys.stdout = self

    def write(self, data):
        """
        - Writes data to the sys.stdout
        - Removes the ansii escape chars before writing to file
        :param data:
        """
        self.stdout.write(data)
        ansi_escape = re.compile(r'\x1b[^m]*m')
        data = ansi_escape.sub('', data)
        self.file.write(data)
        self.file.flush()

    def isatty(self):
        """Check if sys.stdout is a tty """
        print self.stdout.isatty()
        return self.stdout.isatty()

    def flush(self):
        """flush logfile """
        return self.stdout.flush()
