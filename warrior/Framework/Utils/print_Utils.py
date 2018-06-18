"""
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
"""

from WarriorCore.Classes.war_print_class import print_main
import sys
import traceback

"""
Warrior Frameworks print library

!!! Important!!!
DO NOT import any modules from warrior/Framework package that uses
warrior/Framework/Utils/print_Utils.py at module level into this module
as it will lead to cyclic imports.

"""


def print_debug(message, *args):
    """Print a debug message to the terminal """
    print_type = "-D-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    print_main(message, print_type)
    return message


def print_notype(message, *args):
    """Prints with out print type(-I-,-E-),with color cyan in bold TEXT """
    print_type = ""
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    if sys.stdout.isatty():
        color_message = "\033[0;34m" + str(message) + "\033[0m "
    print_main(message, print_type, color_message)
    return message


def print_normal(message, *args):
    """Prints with out print type(-I-,-E-),with color cyan in bold TEXT """
    print_type = ""
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    print_main(message, print_type)
    return message


def print_without_logging(message, *args):
    """Prints without writing to log file"""
    print_type = "-N-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    print_main(message, print_type, logging=False)
    return message


def print_info(message, *args):
    """Print an info message to the terminal """
    print_type = "-I-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    if sys.stdout.isatty():
        msg_upper = message.upper()
        if ":PASS" in msg_upper:
            color_message = message[:msg_upper.index(":PASS") + 1] + "\033[1;32m" + "PASS" + \
                            "\033[0m" + message[msg_upper.index(":PASS") + 5:]

        elif ":RAN" in msg_upper:
            color_message = message[:msg_upper.index(":RAN") + 1] + "\033[1;32m" + "RAN" + \
                            "\033[0m" + message[msg_upper.index(":RAN") + 5:]

        elif ":FAIL" in msg_upper:
            color_message = message[:msg_upper.index(":FAIL") + 1] + "\033[1;31m" + "FAIL" + \
                            "\033[0m" + message[msg_upper.index(":FAIL") + 5:]

        elif ":EXCEPTION" in msg_upper:
            color_message = message[:msg_upper.index(":EXCEPTION") + 1] + "\033[1;31m" + \
                            "EXCEPTION" + "\033[0m" + message[msg_upper.index(":EXCEPTION") + 10:]

        elif ":ERROR" in msg_upper:
            color_message = message[:msg_upper.index(":ERROR") + 1] + "\033[1;31m" + "ERROR" + \
                            "\033[0m" + message[msg_upper.index(":ERROR") + 6:]

        elif ":SKIPPED" in msg_upper:
            color_message = message[:msg_upper.index(":SKIPPED") + 1] + "\033[1;33m" + "SKIPPED" + \
                            "\033[0m" + message[msg_upper.index(":SKIPPED") + 9:]

    print_main(message, print_type, color_message)
    return message


def print_error(message, *args):
    """Prints an error message to the terminal """
    print_type = "-E-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    if sys.stdout.isatty():
        print_type = "\033[1;31m"+ "-E-" + "\033[0m"
        color_message = "\033[1;31m" + str(message) + "\033[0m"
    print_main(message, print_type, color_message)
    return message


def print_exception(exception):
    """Print details of an exception to the console """
    print_info('\n')
    print_error("!!! *** Exception occurred during execution *** !!!")
    print_error("Exception Name: {0}".format(exception.__class__.__name__))
    print_error("Exception trace back: \n \t{0}".format(traceback.format_exc()))
    return traceback.format_exc()


def print_warning(message, *args):
    """Prints a warning message to the terminal """
    print_type = "-W-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    if sys.stdout.isatty():
        print_type = "\033[1;33m"+ "-W-" + "\033[0m"
        color_message = "\033[1;33m" + str(message) + "\033[0m"
    print_main(message, print_type, color_message)
    return message


def print_sub(message, *args):
    """Substitutes the string with *args tuple provided
    User has to provide the place holder for substitution in the message
    as {0}, {1}, {2} ..etc and the corresponding values in the *args.

    Eg: print_sub("My name is {0} {1}, I live in {2}", 'John', 'Doe', 'Texas')
    Output: My Name is John Doe, I live in Texas
    """
    print_type = "-I-"
    message = message.format(*args)
    print_main(message, print_type)
    return message

