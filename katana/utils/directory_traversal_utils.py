import glob
import os

from wui.core.core_utils.app_info_class import AppInformation


def get_sub_dirs_and_files(path):
    """
    Gets the direct child sub-files and sub-folders of the given directory

    Args:
        path: Absolute path to the directory

    Returns:

        dict: {"folders": [list of sub-folders], "files": [list of sub-files]}

    """
    folders = get_sub_folders(path)
    files = get_sub_files(path)
    return {"folders": folders, "files": files}


def get_sub_folders(path):
    """
    Gets the direct child sub-folders of the given directory
    Args:
        path: Absolute path to the directory

    Returns:
        onlyfolders: [list of sub-folders]

    """
    folders = []
    temp = glob.glob(path + os.sep + "*")
    for folder in temp:
        if os.path.isdir(folder):
            folders.append(folder)
    folders = [f.replace("\\", '/') for f in folders]
    only_folders = map(lambda f: f.rpartition('/')[2], folders)
    return only_folders


def get_sub_files(path):
    """
    Gets the direct child sub-files of the given directory
    Args:
        path: Absolute path to the directory

    Returns:
        onlyfiles: [list of sub-files]

    """
    files = glob.glob(path + os.sep + "*.*")
    files = [f.replace("\\", '/') for f in files]
    only_files = map(lambda f: f.rpartition('/')[2], files)
    return only_files


def get_abs_path(relative_path, base_path=None):
    """
    Gets the absolute path from the given relative_path and base_path
    Args:
        relative_path: relative path to the file/directory
        base_path: absolute path from where the relative path should be traced. If not provided, the
                   current working directory path will be used.

    Returns:
        path: absolute path derived from relative_path and base_path

    """
    if base_path is None:
        base_path = os.getcwd()

    path = os.path.join(base_path.strip(), relative_path.strip())

    if not os.path.exists(path):
        AppInformation.log_obj.append_log("An Error Occurred: {0} does not exist".format(path))
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
    for i in range(0, level):
        directory_path = os.path.dirname(directory_path)
    return directory_path
