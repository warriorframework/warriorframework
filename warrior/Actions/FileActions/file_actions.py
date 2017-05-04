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

    def write(self, filename, string, index=None):
        """write string in the filename at index location
        :Arguments:
            filename - filename path in which to write the string
            string - the string to be written
            index - the index in the filename at which to write. writes at the
                    end of file if not provided
        :Returns:
            True if successful otherwise False
            output_dictionary
        """
        wdesc = "write string in the filename at index location"
        pNote(wdesc)
        status = True

        fd = file_Utils.open_file(filename, "a")
        if index and file_Utils.move_to_position(fd, index) == -1:
            status = False
        if status:
            status = file_Utils.write(fd, string+"\n")
        file_Utils.close(fd)

        return status

    def findreplace(self, filename, regex, newstring, occurence="",
                    startidx=0, endidx=-1):
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
            output_dictionary
        """
        wdesc = ("find regex/string in the filename and replace it with "
                 "newstring")
        pNote(wdesc)
        startidx = int(startidx)
        endidx = int(endidx)
        lines_to_replace = occurence.split(',') if occurence else []
        rec = re.compile(regex)
        status = True

        fd = file_Utils.open_file(filename, "r")
        lines = file_Utils.readlines(fd)
        newlines = lines[:startidx] if startidx > 0 else []
        for (idx, line) in enumerate(lines[startidx:endidx]):
            if (lines_to_replace and
                    str(startidx+idx+1) not in lines_to_replace):
                newlines.append(line)
            else:
                newlines.append(rec.sub(newstring, line))
        else:
            if endidx != -1 and endidx != len(lines):
                newlines.extend(lines[endidx:])
        file_Utils.close(fd)
        fd = file_Utils.open_file(filename, "w")
        file_Utils.writelines(fd, newlines)
        file_Utils.close(fd)

        return status

    def remove(self, filename):
        """remove the filename from the system
        :Arguments:
            filename - filename path to be removed from system
        :Returns:
            True if successful otherwise False
            output_dictionary
        """
        wdesc = "remove the filename from the system"
        pNote(wdesc)
        status = file_Utils.remove(filename)
        return status

    def rename(self, filename, newname):
        """rename or move filename to newname
        :Arguments:
            filename - filename path to be renamed or moved
            newname - new file name or path to which the file has to be moved
        :Returns:
            True if successful otherwise False
            output_dictionary
        """
        wdesc = "rename or move a file"
        pNote(wdesc)
        status = file_Utils.move(filename, newname)
        return status

    def copy(self, filename, newname):
        """copy filename to newname
        :Arguments:
            filename - filename path to be copied
            newname - new file name or path to which the file has to be copied
        :Returns:
            True if successful otherwise False
            output_dictionary
        """
        wdesc = "copy filename to newname"
        pNote(wdesc)
        status = file_Utils.copy(filename, newname)
        return status

    def copystat(self, filename, newname):
        """copy stats of filename to newname
        :Arguments:
            filename - stats of the filename path to be copied
            newname - new file name or path to which the stats has to be copied
        :Returns:
            True if successful otherwise False
            output_dictionary
        """
        wdesc = "copy stats of filename to newname"
        pNote(wdesc)
        status = file_Utils.copystat(filename, newname)
        return status

    def copy2(self, filename, newname):
        """copy filename to newname along with stats
        :Arguments:
            filename - filename path to be copied along with stats
            newname - new file name or path to which the file and stats has
                    to be moved
        :Returns:
            True if successful otherwise False
            output_dictionary
        """
        wdesc = "copy filename to newname along with stats"
        pNote(wdesc)
        status = file_Utils.copy2(filename, newname)
        return status
