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

# import standard python libraries
import datetime
import time
import os
import sys
import string
import shutil
import zipfile
import string_Utils
from print_Utils import print_info, print_error, print_warning, print_exception

try:
    if 'linux' in sys.platform:
        mod = 'pexpect'
        import pexpect
except Exception:
    print_info("{0}: {1} module is not installed".format(os.path.abspath(__file__), mod))

def findLastString(filename, searchterm):
    """ Return the last line of a file"""
    fd = open (filename, "r")
    linenum = -1
    for i, line in enumerate (fd, 1):
        if searchterm in line:
            linenum = i
    return linenum

def searchFile(filename, searchterm):
    """ search file for text, return True or False"""
    fd = open (filename, 'r')
    data = fd.read()
    test = data.find(searchterm)
    if test < 0 :
        return False
    return True

def searchaftertext(filename, startterm, searchterm):
    """Start search after a certain text in a file"""
    #print startterm
    #print searchterm
    startline = findLastString (filename, startterm)
    searchtermfound = findLastString (filename, searchterm)
    if searchtermfound > startline:
        return True
    return False

def fileExists(fname):
    """ check if file exists"""
    filestatus = os.path.isfile(fname)
    return filestatus

def dirExists(path):
    """ check if directory exists"""
    dirstatus = os.path.isdir(path)
    return dirstatus

def pathExists(path):
    """ check if path exists , does not care if it is file or directory"""
    pathstatus = os.path.exists(path)
    return pathstatus

def delFile(fname):
    """ check if file exists and delete it"""
    if fileExists(fname):
        filestatus = os.remove(fname)
    return filestatus

def delFolder(path):
    """ check if folder exists and delete it with its content"""
    status = False
    if dirExists(path):
        try:
            shutil.rmtree(path)
            status = True
        except OSError:
            print_error("Cannot remove folder {}".format(path))
    return status

# Return time and date
def getDateTime(time_format=None):
    """Returns the current year-month-date_hour-minute-second """
    if time_format is None:
        timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
    else:
        timestamp = datetime.datetime.now().strftime(time_format)
    return timestamp

def getCurrentFilePath():
    """Will return the file path of file_Utils"""
    return sys.path[0]

def getCurrentFileName():
    """ Will return the file name of file_Utils. Copy into file needed."""
    return os.path.basename (__file__)

def getDirName(filepath):
    """ returns the directory component for the path provided"""
    return os.path.dirname(filepath)


def getXMLDataFile(filename, path):
    """Get the xml Datafile for '.py' testcases """
    path = path.replace ('Testcases','Data')
    filename = filename.replace(".py", "")
    print_info(path + os.sep + filename + os.sep + filename + '.xml')
    return path + os.sep + filename + os.sep + filename + '.xml'

def createDirForPyTc(filename, path, dirname):
    """ method for old directory structure, delete later if not required"""
    path = path.replace ('Testcases',dirname)
    filename = filename.replace(".py", "")
    dirpath = path + os.sep + filename
    if dirExists(dirpath):
        #print_info("Directory already exists for this TC: '%s'" % dirpath)
        return dirpath

    os.makedirs(dirpath)
    #print_info("A new directory created for this TC: '%s'" % dirpath)
    return dirpath

def createDir(path, dirname):
    """Creates a new directory with name = dirname under the provided path, ignores if directory with same name already exists
    Arguments:
        1. path     = (string) full path of an existing directory where a new directory need to be created
        2. dirname  = (string) name of the new directory to be created
    """
    if dirExists(path):
        dirpath = path + os.sep + dirname
        if dirExists(dirpath):

                return dirpath
        try:
                os.makedirs(dirpath)
        except Exception,e:
                print_error(str(e))
        #print_info("A new '%s' directory  created : '%s'" % (dirname, dirpath))
        return dirpath
    else:
        print_warning("Directory does not exist in provided path: {0}".format(path))
        return False

def check_and_create_dir(dirpath):
    """Checks if dir exists in provided path.
    If dir exists returns True
    Elseif dir does not exists, tries to create a directory
        - If dir created successfully, returns True.
        - If dir creation failed returns false
    """
    status = False
    if pathExists(dirpath):
        print_info("Directory exists in provided path '{0}': ".format(dirpath))
        status = True
    elif not pathExists(dirpath):
        try:
            os.makedirs(dirpath)
        except Exception as exception:
            print_warning("Creating directory at '{0}' failed.".format(dirpath))
            print_exception(exception)
            status = False
        else:
            status = True
    return status

def createDir_addtimestamp(path, dirname):
    """Creates a new directory with name = dirname under the provided path, if directory with same name already exists
    adds date+timestamp to the name and creates a new directory with name = dirname+date&timestamp
    Arguments:
        1. path     = (string) full path of an existing directory where a new directory need to be created
        2. dirname  = (string) name of the new directory to be created
    """
    if dirExists(path):
        dirpath = os.path.abspath(path) + os.sep + dirname

        if dirExists(dirpath):
            dirpath = addTimeDate(dirpath)

        try:
            os.makedirs(dirpath)
        except Exception as exception:
            # print_exception(exception)
            print_info("Add date time and try to create directory one more time")
            dirpath = addTimeDate(dirpath)
            os.makedirs(dirpath)

        #print_info("A new '%s' directory  created : '%s'" % (dirname, dirpath))
        return dirpath
    else:
        print_warning("Directory does not exist in provided path: {0}".format(path))
        return False

# to be deleted
#===============================================================================
# Testcases, Logs, Results directory are at the same level
# Creates a new sub-directory under the Results/Logs directory with the dirname provided
#===============================================================================
# def createDirForXmlTc(filename, path, dirname):
#     path = path.replace ('Testcases',dirname)
#     filename = filename.replace(".xml", "")
#     dirpath = path + os.sep + filename
#     if dirExists(dirpath):
#         #print_info("Directory already exists for this TC: '%s'" % dirpath)
#         return dirpath
#
#     os.makedirs(dirpath)
#     #print_info("A new directory created for this TC: '%s'" % dirpath)
#     return dirpath

def getFileName(path):
    """get the file name part from a absolute path"""
    fname = os.path.split(path)[1]
    return fname

# to be deleted
# def getFile(filename, path, dirname):
#     dirpath = createDir (filename, path, dirname)
#     path_split = dirpath.split('/')
#     fname = path_split[-1]
#     extension = getExtension (dirname)
#     print 'dirpath', dirpath
#     fullpath = dirpath + os.sep + fname + '.' + extension
#     if fileExists(fullpath):
#         fullpath = addTimeDate(fullpath)
#     return fullpath

# to be deleted
#===============================================================================
# Create a results/logs file for an xml based test case
# Assumption: directory structure = Result, Logs, Testcases at same level
# #===============================================================================
# def getFileForXmlTc(filename, path, dirname):
#     dirpath = createDirForXmlTc (path, dirname)
#     path_split = dirpath.split('/')
#     fname = path_split[-1]
#     extension = getExtension (dirname)
#     fullpath = dirpath + os.sep + fname + '.' + extension
#     if fileExists(fullpath):
#         fullpath = addTimeDate(fullpath)
#     return fullpath

def get_extension_from_path(path):
    """Takes a filepath as input and returns the extension (extension is everything from the last dot to the end)
    If the input is a directory, the extension returned will be empty

    Arguments:
        1. path = path of the file or directory
    """
    if path:
        extn = os.path.splitext(path)[1]
    else:
        extn = ""
    return extn

def getExtension(dirname):
    """get extension of a path"""
    extension = dirname[:3]
    return extension

def getNameOnly(filename):
    """get file name without extension from a path"""
    nameonly = filename.split('.')[0]
    return nameonly


def get_file_from_remote_server(remote_ip, remote_uname, remote_passwd, src, dest, logfile=None):
    """ use scp to get file from remote server """
    child = pexpect.spawn('scp -r %s@%s:%s %s' % (remote_uname, remote_ip, src, dest ))
    try:
        child.logfile = open(logfile, "a")
    except Exception,e:
        child.logfile = None
    child.expect('assword:*')
    child.sendline(remote_passwd)
    try:
        child.expect(pexpect.EOF)
    except Exception,e:
        print_error("Import error, error : '%s'" % str(e))
        return False
    else:
        return True

def put_file_to_remote_server(remote_ip, remote_uname, remote_passwd, src, dest, logfile=None):
    """ use scp to put file from remote server """
    cmd = 'scp %s %s@%s:%s' % (dest, remote_uname, remote_ip, src)
    print_info("Running cmd: %s" % cmd)
    child = pexpect.spawn(cmd)
    try:
        child.logfile = open(logfile, "a")
    except Exception, e:
        child.logfile = None
    child.expect('assword:*')
    child.sendline(remote_passwd)
    try:
        child.expect(pexpect.EOF)
        out = child.before
        print_info(out)
        if '100%' in out:
            return True
        else:
            return False
    except Exception, e:
        print_error("Import error, error : '%s'" % str(e))
        return False

def incrementFilename(filename, increment):
    """ add count to filename """
    fname = filename.split('.')
    finalname= fname[0]+'_'+increment+'.'+fname[1]
    return finalname


# to be deleted
# def getDataFile(filename, path):# to be deleted once get_testcase_datafile is implemented
#     nameonly = getNameOnly(filename)
#     fullpath = path + os.sep + 'Data' + os.sep + nameonly + '_MainData' + '.xml'
#
#     if not fileExists(fullpath): print_warning('Default Datafile (%s_MainData.xml) not found in default location %s ' % (nameonly, fullpath))
#     return fullpath


def getCustomLogFile(filename, path, custom, ext='.log'):
    """ append filename of log file with custom string """
    nameonly = getNameOnly(filename)

    fullpath = path + os.sep + nameonly + "_" + custom+ ext


    if fileExists(fullpath):
        fullpath = addTimeDate (fullpath)
    return fullpath


def getNewExtension(filename, extension):
    """ Replace the extention of the file"""
    nameonly = os.path.splitext(filename)
    fullpath = nameonly[0] + '.' + extension
    if fileExists(fullpath):
        fullpath = addTimeDate (fullpath)
    return fullpath


def addTimeDate(path):
    """ add time and date to a path (file/dir)"""
    if fileExists(path) or dirExists(path) :
        time.sleep(2)
        ftime       = getDateTime()
        path        = os.path.splitext(path)[0] + "_"+ftime + os.path.splitext(path)[1]

    return path

def deleteLastLine(filename):
    """ delete the last line of a file"""
    lines = open(filename, 'r').readlines()
    del lines[-1]
    open(filename, 'w').writelines(lines)

def deleteFirstLine(filename):
    """ Takes a file name as input and deletes the first line"""
    lines = open(filename, 'r').readlines()
    del lines[0]
    open(filename, 'w').writelines(lines)

def deleteLinesFromFirst(filename):
    """ Takes a file name as input and deletes the first line"""
    deleteFirstLine(filename)


def deletLinesFromLast(filename):
    """ delete the last line of a file"""
    deleteLastLine(filename)

def deleteMatchingFileLines(origfile, newfile, arrValues):
    """ Searches existing file for text and creates new file without the lines containing the text."""
    fin  = open(origfile, 'r')
    fout = open(newfile, 'w')
    for line in fin:
        if any(v in line for v in arrValues):

            print_info("The following was deleted: '%s'" % line)
        else:
            fout.write(line)
    fout.close()


def deleteLinesUntilMatch(filename, match, startfrom='first'):
    """ Opens a file and deletes all the lines until a matching line is encoutered
            
                # filename = location of the file from which lines are to be deleted
                # match = the line to be matched with, this is the entire line given in string format
                # startfrom   = 'first' (default), starts the search begining form the first line of the file
                #                                  and deletes all the lines until matching line is reached
                #             = 'last', starts the search begining form the last line of the file moving upwards
                #                       and deletes all the lines until matching line is reached"""
    lines= open(filename, 'r').readlines()
    linesReverse = list(reversed(lines))

    if startfrom == 'first':
        for i in lines[:]:
            if i != match: lines.remove(i)
            else: break
        resultantList = list(lines)

    if startfrom == 'last':
        for i in linesReverse[:]:
            if i != match: linesReverse.remove(i)
            else: break
        resultantList = list(reversed(linesReverse))
    open(filename, 'w+').writelines(resultantList)


def copyFileContents(srcfile, dstfile):
    """ copy file from src to dst using append method"""
    lines=open(srcfile,'r').readlines()
    open(dstfile, 'a').writelines(lines)

def getLinesBetweenMatchingLines(srcfile, dstfile, start, end, no_of_search=1):
    """ This function opens a file, searches for the start and end strings and writes  the lines in between start and end string into a new file (start, end inluded)
        # srcfile = source file which has the data to be parsed
        # dstfile = destination file to which the captured data is to be written
        # start = starting string to be serached for
        # end = ending string to be searched for
        # no_of_searches = denotes the number of times the file has to be searched for the start and end strings
        #                    supported values = any interger greater than 0
        #                                     = EOF | eof searches the entire file"""
    lines = open(srcfile,'r').readlines()
    #print_info ("lines:%s"% lines)
    i=0
    iteration=0
    resultantList =[]
    if no_of_search == 0:
        print_error ("no of searches should be a non-zero number")
        return False
    while(i<len(lines)):
        #print lines[i]

        printable_only = filter(lambda x:x in string.printable, lines[i])

        if printable_only == start:
            resultantList.append(lines[i])
            i+=1
            while (i<len(lines)):
                printable_only = filter(lambda x:x in string.printable, lines[i])
                if printable_only == end:
                    resultantList.append(lines[i])
                    iteration+=1
                    break
                else:
                    resultantList.append(lines[i])
                    i+=1

        if no_of_search == 'EOF' or no_of_search == 'eof' or iteration < no_of_search: i+=1
        elif no_of_search==iteration: break

    if len(resultantList)==0 :
        print_error("no match found in the file")
    open(dstfile,'w+').writelines(resultantList)


def getSubDirFile(subdir, existing_dir, ext):
    """ Searches for a sub-directory with provided name under a directory. If it does
    # not exist creates a new sub-directory
    # Now under this newly created directory creates file with  sub-directory name and
    # provided extension.If a file with the same name already exists # adds data and
    # time-stamp to the filename .
    # Returns the filename thus created to the calling function
    #
    # Arguments:
    # subdir    = name of the directory and the file to be created under an existing directory
    # dir       = an existing directory
    # ext       = extension for the newly created filename
    #
    # Note: This function does not open the result file, it only creates a name for the file.
    # The file with the created name has to be opened seperately
    """
    path        = createDir_addtimestamp(existing_dir, subdir )
    fullpath    = path + os.sep + subdir + '.' + ext
    if fileExists(fullpath):
        fullpath = addTimeDate(fullpath)
    return fullpath


def create_execution_directory(filepath):
    """Gets a Testcase/Testsuite/Project.xml filepath as input,
        Checks if a directory called Execution exits at the same
        level of Testcase/Testsuite/Project directory
        If it does not exist creates a directory called Execution.
      """
    dirname             = getDirName(filepath)
    execution_folder    = os.sep.join(dirname.split(os.sep)[:-1]) + os.sep + 'Execution'

    if not pathExists(execution_folder):
        os.makedirs(execution_folder)

    dirname = getDateTime()
    execution_dir = createDir_addtimestamp(execution_folder, dirname)
    return execution_dir


def create_zipdir(zipname, path, extn='zip'):
    """zip the path and output to same level"""
    output_filepath = path + os.sep + zipname
    zip_file_path = shutil.make_archive(output_filepath, extn, path)
    return zip_file_path


def getAbsPath(relative_path, start_directory="."):
    """This function is used to manipulate the path according to the
        relative path that is specified

        :Arguments:

            1. @param relative_path: The relative path of directory or file
            2. @param start_directory: The actual dir path where the file must be



          :Returns:

                  1. @return: Returns the abspath with the relative path specified

     """
    value = False
    if relative_path and start_directory:
        relative_path = relative_path.strip()
        try:
            #print relative_path
            os.chdir(start_directory)
            path = os.path.abspath(relative_path)
            value = path
        except Exception, err:
            print_error("{0} file does not exist in provided path".format(relative_path))
            print_error(err)
    return value


def get_parent_dir(path, child):
    """ This function gets the parent directory of any a specified child folder
    from the given path
    """
    if path.rsplit(os.sep)[-1] == child:
        path = os.path.dirname(path)
    else:
        path = os.path.dirname(path)
        path = get_parent_dir(path, child)
    return path


def check_extension_get_absolute_path(relative_path, start_directory, list_extn=[".json", ".xml", ".txt"]):
    """
    This is wrapper function that gets and verifies extention of a file path
    and then returns the absolute path.
    start_directory must be an absolute path
    """
    extension = get_extension_from_path(relative_path)
    if extension in list_extn:
        value = getAbsPath(relative_path, start_directory)
    else:
        value = relative_path
    return value


def get_absolute_path_from_start_directory(relative_path, start_directory, extension=".json"):
    """
    DEPRECATED IN 2.9

    Keyword developer must be aware that relative path can be relative to
    1. testcase file
    2. data file (if path is given in tag= value)
    start_directory must be an absolute path
    """
    print_error("This function is deprecated in 2.9, use check_extension_get_absolute_path or getAbspath instead")
    return check_extension_get_absolute_path(relative_path, start_directory, extension)


def get_absolute_path_of_directory(relative_path_of_dir, start_directory):
    """
    DEPRECATED IN 2.9

    When provided with a start directory and a relative path of a directory, this function
    returns the absolute path. Else returns the relative path

    Keyword developer must be aware that relative path can be relative to
    1. testcase file
    2. data file (if path is given in tag= value)
    start_directory must be an absolute path
    """
    print_error("This function is deprecated in 2.9, use check_extension_get_absolute_path or getAbspath instead")
    return getAbsPath(relative_path_of_dir, start_directory)

# ==============================================================================
# File Operations
# ==============================================================================


def log_result(oper, result):
    """the methods in file_actions class use this to log the result of
    its operation
    """
    resmsg = "completed successfully" if result else "failed"
    msg = "file {} operation {}".format(oper, resmsg)
    if result:
        print_info(msg)
    else:
        print_error(msg)


def open_file(newfile, mode):
    """
    Opens the newfile in the mode specified and returns the filedescriptor
    which would be used by all the other file util operations.
    :Arguments:
        newfile - name of the file to be opened
        mode - mode determines the mode in which the file has to be opened,
        i.e., read, write, append, etc.
            r - Opens a file for reading only. The file pointer is placed at
                the beginning of the file. This is the default mode.
            rb - Opens a file for reading only in binary format. The file
                pointer is placed at the beginning of the file. This is the
                default mode.
            r+ - Opens a file for both reading and writing. The file pointer
                placed at the beginning of the file.
            rb+ - Opens a file for both reading and writing in binary format.
                The file pointer placed at the beginning of the file.
            w - Opens a file for writing only. Overwrites the file if the file
                exists. If the file does not exist, creates a new file
                for writing.
            wb - Opens a file for writing only in binary format. Overwrites
                the file if the file exists. If the file does not exist,
                creates a new file for writing.
            w+ - Opens a file for both writing and reading. Overwrites the
                existing file if the file exists. If the file does not exist,
                creates a new file for reading and writing.
            wb+ - Opens a file for both writing and reading in binary format.
                Overwrites the existing file if the file exists. If the file
                does not exist, creates a new file for reading and writing.
            a - Opens a file for appending. The file pointer is at the end of
                the file if the file exists. That is, the file is in the append
                mode. If the file does not exist, it creates a new file
                for writing.
            ab - Opens a file for appending in binary format. The file pointer
                is at the end of the file if the file exists. That is, the file
                is in the append mode. If the file does not exist, it creates a
                new file for writing.
            a+ - Opens a file for both appending and reading. The file pointer
                is at the end of the file if the file exists. The file opens in
                the append mode. If the file does not exist, it creates a new
                file for reading and writing.
            ab+ - Opens a file for both appending and reading in binary format.
                The file pointer is at the end of the file if the file exists.
                The file opens in the append mode. If the file does not exist,
                it creates a new file for reading and writing.
    :Return:
        fd - file descriptor of the new file opened
    """
    try:
        fd = open(newfile, mode)
        print_info("file {} opened successfully with mode {}".format(newfile,
                                                                     mode))
    except IOError as e:
        print_error("found io exception {} while opening file {} in mode {}".
                    format(str(e), newfile, mode))
        return None
    except Exception as e:
        print_error("found exception {} while opening file {} in mode {}".
                    format(str(e), newfile, mode))
        return None
    return fd


def close(fd):
    """
    Close the file. A closed file cannot be read or written any more.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        True/False - based on the success/failure of the operation
    """
    try:
        name = fd.name
        status = fd.close()
        print_info("file {} closed successfully".format(name))
    except ValueError:
        print_warning("file is already closed...")
        status = True
    except Exception as e:
        print_error("found exception {} while closing {}".format(str(e), fd))
        status = False

    return status


def read(fd, **kwargs):
    """
    Reads at most size bytes from the file (less if the read hits EOF before
    obtaining size bytes).
    :Arguments:
        fd - file descriptor got from open_file
    :Optional:
        size - number of bytes to be read
    :Return:
        the string read from the file, None if not able to read
    """
    try:
        readsize = fd.read(**kwargs)
        print_info("read {} bytes from file {}".format(readsize, fd.name))
    except ValueError:
        print_error("file is already closed...")
        readsize = 0
    except Exception as e:
        print_error("found exception {} while reading {}".format(str(e), fd))
        readsize = 0
    return readsize


def readline(fd, **kwargs):
    """
    Reads one entire line from the file. A trailing newline character is kept
    in the string.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        the line read
    """
    try:
        line = fd.readline(**kwargs)
        print_info("read a line from file "+fd.name)
    except ValueError:
        print_error("file is already closed...")
        line = False
    except Exception as e:
        print_error("found exception {} while reading line in {}".
                    format(str(e), fd))
        line = False
    return line


def readlines(fd, **kwargs):
    """
    Reads until EOF using readline() and return a list containing the lines.
    If the optional sizehint argument is present, instead of reading up to EOF,
    whole lines totalling approximately sizehint bytes (possibly after rounding
    up to an internal buffer size) are read.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        list of lines from the file
    """
    try:
        lines = fd.readlines(**kwargs)
        print_info("read all lines from file "+fd.name)
    except ValueError:
        print_error("file is already closed...")
        lines = False
    except Exception as e:
        print_error("found exception {} while reading lines in {}".
                    format(str(e), fd))
        lines = False
    return lines


def truncate(fd, **kwargs):
    """
    Truncates the file's size. If the optional size argument is present, the
    file is truncated to (at most) that size.
    :Arguments:
        fd - file descriptor got from open_file
    :Optional:
        size - size up to which to truncate
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        fd.truncate(**kwargs)
        print_info("truncated the file "+fd.name)
        status = True
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while truncating {}".
                    format(str(e), fd))
    return status


def write(fd, string):
    """
    Writes a string to the file.
    :Arguments:
        fd - file descriptor got from open_file
        str - string to write
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        fd.write(string)
        print_info("written to file "+fd.name)
        status = True
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while writing {}".format(str(e), fd))
    return status


def writelines(fd, seq):
    """
    Writes a sequence of strings to the file. The sequence can be any
    iterable object producing strings, typically a list of strings.
    :Arguments:
        fd - file descriptor got from open_file
        sequence - sequence of lines to be written
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        fd.writelines(seq)
        print_info("written seq to the file "+fd.name)
        status = True
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while writing {}".format(str(e), fd))
    return status


def get_current_position(fd):
    """
    Returns the file's current position
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        current position of the file, -1 if error occurred
    """
    curpos = -1
    try:
        curpos = fd.tell()
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while getting current position on {}".
                    format(str(e), fd))
    return curpos


def move_to_position(fd, offset, **kwargs):
    """
    Sets the file's current position
    :Arguments:
        fd - file descriptor got from open_file
        offset - number of bytes to be moved
    :Optional:
        whence -
            0 - move offset positions from beginning of file
            1 - move offset positions from current position of file
            2 - move offset positions from end of file
    :Return:
        current position after movement
    """
    curpos = -1
    try:
        if "whence" in kwargs:
            curpos = fd.seek(offset, kwargs["whence"])
        else:
            curpos = fd.seek(offset)
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while moving to position on {}".
                    format(str(e), fd))
    return curpos


def move_to_text(fd, pattern, n=1):
    """
    seek to a text in the file
    :Arguments:
        pattern - the regular expression pattern to search for in the file
        n - seek to the nth occurrence from beginning, default first occurrence
            use negative indices for from the end
    :Return:
        True/False - based success or failure of seeking
    """
    pos = -1
    fd.seek(0, 0)
    data = fd.read()
    try:
        data_pos = string_Utils.seek_next(pattern, data)[n]
        pos = fd.seek(data_pos)
        print_info("moving to {}th pattern {} in file {} successful".
                   format(n, pattern, fd.name))
    except IndexError:
        print_error("pattern {} not found in {}".format(pattern, fd))
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("exception {} occurred while seeking pattern {} in {}".
                    format(str(e), pattern, fd))
    return pos


def get_lines_between(fd, startidx, endidx):
    """
    Get lines between args[0] to args[1]
    :Arguments:
        startidx - line index from which to send
        endidx - line index till to be send
    :Return:
        lines between startidx and endidx
    """
    lines = []
    try:
        fd.seek(0, 0)
        all_lines = fd.readlines()
        lines = all_lines[startidx:endidx]
    except IndexError:
        print_error("file has only {} lines, but expecting {} to {} lines".
                    format(len(all_lines), startidx, endidx))
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while moving to position on {}".
                    format(str(e), fd))
    return lines


def flush(fd):
    """
    Flush the internal buffer, like stdio's fflush. This may be a no-op on some
    file-like objects.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        status = fd.flush()
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while flushing {}".format(str(e), fd))
    return status


def fileno(fd):
    """
    Returns the integer file descriptor that is used by the underlying
    implementation to request I/O operations from the operating system.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        integer file descriptor
    """
    ifd = -1
    try:
        ifd = fd.fileno()
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while getting integer file descriptor "
                    "of {}".format(str(e), fd))
    return ifd

def isatty(fd):
    """
    Returns True if the file is connected to a tty(-like) device, else False.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        True/False - description above
    """
    status = False
    try:
        status = fd.isatty()
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while checking atty of {}".
                    format(str(e), fd))
    return status

def get_next_line(fd):
    """
    Returns the next line from the file each time it is being called.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        next line
    """
    try:
        line = fd.next()
    except ValueError:
        print_error("file is already closed...")
        line = False
    except Exception as e:
        print_error("found exception {} while getting line of {}".
                    format(str(e), fd))
        line = False
    return line

def get_file_name(fd):
    """
    Returns name of the file.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        name of the file, empty string if there was an exception
    """
    fname = ""
    try:
        fname = fd.name
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while getting file name of {}".
                    format(str(e), fd))
    return fname

def get_file_mode(fd):
    """
    Returns access mode with which file was opened.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        mode
    """
    mode = ""
    try:
        mode = fd.mode
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while getting file mode of {}".
                    format(str(e), fd))
    return mode

def is_softspace_required(fd):
    """
    Returns false if space explicitly required with print, true otherwise.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        True/False - description above
    """
    status = False
    try:
        status = fd.softspace
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while getting file mode of {}".
                    format(str(e), fd))
    return status

def is_file_closed(fd):
    """
    Returns true if file is closed, false otherwise.
    :Arguments:
        fd - file descriptor got from open_file
    :Return:
        True/False - description above
    """
    status = False
    try:
        status = fd.closed
    except ValueError:
        print_error("file is already closed...")
    except Exception as e:
        print_error("found exception {} while getting file mode of {}".
                    format(str(e), fd))
    return status

# ==============================================================================
# file meta operations like renaming, deleting etc.,
# ==============================================================================

def copyfileobj(fsrc, fdst):
    """
    Copy the contents of the file-like object fsrc to the file-like object
    fdst.
    :Arguments:
        fsrc - file descriptor of the file to be copied
        fdst - file descriptor of the file on which to be copied
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.copyfileobj(fsrc, fdst)
        status = True
    except Exception as e:
        print_error("copying file {} to file {} raised exception {}".
                    format(fsrc, fdst, str(e)))
    return status


def copyfile(src, dst):
    """
    Copy the contents (no metadata) of the file named src to a file named dst.
    dst must be the complete target file name.
    :Arguments:
        src - file to be copied
        dst - file on which to be copied
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.copyfile(src, dst)
        print_info("src {} copied to dst {} successfully".format(src, dst))
        status = True
    except Exception as e:
        print_error("copying file {} to file {} raised exception {}".
                    format(src, dst, str(e)))
    return status


def copymode(src, dst):
    """
    Copy the permission bits from src to dst. The file contents, owner, and
    group are unaffected. src and dst are path names given as strings.
    :Arguments:
        src - mode of the file to be copied
        dst - file on which mode has to be copied
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.copymode(src, dst)
        print_info("mode of src {} copied to dst {} successfully".
                   format(src, dst))
        status = True
    except Exception as e:
        print_error("copying file mode from {} to file {} raised exception {}".
                    format(src, dst, str(e)))
    return status


def copystat(src, dst):
    """
    Copy the permission bits, last access time, last modification time, and
    flags from src to dst. The file contents, owner, and group are unaffected.
    src and dst are path names given as strings.
    :Arguments:
        src - permission bits of the file to be copied
        dst - file on which permission bits has to be copied
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.copystat(src, dst)
        print_info("metadata of src {} copied to dst {} successfully".
                   format(src, dst))
        status = True
    except Exception as e:
        print_error("copying file stat from {} to file {} raised exception {}".
                    format(src, dst, str(e)))
    return status


def copy(src, dst):
    """
    Copy the file src to the file or directory dst. If dst is a directory, a
    file with the same basename as src is created (or overwritten) in the
    directory specified. Permission bits are copied. src and dst are path
    names given as strings.
    :Arguments:
        src - file to be copied
        dst - file/dir on which to be copied
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.copy(src, dst)
        print_info("src {} copied to dst {} successfully".format(src, dst))
        status = True
    except Exception as e:
        print_error("copying file {} to file {} raised exception {}".
                    format(src, dst, str(e)))
    return status


def copy2(src, dst):
    """
    Similar to shutil.copy(), but metadata (permissions etc., as mentioned in
    copy_stat above) is copied as well  in fact, this is just shutil.copy()
    followed by copystat(). This is similar to the Unix command cp -p.
    :Arguments:
        src - file and metadata to be copied
        dst - file/dir on which to be copied
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.copy2(src, dst)
        print_info("src {} copied to dst {} successfully along with metadata".
                   format(src, dst))
        status = True
    except Exception as e:
        print_error("copying file {} with metadata to file {} raised exception"
                    " {}".format(src, dst, str(e)))
    return status

def move(src, dst):
    """
    Recursively move a file or directory (src) to another location (dst).
    If the destination is an existing directory, then src is moved inside that
    directory. If the destination already exists but is not a directory, it may
    be overwritten depending on os.rename() semantics.If the destination is on
    the current filesystem, then os.rename() is used. Otherwise, src is copied
    (using shutil.copy2()) to dst and then removed.
    :Arguments:
        src - source file to be moved
        dst - target file/directory on which to be moved
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        shutil.move(src, dst)
        print_info("move of src {} to dst {} successful".format(src, dst))
        status = True
    except Exception as e:
        print_error("moving file {} to file {} raised exception {}".
                    format(src, dst, str(e)))
    return status

def remove(nfile):
    """
    removes the file from the filesystem
    :Arguments:
        nfile - filepath to be removed
    :Return:
        True/False - based on the success/failure of the operation
    """
    status = False
    try:
        os.remove(nfile)
        print_info(nfile+" removed from filesystem")
        status = True
    except Exception as e:
        print_error("removing file {} raised exception {}".
                    format(nfile, str(e)))
    return status


def recursive_findfile(file_name, src_dir):
    """
    Finds the file_name in the given directory.
    :Arguments:
        1. file_name(string) - name of the file(with extension) to be searched
        2. src_dir(string) - path of the dir where the file will be searched
    :Return:
        1. output_path(string) - Path of the file(from src_dir) with extension
                                 if the file exists else False
    """

    output_path = False
    if dirExists(src_dir):
        for root, _, files in os.walk(src_dir):
            for f in files:
                if f == file_name:
                    output = os.path.join(root, f)
                    return output
    else:
        print_warning("Directory does not exist in the provided "
                      "path: {}".format(src_dir))

    return output_path


def get_modified_files(src_dir, time_stamp, filetypes=""):
    """
    Finds the modified files(with any one of the filetypes) after a given
    time_stamp in the src_dir. If filetypes argument is empty, all
    modified files will be included.
    :Arguments:
        1. src_dir(string) - path of the directory where the files will be
        2. time_stamp(int/float) - time stamp value. Ex. time.time() will
                                   return current system time in seconds
        3. filetypes(sting) - comma separated file types. Ex. ".py, .xml"
    :Return:
        1. modified_files(list) - list of files modified
    """

    modified_files = []
    filetypes = tuple([ft.strip() for ft in filetypes.split(',') if ft])
    for dirname, _, files in os.walk(src_dir):
        for fname in files:
            full_path = os.path.join(dirname, fname)
            # os.path.getmtime(full_path)
            mtime = os.stat(full_path).st_mtime
            if mtime > time_stamp:
                if filetypes:
                    if full_path.lower().endswith(filetypes):
                        modified_files.append(full_path)
                else:
                    modified_files.append(full_path)

    return modified_files


def convert_to_zip(file_path, compression_type=zipfile.ZIP_DEFLATED):
    """
    Compress the given file based on the compression_type using zipfile module.
    Name of the zipped file will be same as the given file name
    :Arguments:
        1. file_path - File to be zipped
        2. compression_type - ZIP_STORED(no compression) or ZIP_DEFLATED(requires zlib)
    :Returns:
        1. zipped_file - zipped file
    """
    zipped_file = os.path.splitext(file_path)[0] + ".zip"
    zip_object = zipfile.ZipFile(zipped_file, 'w', compression_type)
    zip_object.write(file_path, os.path.basename(file_path))
    zip_object.close()
    return zipped_file
