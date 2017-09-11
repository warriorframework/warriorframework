import shutil

import errno

from wui.core.core_utils.app_info_class import AppInformation


def readlines_from_file(path, start=None, end=None):
    """
    This function uses the readlines() method to read a file.

    A subsection of the file can be returned by giving the start and end parameters.

    Args:
        path: Absolute path to the file
        start: String after which the file should be read
        end: String at which file reading should be stopped

    Returns:
        data: list of lines read from the file

    """
    data = None
    try:
        with open(path, "r") as f:
            data = f.readlines()
    except IOError:
        print "--Error-- {0} does not exist".format(path)
    else:
        output_list = []

        if start is not None and end is not None:
            flag = False
            for line in data:
                if flag and end is not None and line == end:
                    break
                if flag:
                    output_list.append(line)
                if not flag and line.startswith(start):
                    flag = True
            return output_list

    return data


def copy_dir(src, dest):
    output = True
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            output = False
            print "-- An Error Occurred -- {0}".format(e)
    return output


def write_to_file(path, data):
    output = True
    try:
        with open(path, 'w') as f:
            f.write(data)
    except Exception as e:
        print "-- An Error Occurred -- {0}".format(e)
        output = False
    return output
