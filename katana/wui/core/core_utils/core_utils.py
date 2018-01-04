import os
from collections import OrderedDict
from utils.directory_traversal_utils import get_abs_path, join_path


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


def validate_config_json(json_data, warrior_dir):
    """
    This function validates the config.json file and returns an ordered dictionary

    :param json_data: original unordered contents of config.json
    :param warrior_dir: path to warrior directory

    :return: Ordered Dictionary containing validated config.json data
    """
    ordered_json = OrderedDict()
    if "engineer" not in json_data:
        ordered_json["engineer"] = ""
    else:
        ordered_json["engineer"] = json_data["engineer"]

    ordered_json["pythonsrcdir"] = warrior_dir[:-1] \
        if "pythonsrcdir" not in json_data or json_data["pythonsrcdir"] == "" \
        else json_data["pythonsrcdir"]

    warrior_dir = ordered_json["pythonsrcdir"]
    ref = OrderedDict([("xmldir", "Testcases"),
                       ('testsuitedir', 'Suites'),
                       ('projdir', 'Projects'),
                       ('idfdir', 'Data'),
                       ('testdata', 'Config_files')])

    for key, value in ref.items():
        if key not in json_data or json_data[key] == "":
            path = get_abs_path(join_path("Warriorspace", value), warrior_dir)
            if path is not None:
                ordered_json[key] = path
            else:
                ordered_json[key] = ""
                print "-- An Error Occurred -- Path to {0} directory could not be located".format(value)
        else:
            ordered_json[key] = json_data[key]

    if "pythonpath" not in json_data:
        ordered_json["pythonpath"] = ""
    else:
        ordered_json["pythonpath"] = json_data["pythonpath"]

    return ordered_json
