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
import re
from Framework.Utils.testcase_Utils import pNote, pStep
from Framework.Utils import file_Utils
"""This is file_actions module that has all file related keywords """


class FileActions(object):
    """FileActions class which has methods(keywords)
    related to actions used in file KW
    """

    def __init__(self):
        """Constructor for FileActions Class"""
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

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
        pStep('Writing {!r} in {!r}'.format(string, filename))
        file_Utils.close(fd)
        file_Utils.log_result("write", status)

        return status

    def findreplace(self, filename, regex, newstring, occurrence="",
                    int_startidx=0, int_endidx=-1):
        """find regex/string in the filename and replace it with newstring
        :Arguments:
            filename - file path in which to do the operation
            regex - regex or string to be replaced
            newstring - the new string to replace the regex
            occurrence - list of comma separated lines index to find/replace,
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
        lines_to_replace = occurrence.split(',') if occurrence else []
        rec = re.compile(regex)
        status = True
        lines_replaced = 0

        try:
            fd = file_Utils.open_file(filename, "r")
            lines = file_Utils.readlines(fd)
            newlines = lines[:int_startidx] if int_startidx > 0 else []
            if int_endidx < 0:
                int_endidx += len(lines)
            if int_endidx >= len(lines):
                pNote("indices of lines to replace are more than the length of"
                      " the file", "error")
                return False
            for (idx, line) in enumerate(lines[int_startidx:int_endidx+1]):
                if (lines_to_replace and
                        str(int_startidx+idx+1) not in lines_to_replace):
                    newlines.append(line)
                else:
                    newlines.append(rec.sub(newstring, line))
                    lines_replaced += 1
            else:
                if int_endidx+1 != len(lines):
                    newlines.extend(lines[int_endidx:])
            linenos = occurrence if occurrence else "all"
            pStep('replacing {!r} with {!r} in file {!r} on {!r} lines'.format( \
                                        regex, newstring, filename, linenos))
            file_Utils.close(fd)
        except Exception as e:
            exc_msg = "findreplace returned exception {}".format(str(e))
            pNote(exc_msg, "exception")
            status = False
        else:
            if lines_replaced:
                fd = file_Utils.open_file(filename, "w")
                file_Utils.writelines(fd, newlines)
                file_Utils.close(fd)
            else:
                pNote("no lines were replaced as no lines were selected",
                      "warning")
        file_Utils.log_result("findreplace", status)

        return status

    def check_text_occurrence(self, filename, regex, occurrence="",
                              int_startidx=0, int_endidx=-1):
        """find regex/string in the filename
        :Arguments:
            filename - file path in which to do the operation
            regex - regex or string to be checked
            occurrence - list of comma separated lines index to check,
                        empty to check all lines
            startidx - starting line from which to do check, first line
                        if not given
            endidx - ending line to do the check, last line if not given
        :Returns:
            True if successfully checked for all occurrences else False
        """
        wdesc = "find regex/string in the filename in the desired location"
        pNote(wdesc)
        lines_to_check = occurrence.split(',') if occurrence else []
        rec = re.compile(regex)
        status = True

        try:
            fd = file_Utils.open_file(filename, "r")
            lines = file_Utils.readlines(fd)
            if int_endidx < 0:
                int_endidx += len(lines)
            if int_endidx >= len(lines):
                pNote("indices of lines to check are more than the length of "
                      "the file", "error")
                return False
            for (idx, line) in enumerate(lines[int_startidx:int_endidx+1]):
                if not lines_to_check or str(int_startidx+idx+1) in lines_to_check:
                    if rec.search(line) is None:
                        status = status and False
            linenos = occurrence if occurrence else "all"
            pStep('Checking {!r} in file {!r} on {!r} lines'.format(\
                                        regex, filename, linenos))
            file_Utils.close(fd)
        except Exception as e:
            exc_msg = "check_text_occurrence returned exception {}".format(str(e))
            pNote(exc_msg, "exception")
            status = False
        file_Utils.log_result("check_text_occurrence", status)

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
        pStep('removing {!r}'.format(filename))
        file_Utils.log_result("remove", status)
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
        pStep('renaming {!r} to {!r}'.format(filename, newname))
        file_Utils.log_result("rename", status)
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
        pStep('Copying {!r} to {!r}'.format(filename, newname))
        file_Utils.log_result("copy", status)
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
        pStep('Copying stat of {!r} to {!r}'.format(filename, newname))
        file_Utils.log_result("copystat", status)
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
        pStep('Copying contents with stats of {!r} to {!r}'.format(filename, newname))
        file_Utils.log_result("copy2", status)
        return status
