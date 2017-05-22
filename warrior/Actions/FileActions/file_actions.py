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

"""This is file_actions module that has all file related keywords """

import Framework.Utils as Utils
import re
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils import file_Utils


class FileActions(object):
    """FileActions class which has methods(keywords)
    related to actions used in file KW """

    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def _log_result(self, oper, result):
        """UseAsKeyword=No
        the methods in this class can use this to log the result
        of its operation
        """
        resmsg = "completed successfully" if result else "failed"
        print_type = "info" if result else "error"
        msg = "file {} operation {}".format(oper, resmsg)
        pNote(msg, print_type)

    def write(self, filename, string, index=None):
        """write string in the filename at index location
        :Arguments:
            filename - filename path in which to write the string
            string - the string to be written
            index - the index in the filename at which to write. writes at the
                    end of file if not provided
        :Returns:
            True if successful otherwise False
        """
        wdesc = "write string in the filename at index location"
        pNote(wdesc)
        status = True

        fd = file_Utils.open_file(filename, "a")
        if index and file_Utils.move_to_position(fd, index) == -1:
            msg = "Could not move file position to index {}".format(index)
            pNote(msg, "error")
            status = False
        if status:
            status = file_Utils.write(fd, string+"\n")
        file_Utils.close(fd)
        self._log_result("write", status)

        return status

    def findreplace(self, filename, regex, newstring, occurence="",
                    int_startidx=0, int_endidx=-1):
        """find regex/string in the filename and replace it with newstring
        :Arguments:
            filename - file path in which to do the operation
            regex - regex or string to be replaced
            newstring - the new string to replace the regex
            occurence - list of comma separated lines index to find/replace,
                        empty to replace all occurrences
            startidx - starting line from which to do find/replace, first line
                        if not given
            endidx - ending line to do the find/replace, last line if not given
        :Returns:
            True if successfully replaced else False
        """
        wdesc = ("find regex/string in the filename and replace it with "
                 "newstring")
        pNote(wdesc)
        lines_to_replace = occurence.split(',') if occurence else []
        rec = re.compile(regex)
        status = True

        try:
            fd = file_Utils.open_file(filename, "r")
            lines = file_Utils.readlines(fd)
            newlines = lines[:int_startidx] if int_startidx > 0 else []
            for (idx, line) in enumerate(lines[int_startidx:int_endidx]):
                if (lines_to_replace and
                        str(int_startidx+idx+1) not in lines_to_replace):
                    newlines.append(line)
                else:
                    newlines.append(rec.sub(newstring, line))
            else:
                if int_endidx != -1 and int_endidx != len(lines):
                    newlines.extend(lines[int_endidx:])
            file_Utils.close(fd)
        except Exception as e:
            exc_msg = "findreplace returned exception {}".format(str(e))
            pNote(exc_msg, "exception")
            status = False
        else:
            if newlines:
                fd = file_Utils.open_file(filename, "w")
                file_Utils.writelines(fd, newlines)
                file_Utils.close(fd)
            else:
                pNote("no lines were replaced as no lines were selected",
                      "warning")
        self._log_result("findreplace", status)

        return status

    def remove(self, filename):
        """remove the filename from the system
        :Arguments:
            filename - filename path to be removed from system
        :Returns:
            True if successful otherwise False
        """
        wdesc = "remove the filename from the system"
        pNote(wdesc)
        status = file_Utils.remove(filename)
        self._log_result("remove", status)
        return status

    def rename(self, filename, newname):
        """rename or move filename to newname
        :Arguments:
            filename - filename path to be renamed or moved
            newname - new file name or path to which the file has to be moved
        :Returns:
            True if successful otherwise False
        """
        wdesc = "rename or move a file"
        pNote(wdesc)
        status = file_Utils.move(filename, newname)
        self._log_result("rename", status)
        return status

    def copy(self, filename, newname):
        """copy filename to newname
        :Arguments:
            filename - filename path to be copied
            newname - new file name or path to which the file has to be copied
        :Returns:
            True if successful otherwise False
        """
        wdesc = "copy filename to newname"
        pNote(wdesc)
        status = file_Utils.copy(filename, newname)
        self._log_result("copy", status)
        return status

    def copystat(self, filename, newname):
        """copy only stats of filename to newname and not its contents
        :Arguments:
            filename - stats of the filename path to be copied
            newname - new file name or path to which the stats has to be copied
        :Returns:
            True if successful otherwise False
        """
        wdesc = "copy stats of filename to newname"
        pNote(wdesc)
        status = file_Utils.copystat(filename, newname)
        self._log_result("copystat", status)
        return status

    def copy2(self, filename, newname):
        """copy filename to newname along with stats
        :Arguments:
            filename - filename path to be copied along with stats
            newname - new file name or path to which the file and stats has
                    to be moved
        :Returns:
            True if successful otherwise False
        """
        wdesc = "copy filename to newname along with stats"
        pNote(wdesc)
        status = file_Utils.copy2(filename, newname)
        self._log_result("copy2", status)
        return status
