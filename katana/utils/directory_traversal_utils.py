import glob
import os
import re
import errno
import shutil


def get_sub_dirs_and_files(path, abs_path=False):
    """
    Gets the direct child sub-files and sub-folders of the given directory

    Args:
        path: Absolute path to the directory
        abs_path: If set to True, it returns a list of absolute paths to the sub-directories and
                    sub-files instead of directory names only

    Returns:

        dict: {"folders": [list of (if abs_path is True, then path to) sub-folders],
               "files": [list of (if abs_path is True, then path to) sub-files]}

    """
    folders = get_sub_folders(path, abs_path=abs_path)
    files = get_sub_files(path, abs_path=abs_path)
    return {"folders": folders, "files": files}


def get_sub_folders(path, abs_path=False):
    """
    Gets the direct child sub-folders of the given directory
    Args:
        path: Absolute path to the directory
        abs_path: If set to True, it returns a list of absolute paths to the sub-directories
                  instead of directory names only

    Returns:
        only_folders: [list of sub-folders]

    """
    folders = []
    temp = glob.glob(path + os.sep + "*")
    for folder in temp:
        if os.path.isdir(folder):
            folders.append(folder)
    only_folders = [f.replace("\\", '/') for f in folders]
    if not abs_path:
        only_folders = map(lambda f: f.rpartition('/')[2], only_folders)
    return only_folders


def get_sub_files(path, abs_path=False):
    """
    Gets the direct child sub-files of the given directory
    Args:
        path: Absolute path to the directory
        abs_path: If set to True, it returns a list of absolute paths to the sub-files instead of
                  file names only

    Returns:
        only_files: [list of sub-files]

    """
    files = glob.glob(path + os.sep + "*.*")
    only_files = [f.replace("\\", '/') for f in files]
    if not abs_path:
        only_files = map(lambda f: f.rpartition('/')[2], only_files)
    return only_files


def get_abs_path(relative_path, base_path=None, silence_error=False):
    """
    Gets the absolute path from the given relative_path and base_path
    Args:
        relative_path: relative path to the file/directory
        base_path: absolute path from where the relative path should be traced. If not provided, the
                   current working directory path will be used.
        silence_error: Setting this to True would not verify if the directory exists

    Returns:
        path: absolute path derived from relative_path and base_path

    """
    if base_path is None:
        base_path = os.getcwd()

    path = os.path.join(base_path.strip(), relative_path.strip())

    if not silence_error and not os.path.exists(path):
        print "An Error Occurred: {0} does not exist".format(path)
        path = None

    return path


def get_parent_directory(directory_path, level=1):
    """
    Gets the parent directory
    Args:
        directory_path: Absolute path to the file/dir who's parent needs to be returned
        level: Indicates how many levels up to go to find the parent
               eg: default of 1 goes one level up (to the parent directory)
               level=2 would get the grandparent directory

    Returns:

    """
    if directory_path.endswith(os.sep):
        directory_path = directory_path[:-1]
    for i in range(0, level):
        directory_path = os.path.dirname(directory_path)
    return directory_path


def get_paths_of_subfiles(parent_dir, extension=re.compile("\..*")):
    """
    This function returns a list of all the sub-files inside the given directory

    Args:
        parent_dir: Absolute path to the directory
        extension: Regular Expression tha would match a file extension. If not provided, file paths
                   of all extension will be returned

    Returns:
        file_path: Returns a list of paths to sub-files inside the parent_dir

    """
    file_paths = []
    sub_files_and_folders = get_sub_dirs_and_files(parent_dir, abs_path=True)
    for sub_file in sub_files_and_folders["files"]:
        if extension.match(os.path.splitext(sub_file)[1]):
            file_paths.append(sub_file)
    for sub_folder in sub_files_and_folders["folders"]:
        file_paths.extend(get_paths_of_subfiles(sub_folder, extension=extension))
    return file_paths


def get_dir_from_path(path):
    """
    This function is wrapper function for os.path.basename.

    Args:
        path: a file path [Eg: /home/user/Documents/GitHub/warriorframework]

    Returns:
        The base directory name: [Eg: warriorframework]
    """
    return os.path.basename(path)


def join_path(path, *paths):
    """
    This function is wrapper function for os.path.join.

    Args:
        path: a file path
        *paths: paths to be joined to the file path above

    Returns:
        Joined path
    """
    return os.path.join(path, *paths)


def get_relative_path(path, start_directory):
    """
    This is a wrapper function for the os.path.relpath

    Args:
        path: Absolute path to the file/dir to which the relatove path needs to be calculated.
        start_directory: The absolute path to the starting directory

    Returns:
         rel_path: A relative path from start_directory

    """
    if start_directory == "":
        print "-- Error -- start_directory is empty."
        relpath = path
    else:
        try:
            relpath = os.path.relpath(path, start_directory)
        except Exception as e:
            print "-- Error -- {0}".format(e)
            relpath = None
        else:
            if not relpath.startswith(".") and not relpath.startswith(os.sep):
                relpath = os.sep + relpath
    return relpath


def create_dir(path):
    output = path
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            output = False
            print "-- A Error Occurred -- {0}".format(exception)
    return output


def delete_dir(src):
    output = True
    try:
        shutil.rmtree(src)
    except Exception as e:
        print e
        output = False
    return output


def file_or_dir_exists(filepath):
    output = False
    if os.path.exists(filepath):
        output = True
    return output


def get_direct_sub_files(path, abs_path=False, extension=re.compile("\..*")):
    """
    Gets the direct child sub-files of the given directory
    Args:
        path: Absolute path to the directory
        abs_path: If set to True, it returns a list of absolute paths to the sub-files instead of
                  file names only

    Returns:
        only_files: [list of sub-files]

    """
    files = glob.glob(path + os.sep + "*.*")
    only_files = [f.replace("\\", '/') for f in files]
    if not abs_path:
        only_files = map(lambda f: f.rpartition('/')[2], only_files)
    final_files = []
    for sub_file in only_files:
        if extension.match(os.path.splitext(sub_file)[1]):
            final_files.append(sub_file)
    return only_files
