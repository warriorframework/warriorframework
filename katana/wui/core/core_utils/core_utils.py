import os
from utils.directory_traversal_utils import get_abs_path


def get_app_path_from_name(app_name, config_file, base_directory):
    """
    This function gets the path to the wf_config_file in the app directory

    Args:
        app_name: Name of the app (eg: default.configuration)
        config_file: Name of the config file
        base_directory: Absolute path to the base directory (/warriorframework/katana/)

    Returns:
        app_config_file_path

    """
    temp = app_name.split(".")
    app_config_file_rel_path = ""
    for el in temp:
        app_config_file_rel_path += el
        app_config_file_rel_path += os.sep

    app_config_file_rel_path += config_file

    app_config_file_path = get_abs_path(app_config_file_rel_path, base_directory)

    return app_config_file_path


def _get_package_name(directory_path, trailing_period=True):
    """
    This function changes directory path to a package format

    apps = apps.
    katana/default = katana.default.

    Args:
        directory_path: directory path that needs to be changed to a package format
        trailing_period: if set to False, the last period at the end of the package would be
                         remove.

    Returns:
        package_name: directory path in a package format

    """
    dir_list = directory_path.split(os.sep)
    package_name = ""
    for el in dir_list:
        package_name += el + "."
    if not trailing_period:
        package_name = package_name[:-1]
    return package_name