import os

from utils.json_utils import read_json_data
from wui.core.core_utils.core_utils import get_app_path_from_name
from utils.directory_traversal_utils import get_abs_path, get_parent_directory


class App:

    def __init__(self, json_data):
        self.data = json_data


class Apps:

    def __init__(self):
        self.apps = []
        self.paths = []

    def set_apps(self, data):
        """ call this to build Apps array and make app objects """
        self.get_config_paths(data)
        for url in self.paths:
            app = App(read_json_data(url))
            self.apps.append(app)
        return self.apps

    def get_config_paths(self, data):
        """ sets paths array to paths of json files"""
        for app1 in data['available_apps']:
            for app2 in data['settings_installed_apps']:
                if app1 == app2:
                    self.paths.append(get_app_path_from_name(app1, data['config_file_name'],
                                                             data['base_directory']))
