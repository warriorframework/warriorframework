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
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_error, print_debug, print_warning
from Framework.Utils.data_Utils import get_object_from_datarepository


class LogActions(object):
    """class LogActions having keywords that are used for logging within test"""

    def __init__(self):

        """
            Constructor
        """

        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.map_function = {"INFO":print_info, \
                             "DEBUG":print_debug, \
                             "WARN":print_warning, \
                             "ERROR":print_error}

    def log_message(self, message=None, type="INFO", list_message=None, dict_message=None):
        """Keyword to print the given message.
           :Arguments:
                  1. type = message severity level
                            INFO,WARN,DEBUG,ERROR are supported values
                  2. message = message to be printed,
                  3. list_message = list of messages to be printed,
                  4. dict_message = dict with key 'custom message from user'
                     and value 'name in data repo'
                  one of the arguments message, list_message, dict_message is mandatory.

           :Returns:
                  1. True (boolean), this keyword always returns True.
                     Don't want to fail the test based on this keyword.

        """
        wdesc = "keyword to print the given log message"
        Utils.testcase_Utils.pNote(wdesc)
        if not (message or list_message or dict_message):
            print_error("Please specify atleast one message for printing")
            Utils.testcase_Utils.pNote("Please specify atleast one message for printing")
            return True
        if not self.map_function.get(type):
            print_error("type : "+type+" is not supported")
            Utils.testcase_Utils.pNote("type : "+type+" is not supported")
            return True
        if message:
            self.map_function[type](message)
        if list_message:
            _ = [self.map_function[type](message) for message in list_message]
        if dict_message:
            for message, value in dict_message.iteritems():
                value = get_object_from_datarepository(value)
                if value is not None:
                    self.map_function[type](message + ": " + value)
                else:
                    self.map_function[type](message)
        return True
