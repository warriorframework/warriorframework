import os
from utilities.file_utils import get_abs_path


def get_app_path_from_name(app_name, config_file, current_directory):
    temp = app_name.split(".")
    app_config_file_rel_path = ".." + os.sep
    for el in temp:
        app_config_file_rel_path += el
        app_config_file_rel_path += os.sep

    app_config_file_rel_path += config_file

    app_config_file_path = get_abs_path(app_config_file_rel_path, current_directory)

    return app_config_file_path


def split_str_at_last_index(str, split_at):
    temp = str.split(split_at)

    output = ""
    for j in range(0, len(temp) - 1):
        output += temp[j]
        output += split_at

    output = output.strip(split_at)

    return output


def strip_list_element_of(element, strip_list):
    for el in strip_list:
        element = element.strip(el)

    return element


def strip_list_elements_of(element_list, strip_list):
    for i in range(0, len(element_list)):
        for el in strip_list:
            element_list[i] = element_list[i].strip(el)
    return element_list

def _get_package_name(directory_path):
    """
    This function changes directory path to package

    apps = apps.
    katana/default = katana.default.

    Args:
        directory_path:

    Returns:

    """
    dir_list = directory_path.split(os.sep)
    package_name = ""
    for el in dir_list:
        package_name += el + "."
    return package_name