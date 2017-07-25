import glob
import os


def get_sub_dirs_and_files(path):
    folders = get_sub_folders(path)
    files = get_sub_files(path)
    return {"folders": folders, "files": files}


def get_sub_folders(path):
    folders = []
    temp = glob.glob(path + os.sep + "*")
    for folder in temp:
        if os.path.isdir(folder):
            folders.append(folder)
    folders = [f.replace("\\", '/') for f in folders]
    onlyfolders = map(lambda f: f.rpartition('/')[2], folders)
    return onlyfolders


def get_sub_files(path):
    files = glob.glob(path + os.sep + "*.*")
    files = [f.replace("\\", '/') for f in files]
    onlyfiles = map(lambda f: f.rpartition('/')[2], files)
    return onlyfiles


def get_abs_path(relative_path, base_path):
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


def readlines_from_file(path, start=None, end=None):
    with open(path, "r") as f:
        data = f.readlines()
    output_list = []

    if start is not None and end is not None:
        flag = False
        for line in data:
            if flag and line == end:
                break
            if flag:
                output_list.append(line)
            if not flag and line.startswith(start):
                flag = True
        return output_list

    return data


def get_current_directory(current_directory):
    return os.path.basename(os.path.normpath(current_directory))