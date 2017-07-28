import glob
import os


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
    onlyfolders = map(lambda f: f.rpartition('/')[2], folders)
    return onlyfolders


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
    onlyfiles = map(lambda f: f.rpartition('/')[2], files)
    return onlyfiles


def get_abs_path(relative_path, base_path):
    """
    Gets the absolute path from the given relative_path and base_path
    Args:
        relative_path: relative path to the file/directory
        base_path: absolute path to the relative_path

    Returns:
        value: absolute path derived from relative_path and base_path

    """
    value = False
    current_directory = os.path.dirname(os.path.realpath(__file__))
    relative_path = relative_path.strip()
    try:
        os.chdir(base_path)
        path = os.path.abspath(relative_path)
        value = path
        os.chdir(current_directory)
    except Exception, err:
        print "{0} file does not exist in provided path".format(relative_path)
        print(err)
    return value


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