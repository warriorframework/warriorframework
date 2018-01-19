import json
from wui.core.core_utils.app_info_class import AppInformation
from django.template.defaulttags import register
from collections import OrderedDict

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

@register.filter
def get_item(data, key):
    """
        Allow django template to access dict with key with special character
    """
    if type(data) == OrderedDict or type(data) == dict:
        return data.get(key)
    else:
        return ""

@register.filter
def is_dict(data):
    return "true" if isinstance(data, OrderedDict) or isinstance(data, dict) else "false"

@register.filter
def is_list(data):
    return "true" if isinstance(data, list) else "false"

@register.filter
def get_length(data):
    return len(data)
