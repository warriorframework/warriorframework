import json
from wui.core.core_utils.app_info_class import AppInformation


def read_json_data(file_path):
    """
    This function reads a file contents and converts the string type to JSON (dict)

    Returns:
        data (dict): Contents of the config file

    """
    data = None
    try:
        with open(file_path) as data_file:
            data = json.load(data_file)
    except IOError:
        print "An Error Occurred: {0} file does not exist".format(file_path)
    except ValueError:
        print "An Error Occurred: Incorrect JSON format found in {0}".format(file_path)
    except Exception as e:
        print "An Error Occurred: {0}".format(e)
    return data
