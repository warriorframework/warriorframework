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


if __name__ == "__main__":
    path = get_abs_path("../default", "/home/sanika/django-katana-development-related/warriorframework/katana/core")
    print get_sub_folders(path)