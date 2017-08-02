import json


def read_json_data(file_path):
    """
    This function reads a file contents and converts the string type to JSON (dict)

    Returns:
        data (dict): Contents of the config file

    """
    with open(file_path) as data_file:
        data = json.load(data_file)
    return data