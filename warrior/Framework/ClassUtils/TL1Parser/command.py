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

"""
This module is used to store the format of TL1 commands for parsing.
"""


class Command(object):
    """
    Contains data for a command needed for parsing
    """
    def __init__(self, name='', regex='', args=None, keywords=None):
        """
        Initialize a Command object
        Args:
            name (str, optional): name of the command (RTRV-VERSION, etc)
            regex (str, optional): regex used to split argument data
            args (list, optional): manually provide list of arguments
            keywords (list, optional): manually provide list of keywords
        """
        self.name = name
        self.regex = regex
        self.keyword_pos = 0
        if args is None:
            self.args = []
        else:
            self.args = args
        if keywords is None:
            self.keywords = []
        else:
            self.keywords = keywords

    def __str__(self):
        """
        String representation of Command object
        """
        args = ''
        for key in self.args:
            args += '\t%s\n' % key

        keywords = ''
        for key in self.keywords:
            keywords += '\t%s\n' % key

        return '%s:\nargs:\n%skeywords:\n%s' % (self.name, args, keywords)

    def add_arg(self, value='', optional=False):
        """
        Add an argument to the command
        Args:
            value (str): argument to be added
        """
        self.args.append((value, optional))

    def add_keyword(self, value=''):
        """
        Add a keyword to the command
        Args:
            value (str): keyword to be added
        """
        self.keywords.append(value)
